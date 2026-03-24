import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

# ==========================================
# 1. LOAD DATASET
# ==========================================
# Make sure to use the absolute path!
DB_PATH = "gym_footfall_hourly_dataset_v3.db"
print(f"Loading data from {DB_PATH}...")

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM gym_footfall", conn)
conn.close()

# ==========================================
# 2. FEATURE SELECTION & CLEANING
# ==========================================
# Drop columns that represent target leakage or non-predictive strings
leakage_columns = [
    "exam_intensity", 
    "academic_load_index", 
    "weather_impact_factor", 
    "event_boost_factor", 
    "gym_adoption_ratio", 
    "equipment_availability_ratio", 
    "hourly_effective_capacity", 
    "base_demand"
]

cols_to_drop = [col for col in leakage_columns if col in df.columns] + ["date", "timestamp"]
df_clean = df.drop(columns=cols_to_drop)

# Separate Target (y) and Features (X)
X = df_clean.drop(columns=["hourly_gym_footfall"])
y = df_clean["hourly_gym_footfall"]

# ==========================================
# 3. DEFINE FEATURE TYPES
# ==========================================
categorical_features = [
    "session", 
    "exam_phase", 
    "weather_condition", 
    "maintenance_severity"
]

numerical_features = [
    "hour", 
    "day_of_week", 
    "month", 
    "active_student_population",
    "total_daily_slots"
]

# Keep 'year' as passthrough so train_models.py can safely drop it after doing time-series splits
binary_features = [
    "is_sunday", 
    "is_vacation", 
    "is_gym_open", 
    "interuni_event", 
    "maintenance_flag",
    "year"
]

# ==========================================
# 4. BUILD PREPROCESSING PIPELINE
# ==========================================
print("Building and fitting preprocessing pipeline on entire dataset...")

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), categorical_features),
        ("passthrough", "passthrough", binary_features)
    ]
)

# ==========================================
# 5. TRANSFORM ENTIRE DATASET
# ==========================================
# Fit and transform all data at once
X_processed = preprocessor.fit_transform(X)

# Extract column names after One-Hot Encoding
cat_encoder = preprocessor.named_transformers_["cat"]
cat_feature_names = cat_encoder.get_feature_names_out(categorical_features)
all_feature_names = numerical_features + list(cat_feature_names) + binary_features

# Convert back to DataFrame
df_processed_X = pd.DataFrame(X_processed, columns=all_feature_names)

# Combine Features (X) and Target (y) back into a single dataframe
df_final = pd.concat([df_processed_X, y.reset_index(drop=True)], axis=1)

# ==========================================
# 6. SAVE ARTIFACTS AS SQLITE DB
# ==========================================
print("Saving preprocessed data to SQLite database...")

OUT_DB_PATH = "gym_footfall_ml_ready_v3.db"

# Connect to the new database and save the dataframe as a table named 'ml_ready_data'
conn_out = sqlite3.connect(OUT_DB_PATH)
df_final.to_sql("ml_ready_data", conn_out, if_exists="replace", index=False)
conn_out.close()

# Save the preprocessor pipeline for the UI Dashboard
joblib.dump(preprocessor, "preprocessor_v3.pkl")

print("Preprocessing complete! Data is ML-ready.")
print(f"Files saved: {OUT_DB_PATH}, preprocessor_v3.pkl")