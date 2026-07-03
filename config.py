"""
F1 Pit Stop Strategy Optimizer - Central Config
All project-wide settings live here.

"""

import os
from pathlib import Path

# PATHS ================================================================
ROOT_DIR             = Path(__file__).parent
RAW_DATA_DIR         = ROOT_DIR/ "data" / "raw"
CACHE_DIR            = ROOT_DIR / "data" / "raw" / "cache"
PROCESSED_DATA_DIR   = ROOT_DIR / "data" / "processed"
LOGS_DIR             = ROOT_DIR / "logs"

LAPS_CSV                    = PROCESSED_DATA_DIR / "laps_2023.csv"
FEATURES_CSV                = PROCESSED_DATA_DIR / "features_2023.csv"
FEATURES_SCALED_CSV         = PROCESSED_DATA_DIR / "features_2023_scaled.csv"
FEATURE_IMPORTANCE_CSV      = PROCESSED_DATA_DIR / "feature_importance.csv"


MODELS_DIR          = ROOT_DIR / "src" / "models"
XGBOOST_MODEL_PATH  = MODELS_DIR / "xgboost_pitstop.joblib"


MLFLOW_TRACKING_DIR = ROOT_DIR / "mlflow_tracking"



# DATA - RACES TO COLLECT =================================================
RACES_2023 = [
    ("2023", "Bahrain",      "R"),
    ("2023", "Saudi Arabia", "R"),
    ("2023", "Australia",    "R"),
    ("2023", "Monaco",       "R"),
    ("2023", "Spain",        "R"),
    ("2023", "Silverstone",  "R"),
    ("2023", "Hungary",      "R"),
    ("2023", "Monza",        "R"),
    ("2023", "Singapore",    "R"),
    ("2023", "Abu Dhabi",    "R"),
]

# Races held back for testing (last N in the list above)
TEST_RACES = ["Singapore", "Monza"]



# FEATURE ENGINEERING
# rates calculated from EDA (SOFT degrades fastest, HARD slowest)
COMPOUND_ORDER = {
    "SOFT":         0,
    "MEDIUM":       1,
    "HARD":         2,
    "INTERMEDIATE": 3,
    "WET":          4,
}


# Reverse mapping - used by the strategy engine to recommend compound names
COMPOUND_NAMES = {v: k for k, v in COMPOUND_ORDER.items()}

# Rollin window for lap time smoothing
LAP_TIME_ROLLING_WINDOW = 3

# Real max tyre life discovered during EDA
MAX_TYRE_LIFE = 56

# Columns never fed to the model - identity, target, or leakage sources 
EXCLUDE_FROM_FEATURES = [
    "Pitted", "Driver", "RaceName", "Compound",
    "IsAccurate", "FastF1Generated", "IsPersonalBest",
    "TrackStatus", 
    "PitInTime", "PitOutTime",
    "DriverNumber", "Team"
]


# Final feature set used for XGBoost training
# (updated after data leakage investigation - see notebooks/02_feature_engineering.ipynb)
FEATURE_COLS = [
    "Stint",
    "Sector1Time", "Sector2Time", "Sector3Time",
    "SpeedI1", "SpeedI2", "SpeedFL", "SpeedST",
    "TyreLife",
    "FreshTyre",
    "Position",
    "CompoundEncoded",
    "LapTimeDelta",
    "LapTimeRolling3",
    "DegradationFromStintStart",
    "TotalLaps",
    "RacePctComplete",
    "LapsRemaining",
    "IsLateRace",
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
    # scale_pos_weight calculated dynamically from class imbalance
}
# Decision threshold for converting probability → pit/no-pit recommendation
# Update this after running threshold tuning in notebooks/05_xgboost.ipynb
DECISION_THRESHOLD = 0.50  # placeholder — update after tuning

MLFLOW_EXPERIMENT_XGBOOST = "f1_pitstop_xgboost"


# API =================================================================
API_HOST = "0.0.0.0"
API_PORT = 8000


# LOGGING ==============================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# V2  PLANNED - LSTM TYRE DEGRADATION (not yet implemented)
# LSTM_SEQUENCE_LENGTH      = 
# LSTM_FORECAST_HORIZON     = 
# LSTM_HIDDEN_SIZE          = 
# LSTM_NUM_LAYERS           = 
# LSTM_DROPUT               = 
# LSTM_BATCH_SIZE           = 
# LSTM_EPOCHS               =
# LSTM_LEARNING_RATE.       =
# MLFLOW_EXPERIMENT_LSTM    =