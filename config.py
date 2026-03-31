# F1 Pit Stop Strategy Optimizer - Central Config
# All project settings live here

import os 
from pathlib import Path

# Paths

# Root of the project 
ROOT_DIR = Path(__file__).parent

# Data 
RAW_DATA_DIR = ROOT_DIR/"data"/"raw"
CACHE_DIR = ROOT_DIR/"data"/"raw"/"cache"
PROCESSED_DATA_DIR = ROOT_DIR/"data"/"processed"

# Processed files
LAPS_CSV = PROCESSED_DATA_DIR/"laps_2023.csv"
FEATURES_CSV = PROCESSED_DATA_DIR/"features_2023.csv"
FEATURE_IMPORTANCE_CSV = PROCESSED_DATA_DIR/"feature_importance.csv"

# Models
MODELS_DIR = ROOT_DIR/"src"/"models"
XGBOOST_MODEL_PATH = MODELS_DIR/"xgboost_pitstop.joblib"
LSTM_MODEL_PATH = PROCESSED_DATA_DIR/"lstm_tyre_deg.pt"

# MLflow
MLFLOW_TRACKING_DIR = ROOT_DIR/"mlflow_tracking"

# Data - Races to collect

RACES_2023 = [
    ("2023", "Bahrain",       "R"),
    ("2023", "Saudi Arabia",  "R"),
    ("2023", "Australia",     "R"),
    ("2023", "Monaco",        "R"),
    ("2023", "Spain",         "R"),
    ("2023", "Silverstone",   "R"),
    ("2023", "Hungary",       "R"),
    ("2023", "Monza",         "R"),
    ("2023", "Singapore",     "R"),
    ("2023", "Abu Dhabi",     "R"),
]

# Last N races used for testing (rest = training)

TEST_RACE_COUNT = 2


# Feature Engineering

COMPOUND_ORDER = {
    "SOFT": 0,
    "MEDIUM": 1,
    "HARD": 2,
    "INTERMEDIATE": 3,
    "WET": 4,
}

# Rolling window for lap time smoothing
LAP_TIME_ROLLING_WINDOW = 3

# Max tyre life for normalisation (most tyres last under 50 laps)
MAX_TYRE_LIFE = 50 

# Features used for model training (order matters for SHAP plots)
FEATURE_COLS = [
    "LapNumber",
    "TotalLaps",
    "RacePctComplete",
    "LapsRemaining",
    "IsLateRace",
    "CompoundEncoded",
    "TyreLife",
    "TyreLifeNorm",
    "StintNumber",
    "LapTimeSeconds",
    "LapTimeDelta",
    "LapTimeRolling3",
    "DegradationFromStintStart",
    "TrackTemp",
    "AirTemp",
    "Position",
]
 
TARGET_COL = "Pitted"

# XGBOOST MODEL 

XGBOOST_PARAMS = {
    "n_estimators":     300,
    "max_depth":        6,
    "learning_rate":    0.05,
    "subsample":        0.8,
    "colsample_bytree": 0.8,
    "eval_metric":      "auc",
    "random_state":     42,
    "n_jobs":           -1,
    # scale_pos_weight is set dynamically from class imbalance ratio
}
 
MLFLOW_EXPERIMENT_XGBOOST = "f1_pitstop_xgboost"


# LSTM MODEL (Phase 2)

LSTM_SEQUENCE_LENGTH = 10      # How many past laps the LSTM looks at
LSTM_FORECAST_HORIZON = 5      # How many future laps it predicts
LSTM_HIDDEN_SIZE = 64
LSTM_NUM_LAYERS = 2
LSTM_DROPOUT = 0.2
LSTM_BATCH_SIZE = 32
LSTM_EPOCHS = 50
LSTM_LEARNING_RATE = 0.001
 
MLFLOW_EXPERIMENT_LSTM = "f1_tyre_degradation_lstm"


# API (Phase 4)

API_HOST = "0.0.0.0"
API_PORT = 8000

# Logging 
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL  = "INFO"