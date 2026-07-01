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


# Tyre compound durability encoding (confirmed against real degradation
# rates calulated from this dataset during EDA)
COMPOUND_MAP = {
    "SOFT": 0,
    "MEDIUM": 1,
    "HARD": 2,
    "INTERMEDIATE": 3,
    "WET": 4,
}


# Raw telemetry columns affected by pit-lane contamintion
TELEMETRY_COLS_TO_FIX =[
    "Sector1Time", "Sector2Time", "Sector3Time",
    "SpeedI1", "SpeedI2", "SpeedFL", "SpeedST"
]



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
        df[col] = pd.to_timedelta(df[col], errors = "coerce").dt.total_seconds()
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
            None: pd.NA,
            "nan": pd.NA,
                            })
        df[col] = df[col].astype("boolean")

    logger.info(f"Fixed dtypes for {len(numeric_as_categorical)} categorical"
                f" and {len(bool_cols)} boolean columns")
    return df


def create_target_variable(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the pitted target ( 1 = pitted this lap, 0 = styaed out).
    PitInTime/PitOutTime are dropped immediately after - the model must
    never see them directly, only the extracted yes/no signal.

    """

    df["Pitted"] = df["PitInTime"].notna().astype(int)
    pit_rate = df["Pitted"].mean()
    logger.info(f"Created Pitted target. Pit rate: {pit_rate:.2%}")
    return df

def drop_missing_lap_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows with missing LapTime BEFORE calculating any degradation
    features. This must happen before step 6, otherwise gaps in the lap 
    sequence corrupt the groupby/diff/rolling calculations downstream.

    """

    before = len(df)
    df = df.dropna(subset = ["LapTime"]).copy()
    logger.info(f"Dropped {before - len(df)} rows with missing LapTime."
                f" Remaining: {len(df)}")
    return df


def encode_compounds(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode tyre compounds as ordered integers (durability order).

    """
    df["CompoundEncoded"] = df["Compound"].map(COMPOUND_MAP)
    unmapped = df[df["CompoundEncoded"].isna()]["Compound"].unique()
    if len(unmapped) > 0:
        logger.warning(f"Unmapped compounds found: {unmapped}")
    return df



def fix_tyre_degradation_leakage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build LapTimeDelta, LapTimeRolling3, DegradationFromStintStart - 
    with pit-lap LapTime masked out BEFORE calculation, then forward-filled,
    so these features reflect geuine tyre degradation rather than the
    pit lane detour's contribution to that lap's time

    """
    df = df.sort_values(["RaceName", "Driver", "Stint", "LapNumber"]).reset_index(drop = True)
    lap_time_clean = df["LapTime"].copy()
    lap_time_clean[df["Pitted"] == 1] = np.nan

    group_keys = [df["RaceName"], df["Driver"], df["Stint"]]



    # LapTimeDelta
    df["LapTimeDelta"] = lap_time_clean.groupby(group_keys).diff()
    df["LapTimeDelta"] = df.groupby(
        ["RaceName", "Driver", "Stint"]

    )["LapTimeDelta"].transform(lambda x: x.ffill())
    df["LapTimeDelta"] - df["LapTimeDelta"].fillna(0)


    # LapTimeRolling3
    df["LapTimeRolling3"] = lap_time_clean.groupby(group_keys).transform(
        lambda x: x.rolling(window = 3, min_periods = 1).mean()
    )

    
    df["LapTimeRolling3"] = df.groupby(
        ["RaceName", "Driver", "Stint"]
    )["LapTimeRolling3"].transform(lambda x: x.ffill())
    df["LapTimeRolling3"] = df["LapTimeRolling3"].fillna(df["LapTime"])



    # DegradationFromStintStart (baseline = 3rd lap of stint, skips cols out lap)
    def calx_degradation(group):
        valid = group.dropna()
        if len(valid) >= 3:
            baseline = valid.iloc[2]
        elif len(valid) > 0:
            baseline = valid.iloc[0]
        else:
            return group * np.nan
        return group - baseline
    
    df["DegradationFromStintStart"] = lap_time_clean.groupby(group_keys).transform(calx_degradation)
    df["DegradationFromStintStart"] = df.groupby(
        ["RaceName", "Driver", "Stint"]
    )["DegradationFromStintStart"].transform(lambda x: x.ffill())
    df["DegradationFromStintStart"] = df["DegradationFromStintStart"].fillna(0)

    logger.info("Fixed tyre degradation feature leakage"
                "(LapTimeDelta, LapTimeRolling3, DegradationFromStintStart)")
    return df



def fix_telemetry_leakage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Same root cause as fix_tyre-degradation_leakage, applied to raw 
    telemetry columns. Sector times and speed-trap readings are distorted on
    pit laps (pit lane speed limiter, extra distance),
    so they are masked and forward-filled the same way.

    """
    for col in TELEMETRY_COLS_TO_FIX:
        if col not in df.columns:
            continue
        masked = df[col].copy()
        masked[df["Pitted"] == 1] = np.nan

        df[col] = masked.groupby(
            [df["RaceName"], df["Driver"], df["Stint"]]
        ).transform(lambda x: x.ffill())
        df[col] = df[col].fillna(df[col].median())


    logger.info(f"Fixed telemetry leakage for {len(TELEMETRY_COLS_TO_FIX)} columns")
    return df


def add_race_context_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    RacePctComplete, LapsRemaining, IsLateRace, 
    Requires TotalLaps to exist.

    """
    if "TotalLaps" not in df.columns:
        df["TotalLaps"] = df.groupby("RaceName")["LapNumber"].transform("max")

    df["RacePctComplete"] = df["LapNumber"] /df["TotalLaps"]
    df["LapsRemaining"] = df["TotalLaps"]  - df["LapNumber"]
    df["IsLateRace"] = (df['RacePctComplete'] > 0.7).astype(int)
    
    logger.info("Added race context features (RacePCtComplete, LapsRemaining, IsLateRace)")
    return df

def run_feature_engineering(save: bool = True):
    df = load_raw_laps()
    df = drop_useless_columns(df)
    df = convert_time_columns(df)
    df = fix_data_types(df)
    df = create_target_variable(df)
    df = df.drop(columns = ["PitInTime", "PitOutTime"], errors= "ignore")

    # IMPORTANT: drop missing LapTime BEFORE any degradation calculations
    df = drop_missing_lap_time(df)
    df = encode_compounds(df)

    df = fix_tyre_degradation_leakage(df)
    df = fix_telemetry_leakage(df)
    df = add_race_context_features(df)





    



if __name__ == "__main__":
    run_feature_engineering()