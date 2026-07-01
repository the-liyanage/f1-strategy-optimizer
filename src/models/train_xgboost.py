
"""
Phase 1: Train XGBoost Pit Stop Classifier
Predicts: should this driver pit at the end of this lap (Yes/No)

Trains on 8 races, tests on 2 held-out races (Singapore + Monza) chosen
specifically for havibg different track characteristics than the training
set, so the test genuinely measures generalisation to unseen conditions.

"""
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



# Races held out for testing - different circuit types than most of the
# training set (street circuit + low-degradation high-speed circuit),
# so the test measures genuine generalisation.
TEST_RACES = ["Singapore", "Monza"]


# Columns that exist in the dataframe but must never be fed to the model
EXCLUDE_FROM_FEATURES = ["Pitted", "Driver", "RaceName"]


def load_features(path: Path = FEATURES_CSV) -> pd.DataFrame:
    """
    load the engineered features produced by feature_engineering.py

    """
    logger.info(f"Loading features from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows, {df.shape[1]} columns")
    return df


def split_by_race(df: pd.DataFrame):
    """
    Split into train/test by ENTIRE race, not randomly.

    Why: laps from the same race share context (track temperature, safety car periods,
    circuit characteristics). A random split would leak that shared context
    between train and test. Making results look better than they really are. 
    Splitting by whole rae gives an honest test of generalisation
    unseen conditions.
    
    """

    train_df = df[~df["RaceName"].isin(TEST_RACES)]
    test_df = df[df["RaceName"].isin(TEST_RACES)]

    logger.info(f"Train: {len(train_df)} laps from"
                f" {train_df["RaceName"].nunique()} races")
    logger.info(f"Test:  {len(test_df)} laps from {TEST_RACES}")

    return train_df, test_df
    

def run_training():
    """
    full training pipeline
    """
    df = load_features()
    train_df, test_df  = split_by_race(df)

if __name__ == "__main__":
    run_training()