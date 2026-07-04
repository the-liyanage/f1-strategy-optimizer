
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
EXCLUDE_FROM_FEATURES = [
    "Pitted", "Driver", "RaceName",
    "Time", "LapStartTime",
    "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime",
    "LapNumber", "LapTime"
    ]


def load_features(path: Path = FEATURES_CSV) -> pd.DataFrame:
    """
    load the engineered features produced by feature_engineering.py

    """
    logger.info(f"Loading features from {path}")
    df = pd.read_csv(path)
    logger.info(f"Path of the feature engineered dataset: {path}")
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

def get_feature_columns(df: pd.DataFrame) -> list:
    """
    All columns except identity/target columns the model must not see.

    """
    feature_columns = [c for c in df.columns if c not in EXCLUDE_FROM_FEATURES]
    logger.info(f"feature columns: {feature_columns}")
    return feature_columns



def calculate_scale_pos_weight(y_train: pd.Series) -> float:
    """
    XGBoost's handling for severe class imbalance (~32:1 in this dataset, pit stops
    are rare only ~3% of laps). This tells the model to trea each 
    positive example as it if were 32 examples, so it doesn't just learn to always 
    predict "no pit" and still score high on raw accuracy

    """

    weight = (y_train == 0).sum() / (y_train == 1).sum()
    logger.info(f"scale_pos_weight: {weight:.1f}")
    return weight


def train_model(X_train: pd.DataFrame, y_train: pd.DataFrame) -> xgb.XGBClassifier:
    """
    Train XGBoost with parameters chosen for this problem size and 
    severe class imbalance.

    """

    scale_pos_weight = calculate_scale_pos_weight(y_train)

    model = xgb.XGBClassifier(
        n_estimators = 300, # number of trees to build
        max_depth = 6, # how deep each tree can grow
        learning_rate = 0.05, # how much each tree corrects previous mistakes
        subsample = 0.8, # % of rows used per tree (reduce overfitting)
        colsample_bytree = 0.8, # % of features used per tree (reduce overfitting)
        scale_pos_weight=scale_pos_weight, 
        eval_metric = "auc",
        random_state = 42, #reproducibility 
        n_jobs = -1, #use all available CPU cores

    )

    logger.info("Training XGBoost....")
    model.fit(X_train, y_train)
    logger.info("Training complete!")
    return model




def evaluate_model(model: xgb.XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Evaluate on held out races, return key metrics
    """ 

    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:,1]


    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_pred_proba)



    metrics = {
        "roc_auc" : auc,
        "precision_pit": report["1"]["precision"],
        "recall_pit": report["1"]["recall"],
        "f1_pit": report["1"]["f1-score"],
    }


    logger.info("Evaluation Results (Singapore + Monza, unseen):")
    logger.info(f"  ROC-AUC:        {auc:.4f}")
    logger.info(f"  Pit Precision:  {metrics['precision_pit']:.4f}")
    logger.info(f"  Pit Recall:     {metrics['recall_pit']:.4f}")
    logger.info(f"  Pit F1:         {metrics['f1_pit']:.4f}")
 
    return metrics 


def get_feature_importance(model: xgb.XGBClassifier, feature_cols: list) -> pd.DataFrame:
    """Return features sorted by how much the model relied on them."""
    importance = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": model.feature_importances_,
    }).sort_values("Importance", ascending=False)
 
    logger.info("Top 5 most important features:")
    for _, row in importance.head(5).iterrows():
        logger.info(f"  {row['Feature']}: {row['Importance']:.4f}")
 
    return importance

def save_models(model: xgb.XGBClassifier, path: Path = XGBOOST_MODEL_PATH):
    """
    Persist the trained model to disk for later use by the API
    """

    path.parent.mkdir(parents=True, exist_ok= True)
    joblib.dump(model, path)
    logger.info(f"Model saved -> {path}")

def run_training():
    """
    full training pipeline
    """
    df = load_features()
    train_df, test_df  = split_by_race(df)
    feature_cols = get_feature_columns(df)
    X_train = train_df[feature_cols]
    y_train = train_df["Pitted"]
    X_test = test_df[feature_cols]
    y_test = test_df["Pitted"]



    model = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    importance = get_feature_importance(model, feature_cols)

    save_models(model)
    return model, metrics, importance

if __name__ == "__main__":
    run_training()