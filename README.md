# 🏎️  F1 Pit Stop Strategy Optimizer
An end-to-end machine learning system that predicts the optimal lap to pit and recommends tyre strategies using real Formula 1 telemetry data. 
Built with XGBoost, PyTorch LSTM, Fast API, and deployed with Docker.

## 📌 What is this Project?
In Formula 1, pit stop timing is one of the most important strategic decisions a team makes during a race. Pit too early and you lose track postiion. Pit too late and your tyres are completely degraded, costing you seconds every lap.


This project builds an ML system that answers two questions:
1. Should this driver pit this lap? (XGBoost classifier)

2. How will this tyre degrade over the next 10 laps (PyTorch LSTM)

It then combines both answers into a strategy engine that recommends the optimal pit window and tyre compound - and serves those recommendations through a live web app.


## Why This Problem?
- Real F1 teams (Mercedes, Ferrari, Red Bull) spen millions solving this exact problem.
- It combines classical ML + deep learning in one project
- The data is real, free and publicly available via FastF1
- It has a clear, explainable output: *Pit Hamilton on lap 28, switch to Medium*
- It can be deployed as a live app with a public URL



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
                    │  fetch_data.py → feature_eng.py     │
                    │  Cleans, transforms, engineers      │
                    │  features from raw lap data         │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌───────────────────┐       ┌─────────────────────────┐
        │  XGBoost Model    │       │   PyTorch LSTM Model    │
        │                   │       │                         │
        │  "Should we pit   │       │  "How will lap times    │
        │   this lap?"      │       │   evolve over the       │
        │  (classification) │       │   next 10 laps?"        │
        │                   │       │  (time series forecast) │
        └─────────┬─────────┘       └────────────┬────────────┘
                  │                              │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │       Strategy Engine        │
                  │  Combines both model outputs │
                  │  + undercut/overcut logic    │
                  │                              │
                  │  Output:                     │
                  │  "Pit on lap 28 → Medium"    │
                  │  "Projected gain: +2.3s"     │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │        FastAPI Backend       │
                  │  Serves predictions via API  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │      Streamlit Frontend      │
                  │  Pick a race, pick a driver  │
                  │  Get strategy recommendations│
                  └──────────────────────────────┘


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
├── config.py                   ← ALL settings live here (paths, params, races)
│                                  change things here, not inside scripts
│
├── data/
│   ├── raw/
│   │   └── cache/              ← FastF1 cache (auto-generated, never edit)
│   └── processed/
│       ├── laps_2023.csv       ← cleaned lap data (generated by fetch_data.py)
│       ├── features_2023.csv   ← engineered features (generated by feature_eng.py)
│       └── feature_importance.csv ← which features matter most
│
├── notebooks/                  ← Jupyter notebooks for exploration
│
├── src/
│   ├── logger.py               ← centralised logging (import this in every script)
│   ├── exception.py            ← custom exception handler
│   │
│   ├── data/
│   │   ├── fetch_data.py       ← Phase 1: download real F1 data via FastF1
│   │   └── feature_engineering.py ← Phase 1: build ML features from raw data
│   │
│   ├── models/
│   │   ├── train_xgboost.py    ← Phase 1: train pit stop classifier
│   │   ├── train_lstm.py       ← Phase 2: train tyre degradation LSTM
│   │   └── strategy_engine.py  ← Phase 3: combine models into recommendations
│   │
│   ├── api/
│   │   └── main.py             ← Phase 4: FastAPI backend
│   │
│   └── utils/                  ← shared helper functions
│
├── frontend/
│   └── app.py                  ← Phase 4: Streamlit web app
│
├── mlflow_tracking/            ← MLflow stores all experiment results here
├── logs/                       ← log files from each run (auto-generated)
├── tests/                      ← unit tests
│
├── docker/
│   ├── Dockerfile              ← how to build the container
│   └── docker-compose.yml      ← run API + frontend + MLflow together
│
├── requirements.txt            ← all Python dependencies
├── .gitignore                  ← what Git should NOT track
└── GETTING_STARTED.md          ← full step-by-step setup guide

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

## Model Performance (Phase 1 - XGBoost)


## Roadmap 
 ```
Phase 1 - Data pipeline + XGBoost pit stop classifier
Phase 2 - PyTorch LSTM tyre degradation forecaster
Phase 3 - Strategy engine (combines both models)
Phase 4 - FastAPI backend + Streamlit frontend + Docker deployement

```


## 🧠 Key Concepts Used
Why XGBoost for Phase 1?
- On tabular data (rows and columns), gradient boosted trees consistently outperform neural networks. XGBoost is the go-to-go choice for structured data in industry and Kaggle competitions alike

Why LSTM for Phase 2?
- Tyre degradation is a time series problem, each lap depends on the laps before it. LSTMs (Long Short-Term Memory networks) are specifically designed to learn patterns in sequences, making them ideal for forecasting lap time evolution over a stint.

Why split by race, not randomly?
- Random splits would leak information, the model could memorise patterns from the same race it's being tested on. Splitting by race means the model is tested on circuits and conditions it has genuinely never seen.

Why MLflow?
- Eveey training run logs its parameters, metrics, and model artifact automatically. This means eperiments are reproducible, comparable, and auditable.










### Author 
#### Hiruni Liyanage
