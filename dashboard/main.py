from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

app = FastAPI(title="WeGoGym Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MODEL & PREPROCESSOR LOADING (EXPERIMENT)
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENT_DIR = os.path.join(BASE_DIR, "EXPERIMENT")

def load_experiment_assets():
    """Load the preprocessor and XGBoost model from the EXPERIMENT folder."""
    preprocessor_path = os.path.join(EXPERIMENT_DIR, "preprocessor.pkl")
    xgb_path = os.path.join(EXPERIMENT_DIR, "XGBoost_model.pkl")

    preprocessor, xgb_model = None, None
    try:
        if os.path.exists(preprocessor_path):
            preprocessor = joblib.load(preprocessor_path)
            print(f"✅ Preprocessor loaded from {preprocessor_path}")
        else:
            print(f"⚠️ Preprocessor not found at {preprocessor_path}")
    except Exception as e:
        print(f"Error loading preprocessor: {e}")
    try:
        if os.path.exists(xgb_path):
            xgb_model = joblib.load(xgb_path)
            print(f"✅ XGBoost model loaded from {xgb_path}")
        else:
            print(f"⚠️ XGBoost model not found at {xgb_path}")
    except Exception as e:
        print(f"Error loading XGBoost model: {e}")

    return preprocessor, xgb_model

preprocessor, xgb_model = load_experiment_assets()

# ==========================================
# MAPS & CONSTANTS
# ==========================================
days_map = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}
months_map = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

MORNING_HOURS = [6, 7, 8]
EVENING_HOURS = [17, 18, 19]

HOUR_LABELS = {
    6: "6:00 AM", 7: "7:00 AM", 8: "8:00 AM",
    17: "5:00 PM", 18: "6:00 PM", 19: "7:00 PM"
}

# ==========================================
# REQUEST / RESPONSE SCHEMAS
# ==========================================
class PredictRequest(BaseModel):
    day: str
    month: str
    year: int = 2025
    session: str          # "Morning" or "Evening"
    hour: int             # 6,7,8 or 17,18,19
    is_vacation: bool
    weather: str          # "normal", "heavy_rain", "extreme_heat", "cold_morning"
    exam: str             # "none", "midterm", "endterm"
    maint: str            # "none", "low", "medium", "high"
    pop: int              # active_student_population

class WeekForecastRequest(BaseModel):
    month: str
    week: str
    base_pop: int

# ==========================================
# CORE PREDICTION LOGIC
# ==========================================
def _build_feature_row(day: str, month: str, year: int, session: str, hour: int,
                       is_vacation: bool, weather: str, exam: str, maint: str, pop: int) -> pd.DataFrame:
    """Build a single-row DataFrame matching the preprocessor's expected input schema.
    
    Features expected by the preprocessor (from preprocess_db.py):
      Numerical:   hour, day_of_week, month, year, active_student_population
      Categorical: session, exam_phase, weather_condition, maintenance_severity
      Binary:      is_sunday, is_vacation, is_gym_open, interuni_event, maintenance_flag
    """
    # --- STRICT DATA FORMATTING ---
    # 1. Session must be Title Cased to match training data ("Morning" / "Evening")
    session = session.strip().title()

    # 2. All other categoricals must be strictly lowercased
    exam = exam.strip().lower()
    weather = weather.strip().lower()
    maint = maint.strip().lower()

    # 3. Explicit numeric casting
    pop = int(pop)
    hour = int(hour)
    year = int(year)

    day_idx = days_map.get(day, 0)
    month_idx = months_map.get(month, month) if isinstance(month, str) else month

    # Map frontend weather strings to the dataset's weather_condition values
    weather_map = {
        "normal": "normal",
        "heavy_rain": "heavy_rain",
        "extreme_heat": "extreme_heat",
        "heat": "extreme_heat",
        "cold": "cold_morning",
        "cold_morning": "cold_morning",
    }
    weather_condition = weather_map.get(weather, "normal")

    # Map frontend maint strings to dataset's maintenance_severity values
    maint_map = {
        "none": "none", "low": "low", "medium": "medium", "med": "medium", "high": "high"
    }
    maintenance_severity = maint_map.get(maint, "none")

    # Map frontend exam strings to dataset's exam_phase values
    exam_phase = exam if exam in ("none", "midterm", "endterm") else "none"

    row = {
        # Numerical features (explicitly typed)
        "hour": hour,
        "day_of_week": int(day_idx),
        "month": int(month_idx),
        "year": year,
        "active_student_population": pop,
        # Categorical features (strictly formatted)
        "session": session,
        "exam_phase": exam_phase,
        "weather_condition": weather_condition,
        "maintenance_severity": maintenance_severity,
        # Binary features
        "is_sunday": 1 if day_idx == 6 else 0,
        "is_vacation": int(is_vacation),
        "is_gym_open": 0 if (day_idx == 6 or is_vacation) else 1,
        "interuni_event": 0,
        "maintenance_flag": 0 if maintenance_severity == "none" else 1,
    }
    return pd.DataFrame([row])


