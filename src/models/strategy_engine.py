import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

# this is used to load the trained model (xgboost)
import joblib
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional

from config import (
    XGBOOST_MODEL_PATH,
    DECISION_THRESHOLD,
    COMPOUND_ORDER,
    COMPOUND_NAMES,
    FEATURE_COLS
)

from src.logger import get_logger
logger = get_logger(__name__)

print("Target Project root", Path(__file__).parent.parent.parent)
# DATA CLASSES
@dataclass
class LapSituation:
    """
    Represent the current race situation for one driver on one lap.
    This is the input to the strategy engine.

    All fields correspond to features the XGBoost model was trained on.
    the API/frontend collects these values and passes them here.

    WHY A DATACLASS?
    - a dataclass is a special python class that's just for holding data
    - it autogenerates __init__, __repr__, etc. without we writing them.
    - it's cleaner than passing a raw dicktionary because:
        -- you get type hints
        -- you get validation
        - it's self-documenting

    """

    driver: str             # "HAM", "VER"
    lap_number: int         # current lap of the race
    tyre_life: int          # how many laps on the current tyre set
    compound: str           # "SOFT", "MEDIUM"....
    position: int           # current race position
    laps_remaining: int     # laps left until the chequered flag
    lap_time_delta: float   # how much slower this lap vs previous (in seconds)
    degradation_from_stint_start: float     # total time lost since tyre fitted (in seconds)
    lap_time_rolling3: float                # rolling avrage of least 3 lap time (in seconds)
    stint: int = 1          # which stint this is 
    total_laps:int = 57     # total race length(default: typical F1 race)
    is_late_race: int = 0   # 1 if past 70% of race distance, else 0




    @dataclass
    class StrategyRecommendation:
        """
        The output of the strategy engine - everything the frontend/API needs
        to display a complete pit stop recommendation to the user

        """

        driver: str
        lap_number: int
        decision: str           # pit or stay out
        confidence_pct : float  # model's probability as a percentage
        reasons: list           # list of plain english reason strings
        compound_recommendation: str        # soft, medium or hard
        current_compound: str               # what they are currently on
        laps_remaining: int
        tyre_life: int 


# MODEL LOADING

# module-level  model cache - loaded once when the moule is first imported,
# then reused for every subsequenct prediction. without this, every single
# API call would load the model from disk, making the API slow
_model = None 



def get_model():
    """
    Load the trained XGBoost model, with caching 
    First call loads from disk; all subsequent calls return the cached version.
    This is called 'lazy loading' we only load when we first need it.

    """

    global _model
    if _model is None:
        logger.info(f"Loading XGBoost model from {XGBOOST_MODEL_PATH}")
        _model = joblib.load(XGBOOST_MODEL_PATH)
        logger.info("Model loaded successfully")
    return _model



# FEATURE PREPARATION

def situation_to_features(sitution: LapSituation) -> pd.DataFrame:
    """
    convert a Lapsituation into a single-row DataFrame that matches 
    exactly what the XGBoost model was trained on.

    Why :
    the model was trained on a specific set of columns in a specific order.
    if we pass columns in a different order, or with different names, or
    with missing columns, XGBoost will either crash or give wrong answers,

    This function gurantees the input always matches training exactly

    """
    race_pct_complete = (sitution.total_laps - sitution.laps_remaining)/sitution.total_laps

    # Build a dictionary of every feature the model expects

    features = {
        "Stint":                sitution.stint,
        "Sector1Time":          0.0,                # not available at prediction time
        "Sector2Time":          0.0,                # filled with neutral values
        "Sector3Time":          0.0,                 # (model learned not to rely on these)
        "SpeedI1":              0.0,                # after leakage fix
        "SpeedI2":              0.0,
        "SpeedFL":    0.0
    }