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

```
Trained on 8 races, tested on 2 completely unseen races (Singapore + Monza), chosen specifically for having different track characteristics than the training set:

Model                       ROC-AUC         F1 (pit class)    Precision(pit)      Recall(pit)
-------------------------------------------------------------------------------------------------------

Baseline (tyre age rule)     0.60            0.09              0.05                 0.48
Logistic Regression          0.83            0.20              0.12                 0.51
XGBoostin                                progress


Class imbalance: only ~3% of laps in the dataset are actual pit stops
(~33:1 ratio), handled via class_weight='balanced' (Logistic Regression) and
scale_pos_weight (XGBoost).
```



Roadmap

 - EDA — explored real race data, found and characterized class imbalance
 - Feature engineering — tyre degradation, race context, leakage fixes
 - Baseline — simple rule-based comparison point
 - Logistic Regression — linear model comparison
 - XGBoost — primary model (final validation in progress)
 - Convert notebooks to production scripts (src/)
 - Strategy engine — turn predictions into readable recommendations
 - FastAPI backend
 - Streamlit frontend
 - Docker deployment


Planned for v2 (after v1 ships):
- PyTorch LSTM for tyre degradation forecasting
- Combine LSTM + XGBoost outputs in the strategy engine

-------------------------------------------------------------------------------------------------------


Key Concepts Applied

Why split by race, not randomly?
Laps from the same race share context(track temperature, safety car periods, circuit characteristics). A random split would leak that context between train and test, making results look better than they really are. Splitting by entire race gives an honest test of generalization to genuinely unseen conditions.

Why compare three models instead of jumping to XGBoost? 
Establishing a baseline and a linear model first proves whether added model complexity is actually earning its place, rather than assuming a more powerful model is automatically better.

Why scale features for Logistic Regression but not XGBoost? 
Logistic Regression's gradient-based optimization is sensitive to feature scale;
tree-based models like XGBoost split on raw thresholds and are unaffected by scale, so scaling there would add complexity with no benefit.







### Author 
#### Hiruni Liyanage
