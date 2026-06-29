# 🏎️  F1 Pit Stop Strategy Optimizer
An end-to-end machine learning system that predicts optimal pit stop timing using real Formula 1 telemetry data. Built with XGBoost, FastAPI, and Streamlit, containerized with Docker.

## 📌 What is this Project?
In Formula 1, pit stop timing is one of the most important strategic decisions a team makes during a race. Pit too early and you lose track position. Pit too late and degraded tyres cost seconds every lap.





## 🏗️ Architecture Overview

 ```
┌─────────────────────────────────────┐
                    │           FastF1 API                │
                    │  (real F1 lap + telemetry data)     │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │         Data Pipeline               │
                    │  EDA → Feature Engineering          │
                    │  Tyre degradation, race context,    │
                    │  compound encoding                  │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │       Model Comparison              │
                    │  Baseline Rule → Logistic Regression│
                    │  → XGBoost (best performer)         │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │       Strategy Engine               │
                    │  Turns model output into a          │
                    │  human-readable recommendation:     │
                    │  "Pit now — tyre degradation high"  │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │        FastAPI Backend              │
                    │  Serves predictions via REST API    │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │      Streamlit Frontend             │
                    │  Pick a race, pick a driver,        │
                    │  get a live strategy recommendation │
                    └──────────────────────────────────────┘

Note on scope: this is v1 of the project, using XGBoost as the primary
model. A v2 upgrade — a PyTorch LSTM for forecasting tyre degradation as a
time series — is planned as a future addition once v1 is fully shipped.

```


## Tech Stack
```
Layer                 Tool                        Why
-------------------------------------------------------------------------------------------------------

Data                  FastF1                      Free official F1 telemetry API
Data manipulation     Pandas, Numpy               Industry standard for tabular data
Classical ML          XGBoost                     Best-in-class for tabular data
Deep Learning         PyTorch                     Most widely used DL framework in research + Industry
Experiment Tracking   MLflow                      Tracks every experiment, params, and metrics
API Backend           FastAPI                     Fast, modern Python API framework
Frontend              Streamlit                   Fastest way to build ML web apps in Python
Deployement           Docker + Render             Containerised, reproducible deployment

```


## 📁 Project Struture
```
f1-strategy-optimizer/
│
├── data/
│   ├── raw/cache/               ← FastF1 cache 
│   └── processed/
│       ├── laps_2023.csv               ← cleaned raw lap data
│       ├── features_2023.csv           ← engineered features (XGBoost)
│       └── features_2023_scaled.csv    ← scaled features (Logistic Regression)
│
├── notebooks/
│   ├── 01_eda.ipynb                    ← exploring raw data
│   ├── 02_feature_engineering.ipynb    ← building features, fixing leakage
│   ├── 03_baseline.ipynb               ← simple rule-based baseline
│   ├── 04_logistic_regression.ipynb    ← linear model comparison
│   └── 05_xgboost.ipynb                ← primary model
│
├── src/
│   ├── data/             ← fetch_data.py, feature_engineering.py
│   ├── models/           ← train_xgboost.py, strategy_engine.py
│   └── api/              ← FastAPI backend
│
├── frontend/              ← Streamlit app
├── docker/                ← Dockerfile, docker-compose.yml
├── requirements.txt
└── GETTING_STARTED.md     ← full step-by-step setup guide

```


## Quickstart
1. Clone the repository

```
git clone https://github.com/YOUR_USERNAME/f1-strategy-optimizer.git
cd f1-strategy-optimizer
```

2. Create and activate virtual environment
```
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Fetch real F1 data
```
python3 src/data/fetch_data.py
```
⏳ Takes 5–15 minutes on first run. Cached after that

5. Run Feature engineering
```
python3 src/data/feature_engineering.py
```

6. Train the model 
```
python3 src/models/train_xgboost.py
```

7. View experiment results in MLflow
```
mlflow ui
```



## Model Comparison

Trained on 8 races, tested on 2 completely unseen races (Singapore + Monza),
chosen specifically for having different track characteristics than the
training set:

ModelROC-AUCF1 (pit class)Precision (pit)Recall (pit)Baseline (tyre age rule)0.600.090.050.48Logistic Regression0.830.200.120.51XGBoostin progress









### Author 
#### Hiruni Liyanage
