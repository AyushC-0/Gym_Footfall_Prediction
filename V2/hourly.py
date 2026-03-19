import pandas as pd
import numpy as np
from datetime import timedelta
import sqlite3

START_DATE = "2021-01-01"
END_DATE = "2026-01-01"
np.random.seed(42)

dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
df = pd.DataFrame({"date": dates})

df["day_of_week"] = df["date"].dt.weekday
df["is_sunday"] = (df["day_of_week"] == 6).astype(int)
df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year
df["is_vacation"] = df["month"].isin([5, 6]).astype(int)
df["is_gym_open"] = ((df["is_sunday"] == 0) & (df["is_vacation"] == 0)).astype(int)

# FIX: Much wider variance so the ML model respects the slider!
df["active_student_population"] = np.random.randint(100, 550, size=len(df))

def get_exam_phase(date):
    if date.month in [1, 4, 7, 10]: return "midterm"
    if date.month in [3, 6, 9, 12]: return "endterm"
    return "none"
df["exam_phase"] = df["date"].apply(get_exam_phase)

def get_weather(row):
    if row["month"] in [7, 8, 9]: return "heavy_rain"
    if row["month"] in [12, 1]: return "cold_morning"
    if row["month"] in [4, 5]: return "extreme_heat"
    return "normal"
df["weather_condition"] = df.apply(get_weather, axis=1)

df["interuni_event"] = ((df["month"] == 1) & (df["date"].dt.day.between(15, 21))).astype(int)
df["gym_adoption_ratio"] = np.clip(0.3 + (df["year"] - 2021) * 0.05 + np.random.normal(0, 0.05, len(df)), 0.25, 0.6)
df["maintenance_flag"] = (np.random.rand(len(df)) < 0.08).astype(int)
df["maintenance_severity"] = df["maintenance_flag"].apply(lambda f: "none" if f==0 else np.random.choice(["low", "medium", "high"], p=[0.5, 0.3, 0.2]))
df["equipment_availability_ratio"] = df["maintenance_severity"].map({"none": 1.0, "low": 0.9, "medium": 0.8, "high": 0.65})

# Explode to hourly
operating_hours = [6, 7, 8, 17, 18, 19]
df_hourly = df.loc[df.index.repeat(len(operating_hours))].copy()
df_hourly['hour'] = operating_hours * len(df)
df_hourly['session'] = np.where(df_hourly['hour'] < 12, 'Morning', 'Evening')
df_hourly['timestamp'] = df_hourly.apply(lambda r: r['date'] + timedelta(hours=r['hour']), axis=1)

# ==========================================
# APPLYING YOUR BEHAVIORAL BIASES
# ==========================================
def calculate_hourly_demand(row):
    # Base calculation
    base = row["active_student_population"] * row["gym_adoption_ratio"]
    
    # BIAS 1: Evening Preference (Lazy default) vs Consistent Morning
    session_mult = 1.0 if row["session"] == "Evening" else 0.45 
    
    # BIAS 2: Heat waves shift people to the morning
    if row["weather_condition"] == "extreme_heat":
        if row["session"] == "Morning": session_mult += 0.4
        if row["session"] == "Evening": session_mult -= 0.3

    # BIAS 3: Exams kill morning gym routines
    if row["exam_phase"] in ["midterm", "endterm"] and row["session"] == "Morning":
        session_mult *= 0.3
        
    # BIAS 4: Specific Hour crowding rules
    hour = row["hour"]
    if hour == 6: hour_mult = 0.2
    elif hour in [7, 8]: hour_mult = 0.4 # 7 and 8 more crowded than 6
    elif hour in [17, 18]: hour_mult = 0.4 # 5 and 6 more crowded than 7 (19)
    elif hour == 19: hour_mult = 0.2
    else: hour_mult = 0.1
    
    # Combine impacts
    weather_mult = {"normal": 1.0, "heavy_rain": 0.7, "cold_morning": 0.8, "extreme_heat": 0.9}[row["weather_condition"]]
    event_mult = 1.2 if row["interuni_event"] == 1 else 1.0
    
    raw = base * session_mult * hour_mult * weather_mult * event_mult
    return raw

df_hourly["hourly_raw_demand"] = df_hourly.apply(calculate_hourly_demand, axis=1)

# Change the base capacity from 30 to a much higher number (e.g., 90)
HOURLY_BASE_CAPACITY = 90

# OPTIONAL: Lower the base adoption ratio slightly so the slider has a wider visible effect
df["gym_adoption_ratio"] = np.clip(0.15 + (df["year"] - 2021) * 0.05 + np.random.normal(0, 0.05, len(df)), 0.1, 0.4)
df_hourly["hourly_effective_capacity"] = (HOURLY_BASE_CAPACITY * df_hourly["equipment_availability_ratio"]).astype(int)
df_hourly["hourly_gym_footfall"] = np.where(
    df_hourly["is_gym_open"] == 0, 0,
    np.minimum(df_hourly["hourly_raw_demand"], df_hourly["hourly_effective_capacity"])
).astype(int)
df_hourly["hourly_gym_footfall"] = df_hourly["hourly_gym_footfall"].clip(lower=0)

cols_to_keep = ['timestamp', 'date', 'session', 'hour', 'day_of_week', 'is_sunday', 'month', 'year', 'is_vacation', 
                'is_gym_open', 'active_student_population', 'exam_phase', 'weather_condition', 'interuni_event', 
                'maintenance_flag', 'maintenance_severity', 'hourly_gym_footfall']
df_hourly = df_hourly[cols_to_keep]

conn = sqlite3.connect("gym_footfall_hourly_dataset.db")
df_hourly.to_sql("gym_footfall", conn, if_exists="replace", index=False)
conn.close()
print("Dataset generated with new biases!")