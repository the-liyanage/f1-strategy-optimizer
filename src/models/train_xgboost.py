

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent.parent))

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.metrics import classification_report, roc_auc_score


from config import FEATURES_CSV, XGBOOST_MODEL_PATH
from src.logger import get_logger 



logger = get_logger(__name__)



def run_training():
    """
    full training pipeline
    """
    df = load_features()

if __name__ == "__main__":
    run_training()