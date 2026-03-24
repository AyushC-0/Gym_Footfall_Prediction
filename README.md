# Gym Footfall Prediction

A production-grade machine learning system that predicts hourly gym occupancy at a university campus. The project features a full ML lifecycle -- from synthetic data generation and feature engineering to model training, drift detection, and an interactive analytics dashboard.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [The ML Pipeline](#the-ml-pipeline)
- [Data Drift and the V3 Robust Pipeline](#data-drift-and-the-v3-robust-pipeline)
- [Dashboard Pages](#dashboard-pages)
- [Model Performance](#model-performance)
- [License](#license)
- [Author](#author)

---

## Project Overview

University gyms experience complex, non-linear demand patterns driven by academic calendars, weather, exam schedules, and maintenance events. This project builds a comprehensive prediction engine that models these behavioral biases at an **hourly granularity**, trains and compares 5 regression models, and serves predictions through a real-time web dashboard.

The project also demonstrates a complete **Data Drift** lifecycle: simulating a real-world operational change (gym schedule compression), observing model failure, diagnosing the root cause, and engineering a robust recovery pipeline.

---

## Key Features

- **Synthetic Data Engine**: Generates 7 years (2021-2027) of hourly gym footfall data with 12+ behavioral biases including exam stress, weather effects, Sunday closures, maintenance disruptions, and vacation patterns.
- **Multi-Model Training**: Trains and benchmarks 5 algorithms -- XGBoost, Random Forest, CatBoost, KNN, and Linear Regression.
- **Data Drift Simulation**: Injects a structural schedule change in 2026 to demonstrate Covariate Shift and Concept Drift, causing V2 models to fail catastrophically.
- **V3 Robust Pipeline**: Fixes the drift with context-aware features, strict temporal train-test splits (no data leakage), and sample weighting to prioritize recent behavioral patterns.
- **Interactive Dashboard**: A FastAPI-powered web UI with 4 pages -- Landing, Model Overview, Prediction Engine, and Model Comparison -- built with Plotly for interactive charts.
- **Model Versioning**: Full metadata tracking across 4 model generations (V1, V2, Drift, V3) with JSON-based audit trails.

---

## Architecture

```
User Request --> FastAPI Backend --> Preprocessor Pipeline --> ML Model --> Prediction
                     |
                     v
              Static HTML/JS Dashboard (Plotly Charts)
```

**Data Flow:**

```
hourly.py (Generator) --> .db (SQLite) --> preprocess_db.py --> ml_ready.db --> train_models.py --> .pkl (Models)
```

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn |
| **ML Models** | XGBoost, CatBoost, Scikit-learn (Random Forest, KNN, Linear Regression) |
| **Data Processing** | Pandas, NumPy, Scikit-learn Pipelines |
| **Visualization** | Plotly.js |
| **Frontend** | HTML, CSS (TailwindCSS), JavaScript |
| **Database** | SQLite |
| **Serialization** | Joblib (.pkl) |

---

## Project Structure

```
Gym_Footfall_Prediction_Ultra_v2/
|
|-- EXPERIMENT/                    # V2/V3 ML Pipeline (Primary)
|   |-- hourly.py                  # Hourly data generator with behavioral biases
|   |-- preprocess_db.py           # Feature engineering and preprocessing pipeline
|   |-- train_models.py            # Model training, evaluation, and artifact export
|   |-- generate_metadata.py       # Metadata generator for all model versions
|   |-- metrics.json               # V3 model performance metrics
|   |-- metadata/                  # Per-model, per-version metadata files
|   |-- *.pkl                      # Trained model artifacts (V2, Drift, V3)
|   |-- *.db                       # SQLite databases (raw and ML-ready)
|
|-- dashboard/                     # Web Dashboard
|   |-- main.py                    # FastAPI application server
|   |-- static/
|       |-- index.html             # Landing page
|       |-- overview.html          # Model overview and metrics
|       |-- predict.html           # Prediction engine with interactive charts
|       |-- compare.html           # Model comparison with drift analysis
|
|-- scripts/                       # V1 Legacy Pipeline
|   |-- generate_data.py           # Daily data generator (V1)
|
|-- models/                        # V1 Legacy model artifacts
|-- data/                          # Raw data files
|-- requirements.txt               # Python dependencies
|-- LICENSE                        # MIT License
|-- README.md                      # This file
```

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AyushC-0/ML_Endterm.git
   cd ML_Endterm
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Generate the dataset:**

   ```bash
   cd EXPERIMENT
   python hourly.py
   ```

4. **Preprocess the data:**

   ```bash
   python preprocess_db.py
   ```

5. **Train the models:**

   ```bash
   python train_models.py
   ```

6. **Launch the dashboard:**

   ```bash
   cd ../dashboard
   python main.py
   ```

7. **Open your browser** and navigate to `http://localhost:8000`

---

## The ML Pipeline

### Stage 1: Data Generation (`hourly.py`)

Generates ~38,000+ hourly records across 2021-2027 with the following behavioral biases:

| Bias | Description |
| :--- | :--- |
| **Exam Stress** | Footfall drops by 40-60% during exam phases |
| **Weather** | Rainy days reduce attendance by 20-30% |
| **Sunday Closure** | Gym is closed every Sunday |
| **Vacation** | Summer and winter breaks reduce population |
| **Maintenance** | Random facility shutdowns with severity scaling |
| **Morning vs Evening** | Evening sessions see 20-40% higher demand |
| **Seasonal Trends** | Semester start surges, mid-semester dips |
| **Inter-University Events** | Special events create demand spikes |

### Stage 2: Preprocessing (`preprocess_db.py`)

- StandardScaler normalization on numerical features
- One-Hot Encoding for categorical features (session, exam phase, weather)
- Ordinal Encoding for maintenance severity
- Feature pipeline saved as `preprocessor.pkl` for production inference

### Stage 3: Training (`train_models.py`)

- Time-series aware train-test split (no random shuffling)
- Sample weighting to prioritize post-drift data (3x weight for 2026+)
- Evaluation metrics: R-Squared, RMSE, MAPE
- Model artifacts exported as versioned `.pkl` files

---

## Data Drift and the V3 Robust Pipeline

### What is Data Drift?

Data Drift occurs when the statistical properties of the data a model was trained on change over time, causing the model's predictions to degrade.

### The Drift Scenario

Starting January 2026, the university compressed the gym schedule:

| Period | Morning Slots | Evening Slots | Total Daily Slots |
| :--- | :--- | :--- | :--- |
| **2021-2025** | 7-8, 8-9, 9-10 AM | 5-6, 6-7, 7-8 PM | **6 slots** |
| **2026+** | 7-8, 8-9 AM | 6-7, 7-8 PM | **4 slots** |

This caused two types of drift:

- **Covariate Shift**: The input distribution changed (fewer slots, different hour patterns)
- **Concept Drift**: The relationship between inputs and outputs changed (same demand squeezed into fewer slots = higher density per slot)

### How V3 Fixed It

| Fix | Description |
| :--- | :--- |
| **Context Features** | Added `total_daily_slots` so models understand operational capacity |
| **Dropped `year`** | Removed the absolute year feature to prevent tree extrapolation failure |
| **Temporal Split** | Train on 2021 to mid-2026, test on late 2026 to 2027 (no leakage) |
| **Sample Weighting** | Post-drift data weighted 3x to prioritize learning new behaviors |

---

## Dashboard Pages

| Page | URL | Description |
| :--- | :--- | :--- |
| **Landing** | `/` | Project introduction and navigation |
| **Model Overview** | `/overview` | Detailed metrics, feature importance, and model cards |
| **Prediction Engine** | `/predict` | Interactive hourly predictions with parameter controls |
| **Model Comparison** | `/compare` | Side-by-side RMSE chart across V1, V2, Drift, and V3 |

---

## Model Performance

### V3 Robust Pipeline Results (Final)

| Rank | Model | R-Squared | RMSE | MAPE |
| :---: | :--- | :---: | :---: | :---: |
| 1 | **XGBoost** | **0.983** | 4.21 | 7.50% |
| 2 | Random Forest | 0.973 | 5.38 | 9.51% |
| 3 | CatBoost | 0.965 | 6.07 | 7.33% |
| 4 | KNN | 0.932 | 8.48 | 12.10% |
| 5 | Linear Regression | 0.526 | 22.32 | 84.62% |

### Version Comparison (XGBoost)

| Version | R-Squared | RMSE | Status |
| :--- | :---: | :---: | :--- |
| V1 (Daily Baseline) | ~0.65 | 15.2 | Deprecated |
| V2 (Hourly) | 0.903 | 1.49 | Superseded |
| V2 Post-Drift | -- | 14.8 | Failed |
| **V3 (Robust)** | **0.983** | **4.21** | **Production** |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

**Ayush Choudhury**
