import pandas as pd
import sqlite3
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error

# Import Models
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

# ==========================================
# 1. LOAD ML-READY DATASET
# ==========================================
DB_PATH = "gym_footfall_ml_ready.db"
print(f"Loading preprocessed data from {DB_PATH}...")

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM ml_ready_data", conn)
    conn.close()
except Exception as e:
    print(f"Error loading database: {e}")
    print("Please ensure you are in the correct directory and the .db file exists.")
    exit()

# ==========================================
# 2. TRAIN-TEST SPLIT
# ==========================================
print("Splitting data into training and testing sets...")

X = df.drop(columns=["hourly_gym_footfall"])
y = df["hourly_gym_footfall"]

# 80% for training, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# 3. INITIALIZE MODELS
# ==========================================
models = {
    "Linear_Regression": LinearRegression(),
    "Random_Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
    "CatBoost": CatBoostRegressor(iterations=100, learning_rate=0.1, verbose=0, random_state=42),
    "KNN": KNeighborsRegressor(n_neighbors=5)
}

# Dictionary to store the evaluation results
results = {}

# ==========================================
# 4. TRAIN, EVALUATE, AND SAVE
# ==========================================
print("\n" + "="*50)
print("Starting Model Training Pipeline")
print("="*50)

for model_name, model in models.items():
    print(f"\nTraining {model_name}...")
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions on the test set
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Calculate MAPE and multiply by 100 to display as a percentage
    mape = mean_absolute_percentage_error(y_test, y_pred) * 100
    
    results[model_name] = {"RMSE": rmse, "R2": r2, "MAPE": mape}
    
    print(f"✅ {model_name} trained successfully!")
    print(f"   RMSE: {rmse:.2f} users")
    print(f"   R² Score: {r2:.4f}")
    print(f"   MAPE: {mape:.2f}%")
    
    # Save the model as a .pkl file
    filename = f"{model_name}_model.pkl"
    joblib.dump(model, filename)
    print(f"   💾 Saved as {filename}")

# ==========================================
# 5. SUMMARY REPORT
# ==========================================
print("\n" + "="*60)
print("FINAL LEADERBOARD (Ranked by R² Score)")
print("="*60)

# Sort results by R2 score in descending order
sorted_results = sorted(results.items(), key=lambda item: item[1]['R2'], reverse=True)

# Print header
print(f"{'Rank'.ljust(5)} | {'Model'.ljust(18)} | {'R² Score'.ljust(10)} | {'RMSE'.ljust(10)} | {'MAPE (%)'}")
print("-" * 60)

for rank, (name, metrics) in enumerate(sorted_results, start=1):
    print(f"{str(rank).ljust(5)} | {name.ljust(18)} | {metrics['R2']:.4f}     | {metrics['RMSE']:.2f}       | {metrics['MAPE']:.2f}%")

print("\nAll models have been saved to your directory.")