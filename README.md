# University Gym Footfall Prediction System

## Project Overview
This project focuses on predicting daily gym footfall for a university campus using machine learning. Gym usage is influenced by multiple factors such as academic schedules, seasonal patterns, weather conditions, student population dynamics, and equipment maintenance. The objective is to build a data-driven system that analyzes historical patterns and provides accurate, explainable predictions to support operational planning.

The project is developed in a step-by-step, academically structured manner, starting from data generation and preprocessing, followed by exploratory analysis and baseline model building.

## Problem Statement
University gym facilities experience significant variation in daily footfall due to academic activities, vacations, weather conditions, and operational constraints. Manual estimation of gym usage often leads to inefficient planning and resource utilization.  
The goal of this project is to predict daily gym footfall by modeling these influencing factors using traditional machine learning techniques.

## Data Description

### Data Source
- The dataset is **synthetically generated** using a rule-based Python script.
- No real student or gym usage data is used.

### Time Range & Granularity
- **Start Date:** January 1, 2021  
- **End Date:** January 1, 2026  
- **Frequency:** Daily  

### Key Constraints Modeled
- Gym operates **Monday–Saturday**, closed on Sundays
- Annual vacation closure from **May to June**
- Quarterly exams (midterm and endterm) reduce footfall
- Weather effects (rain, heat, cold) influence attendance
- Equipment maintenance reduces effective capacity
- Campus population varies between 200 and 250 students

The dataset is generated in a reproducible manner and exported as a CSV for development and experimentation.

## Data Cleaning & Preprocessing
- Converted date fields to proper datetime format
- Verified absence of missing or invalid values
- Ensured zero footfall on non-operational days
- One-hot encoded categorical variables
- Converted all boolean features to numeric (0/1)
- Removed non-modeling and intermediate synthetic variables
- Prepared a clean, model-ready dataset

All preprocessing steps are documented in:

## Exploratory Data Analysis (EDA)

EDA was conducted to validate the realism of the synthetic data and understand key patterns.

### Key Analyses Performed
- Daily footfall time-series visualization
- Monthly seasonality analysis
- Exam phase impact analysis
- Weather and maintenance impact analysis
- Capacity utilization distribution
- Correlation analysis
- Seasonal decomposition
- Autocorrelation (ACF) analysis

### Key Insights
- Strong annual seasonality and academic influence
- Clear footfall drops during exams and vacations
- Non-stationary behavior with temporal dependence
- No single dominant feature; multiple interacting factors

EDA is documented in:


## Model Building (Current Progress)

### Approach
The problem is formulated as a **time-aware supervised regression task**, not a pure time-series model. Temporal order is respected during training and testing, while contextual features (academic, environmental, operational) are explicitly modeled.

### Train–Test Split
- **Training:** 2021–2024
- **Testing:** 2025
- No random shuffling (to prevent data leakage)

### Baseline Models Implemented

#### 1. Linear Regression (Full Feature Set)
- Used as an upper-bound linear baseline
- Achieved strong performance due to derived and deterministic features

#### 2. Optimized Linear Regression (Feature Drop)
- Removed derived and redundant features to test true linear capacity
- Performance dropped significantly, highlighting strong non-linear dependencies

This comparison demonstrates that gym footfall cannot be effectively modeled using simple linear assumptions alone.

Modeling work is documented in:

## Key Takeaways So Far
- Gym footfall is driven by **non-linear interactions**
- Linear models have limited explanatory power without derived features
- Ensemble-based models are required for accurate prediction
- The project setup follows sound academic and machine learning practices

## Tools & Technologies
- Python
- Pandas, NumPy
- Scikit-learn
- Matplotlib, Seaborn
- Jupyter Notebook

## Current Status
#### COMPLETED...
- Data generation  
- Data cleaning & preprocessing  
- Exploratory Data Analysis  
- Baseline model building  
- Dashboard development v1

#### PENDING...
- Random Forest model training  
- Model comparison & evaluation  
- Dashboard development v2  
- SQL database integration  

## Notes
This project is designed as an academic proof-of-concept. The synthetic dataset and modeling pipeline demonstrate methodology rather than real-world deployment accuracy.
