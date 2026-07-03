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