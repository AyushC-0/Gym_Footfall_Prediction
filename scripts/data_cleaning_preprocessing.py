import pandas as pd
import numpy as np

"""
2. Load Dataset
"""

import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_PATH = os.path.join(data_dir, "gym_footfall_dataset.csv")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")
print("Shape:", df.shape)

df.head()

df.info()

df.describe(include="all").T

"""
Date Handling & Sorting
"""

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

"""
Missing Value Handling
"""

df.isnull().sum()

# Safety fallback (should not activate)
df = df.dropna()

"""
Data Type Normalization
Convert Binary Flags to Integer
"""

binary_cols = [
    "is_sunday",
    "is_vacation",
    "is_gym_open",
    "interuni_event",
    "maintenance_flag"
]

df[binary_cols] = df[binary_cols].astype(int)
print("Data preprocessing completed successfully.")

"""
Convert Categorical Columns to category
"""

categorical_cols = [
    "exam_phase",
    "weather_condition",
    "maintenance_severity"
]

for col in categorical_cols:
    df[col] = df[col].astype("category")

print("Data preprocessing completed successfully.")

"""
Target Variable Validation
"""

assert (df["daily_gym_footfall"] >= 0).all(), "Negative footfall detected!"
df["daily_gym_footfall"].describe()

"""
Closed-Day Consistency Check
"""

closed_day_violations = df[
    (df["is_gym_open"] == 0) & (df["daily_gym_footfall"] > 0)
]

print("Closed-day violations:", len(closed_day_violations))


"""
Feature Selection for Modeling
Drop Non-Modeling Columns
"""

df_model = df.drop(columns=[
    "base_demand",    # intermediate synthetic variable
    "raw_demand"      # intermediate synthetic variable
])


"""
Encoding Categorical Features
"""

df_encoded = pd.get_dummies(
    df_model,
    columns=categorical_cols,
    drop_first=True
)

# Convert boolean dummy columns to 0/1
bool_cols = df_encoded.select_dtypes(include=["bool"]).columns
df_encoded[bool_cols] = df_encoded[bool_cols].astype(int)

"""
Final Dataset Check
"""

print("Final modeling shape:", df_encoded.shape)
OUT_PATH = os.path.join(data_dir, "gym_footfall_preprocessed.csv")
df_encoded.to_csv(OUT_PATH, index=False)

