import pandas as pd
import numpy as np
from datetime import datetime

# CONFIG
START_DATE = "2021-01-01"
END_DATE = "2026-01-01"
SEED = 42

np.random.seed(SEED)

# DATE RANGE
dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
df = pd.DataFrame({"date": dates})

# TIME FEATURES
df["day_of_week"] = df["date"].dt.weekday  # Monday = 0
df["is_sunday"] = (df["day_of_week"] == 6).astype(int)
df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year

# GYM OPERATION LOGIC
df["is_vacation"] = df["month"].isin([5, 6]).astype(int)
df["is_gym_open"] = ((df["is_sunday"] == 0) & (df["is_vacation"] == 0)).astype(int)

# CAMPUS POPULATION
df["active_student_population"] = np.random.randint(200, 251, size=len(df))

# EXAM PHASE LOGIC
def get_exam_phase(date):
    month = date.month
    day = date.day

    if month in [1, 4, 7, 10]:
        return "midterm"
    if month in [3, 6, 9, 12]:
        return "endterm"
    return "none"

df["exam_phase"] = df["date"].apply(get_exam_phase)

exam_intensity_map = {
    "none": 1.0,
    "midterm": 0.75,
    "endterm": 0.55
}
df["exam_intensity"] = df["exam_phase"].map(exam_intensity_map)

# ACADEMIC LOAD
df["academic_load_index"] = np.clip(
    np.random.normal(0.5, 0.15, size=len(df)), 0, 1
)

# WEATHER LOGIC
def get_weather(row):
    if row["month"] in [7, 8, 9]:
        return "heavy_rain"
    if row["month"] in [12, 1]:
        return "cold_morning"
    if row["month"] in [4, 5]:
        return "extreme_heat"
    return "normal"

df["weather_condition"] = df.apply(get_weather, axis=1)

weather_factor_map = {
    "normal": 1.0,
    "heavy_rain": 0.80,
    "cold_morning": 0.85,
    "extreme_heat": 0.78
}
df["weather_impact_factor"] = df["weather_condition"].map(weather_factor_map)

# INTER-UNIVERSITY EVENT
df["interuni_event"] = (
    (df["month"] == 1) &
    (df["date"].dt.day.between(15, 21))
).astype(int)

df["event_boost_factor"] = np.where(df["interuni_event"] == 1, 1.15, 1.0)

# GYM ENGAGEMENT TREND
df["gym_adoption_ratio"] = np.clip(
    0.3 + (df["year"] - 2021) * 0.05 + np.random.normal(0, 0.05, len(df)),0.25,0.6)

# MAINTENANCE LOGIC
df["maintenance_flag"] = (np.random.rand(len(df)) < 0.08).astype(int)

def maintenance_severity(flag):
    if flag == 0:
        return "none"
    return np.random.choice(["low", "medium", "high"], p=[0.5, 0.3, 0.2])

df["maintenance_severity"] = df["maintenance_flag"].apply(maintenance_severity)

maintenance_factor_map = {
    "none": 1.0,
    "low": 0.9,
    "medium": 0.8,
    "high": 0.65
}

df["equipment_availability_ratio"] = df["maintenance_severity"].map(
    maintenance_factor_map
)

# CAPACITY
BASE_CAPACITY = 180  # 30 users × 6 hours
df["effective_capacity"] = (
    BASE_CAPACITY * df["equipment_availability_ratio"]
).astype(int)

# DEMAND ESTIMATION
df["base_demand"] = (
    df["active_student_population"] *
    df["gym_adoption_ratio"]
)

df["raw_demand"] = (
    df["base_demand"]
    * df["exam_intensity"]
    * df["weather_impact_factor"]
    * df["event_boost_factor"]
    * (1 - 0.4 * df["academic_load_index"])
)

# NOISE
noise = np.random.normal(
    0,
    df["raw_demand"] * 0.10
)
df["raw_demand"] += noise

# FINAL FOOTFALL
df["daily_gym_footfall"] = np.where(
    df["is_gym_open"] == 0,
    0,
    np.minimum(df["raw_demand"], df["effective_capacity"])
).astype(int)

# CLEANUP
df["daily_gym_footfall"] = df["daily_gym_footfall"].clip(lower=0)

# SAVE DATASET AS CSV
OUTPUT_PATH = "gym_footfall_dataset.csv"

df.to_csv(OUTPUT_PATH, index=False)

print(f"\nDataset saved successfully to: {OUTPUT_PATH}")

# CONSTRAINTS AND LIMITATIONS
# • The dataset is synthetically generated and does not represent real gym attendance data. Results should be interpreted as indicative rather than exact.
# • Data spans from January 2021 to January 2026 at daily granularity. Intra-day session-level variations are not modeled.
# • The gym operates Monday to Saturday and remains closed on Sundays and during the annual vacation period (May–June). Public holidays are approximated.
# • Gym capacity is constrained by operating hours, equipment availability, and maintenance activities. Effective capacity is reduced during maintenance periods.
# • Academic factors such as exams and workload are modeled using rule-based assumptions. Variations across departments or individual schedules are not captured.
# • Weather effects are modeled using seasonal rules rather than real meteorological data and may not reflect daily variability.
# • Student population and gym participation are estimated using simplified engagement ratios and exclude faculty or external users.
# • Only traditional machine learning models are used. Linear Regression serves as a baseline, while Random Forest is the primary model. Neural networks and specialized time-series models are not used.
# • Predictions are scenario-based and intended for planning and analysis, not real-time deployment.
# • During end-term implementation, an SQL database is used for structured storage. Large datasets and trained models are excluded from the Git repository.
# • The system is designed as a proof-of-concept for a small university campus and may require recalibration for other institutions.