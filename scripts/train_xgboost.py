import pandas as pd
import numpy as np
import os
import joblib
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gym_footfall_preprocessed.csv")
    df = pd.read_csv(data_path)
    
    if "date" in df.columns:
        df = df.drop(columns=["date"])
        
    # Add engineered features
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    
    df["exam_weather_interaction"] = (df["exam_intensity"] * df["weather_impact_factor"])
    df["maintenance_capacity_interaction"] = (df["equipment_availability_ratio"] * df["effective_capacity"])
    df["load_exam_interaction"] = (df["academic_load_index"] * (1 - df["exam_intensity"]))
    
    # Needs categorical to be handled for XGBoost if any exist
    # Convert object columns to category if needed.
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category')
    
    train_df = df[df["year"] <= 2024]
    test_df  = df[df["year"] == 2025]
    
    X_train = train_df.drop(columns=["daily_gym_footfall"])
    y_train = train_df["daily_gym_footfall"]
    
    X_test = test_df.drop(columns=["daily_gym_footfall"])
    y_test = test_df["daily_gym_footfall"]
    
    print("Training XGBoost...")
    model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, enable_categorical=True)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    print("XGBoost Performance:")
    print(f"MAE: {mean_absolute_error(y_test, preds):.2f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, preds)):.2f}")
    print(f"R2: {r2_score(y_test, preds):.3f}")
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "xgb_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
