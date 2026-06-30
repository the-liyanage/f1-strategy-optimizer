"""
Phase 1: Step 2: Feature Engineering
Transforms raw lap data into ML - ready features for both XGBoost (unscaled)
and Logistic Regression (scaled, multicollinearity - checked).

This script consolidates everything learned and fixed during the 02_feature_engineeering.ipynb notebook,
including two rounds of data leakkage fixes discovered during model degubbing:

    1. TrackStatus - certaain status codes correlated almost perfectly with
       pit stops. (some codes had 100% pit rates), because FastF1's status 
       codes partially encode pit-lane activity directly.
       FIX: dropped entirely.


    2. Pit - lane contamination - LapTime- derived features (LapTimeDelta,
    LapTimeRolling3, DegradationFromStintStart) and raw telemetry
    columns (Sector times, Speed traps) are distorted on the lap a dirver actually
    pits, because that lap includes driving through the pit lane itself
    (speed limiter, extra distance)

    FIX: pit-lap values for these columns are masked as missing and forward - filled
    from the last genuine racing lap, so the model only ever sees the tyre's 
    true condition going INTO the pit decision, never the consequence of 
    having already pitted.
"""



import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))


import numpy as np
import pandas as pd


from sklearn.preprocessing import StandardScaler


from config import LAPS_CSV, FEATURES_CSV
from src.logger import get_logger


logger = get_logger(__name__)



# Columns that are 100% missing in the raw FastF1 exports - pure noise
COLS_TO_DROP_RAW = ["LapStartDate", "Deleted", "DeletedReason"]

# Columns whose name contain "Time" or "Date" need timedelta -- > seconds conversion
TIME_COL_KEYWORD = ["Time", "Date"]

def load_raw_laps(path: Path = LAPS_CSV) -> pd.DataFrame:
    """ load the cleaned lap data produced by fetch_data.py """
    logger.info(f"Loading raw laps from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows, {df.shape[1]}columns")
    return df

def drop_useless_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ Drop columns that are 100% missing in the raw export. """
    cols = [c for c in COLS_TO_DROP_RAW if c in df.columns]
    df = df.drop(columns = cols, errors = "ignore")
    logger.info(f"Dropped useless columns: {cols}")
    return df

def convert_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ Convert all Time/Date columns from timedelta strings to seconds (float)"""
    df.columns = df.columns.str.strip()
    time_cols = [
        c for c in df.columns
        if any(keyword in c for keyword in TIME_COL_KEYWORD)
    ]
    for col in time_cols:
        df[col] = pd.to_timedelta(df[col], errors = "coerce").dt.total_secnds()
    logger.info(f"Converted {len(time_cols)} time columns to seconds")
    return df


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """ Fix categorical and boolean column types. """

    numeric_as_categorical = ["DriverNumber", "Year", "Position", "TrackStatus"]
    for col in numeric_as_categorical:
        if col in df.columns:
            df[col] = df[col].astype("category")
    
    bool_cols = [c for c in df.columns if df[c].dtype == "bool"]
    if "IsPersonalBest" in df.columns:
        bool_cols.append("IsPersonalBest")



    for col in bool_cols:
        df[col] = df[col].map({
            True: True,
            False: False,
            "True": True,
            "False": False,
            None: pd.Na,
            "nan": pd.NA,
                            })
        df[col] = df[col].astype("boolean")

    logger.info(f"Fixed dtypes for {len(numeric_as_categorical)} categorical"
                f"and {len(bool_cols)} boolean columns")
    return df

def run_feature_engineering(save: bool = True):
    df = load_raw_laps()
    df = drop_useless_columns(df)
    df = convert_time_columns(df)
    df = fix_data_types(df)

    ...



if __name__ == "__main__":
    run_feature_engineering()