def predict_single_hour(model, pre, day, month, year, session, hour,
                        is_vacation, weather, exam, maint, pop) -> int:
    """Run preprocessor + model for a single hour and return clamped int prediction."""
    if pre is None or model is None:
        return 0
    df = _build_feature_row(day, month, year, session, hour, is_vacation, weather, exam, maint, pop)

    # If the gym is closed, footfall is 0
    if df["is_gym_open"].iloc[0] == 0:
        return 0

    try:
        X_transformed = pre.transform(df)
        pred = model.predict(X_transformed)[0]
        return max(0, int(np.round(pred)))
    except Exception as e:
        print(f"Prediction error (hour={hour}): {e}")
        return 0


def _get_status(pred: int):
    """Return (status_label, description) based on refined hourly thresholds."""
    if pred >= 65:
        return "HIGH", "Near-peak hourly capacity. Expect crowded equipment zones."
    elif pred >= 35:
        return "MED", "Moderate hourly traffic. Standard operations sufficient."
    else:
        return "LOW", "Minimal traffic. Ideal time for a distraction-free workout."


# ==========================================
# SMART RECOMMENDATION ENGINE
# ==========================================
def build_recommendation(model, pre, req: PredictRequest):
    """Run the model for ALL hours in the requested session.
    Return the chosen hour's prediction + a recommendation_text if a better slot exists."""
    session_hours = MORNING_HOURS if req.session == "Morning" else EVENING_HOURS

    # Run predictions for every hour in the session
    hour_preds = {}
    for h in session_hours:
        hour_preds[h] = predict_single_hour(
            model, pre,
            req.day, req.month, req.year, req.session, h,
            req.is_vacation, req.weather, req.exam, req.maint, req.pop
        )

    chosen_pred = hour_preds[req.hour]
    chosen_status, _ = _get_status(chosen_pred)

    recommendation_text = ""
    if chosen_status in ("HIGH", "MED"):
        # Find the hour with the lowest footfall in this session
        best_hour = min(hour_preds, key=hour_preds.get)
        best_pred = hour_preds[best_hour]
        if best_hour != req.hour and best_pred < chosen_pred:
            recommendation_text = (
                f"💡 Pro Tip: Avoid the rush! We recommend visiting at "
                f"{HOUR_LABELS[best_hour]} instead, where expected traffic is much lower."
            )

    return chosen_pred, recommendation_text


# ==========================================
# API ENDPOINTS
# ==========================================
@app.post("/api/predict")
def predict_endpoint(req: PredictRequest):
    if not xgb_model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model or preprocessor not loaded")

    prediction, recommendation_text = build_recommendation(xgb_model, preprocessor, req)
    status, description = _get_status(prediction)

    return {
        "prediction": prediction,
        "status": status,
        "description": description,
        "recommendation_text": recommendation_text,
    }


@app.post("/api/daily_forecast")
def daily_forecast_endpoint(req: PredictRequest):
    """Predict footfall for all 6 operational hours in a day based on the shared input features."""
    if not xgb_model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model or preprocessor not loaded")

    forecasts = []
    # All operational hours for WeGoGym
    all_hours = [6, 7, 8, 17, 18, 19]
    
    for h in all_hours:
        # Evaluate context for this specific hour. 
        # Note: 'session' context string technically switches between Morning/Evening based on hour.
        temp_session = "Morning" if h <= 12 else "Evening"
        
        pred_val = predict_single_hour(
            xgb_model, preprocessor,
            day=req.day, month=req.month, year=req.year,
            session=temp_session, hour=h,
            is_vacation=req.is_vacation,
            weather=req.weather, exam=req.exam, maint=req.maint,
            pop=req.pop
        )

        forecasts.append({
            "hour": h,
            "label": HOUR_LABELS.get(h, str(h)),
            "prediction": pred_val
        })

    return {"forecasts": forecasts}


# ==========================================
# STATIC FILES & PAGE ROUTES
# ==========================================
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def home():
    return FileResponse(os.path.join(static_dir, "index.html"))
@app.get("/predict")
def predict_page():
    return FileResponse(os.path.join(static_dir, "predict.html"))
@app.get("/compare")
def compare_page():
    return FileResponse(os.path.join(static_dir, "compare.html"))
@app.get("/overview")
def overview_page():
    return FileResponse(os.path.join(static_dir, "overview.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
