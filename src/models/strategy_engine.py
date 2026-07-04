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
    SHORT_STINT_LAPS,
    MEDIUM_STINT_LAPS,
    HIGH_DEGRADATION_DELTA,
    HIGH_TYRE_AGE,
    HIGH_TOTAL_DEGRADATION,
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
        "Stint":                        sitution.stint,
        "Sector1Time":                  0.0,                # not available at prediction time
        "Sector2Time":                  0.0,                # filled with neutral values
        "Sector3Time":                  0.0,                 # (model learned not to rely on these)
        "SpeedI1":                      0.0,                # after leakage fix
        "SpeedI2":                      0.0,
        "SpeedFL":                      0.0,
        "SpeedST":                      0.0,
        "TyreLife":                     sitution.tyre_life,
        "FreshTyre":                    1 if sitution.tyre_life <=1 else 0,
        "Position":                     sitution.position,
        "CompoundEncoded":              COMPOUND_ORDER.get(sitution.compound, 1),
        "LapTimeDelta":                 sitution.lap_time_delta,
        "LapTimeRolling3":              sitution.lap_time_rolling3,
        "DegradationFromStintStart":    sitution.degradation_from_stint_start,
        "TotalLaps":                    sitution.total_laps,
        "RacePctComplete":              race_pct_complete,
        "LapsRemaining":                sitution.laps_remaining,
        "IsLateRace":                   1 if race_pct_complete > 0.7 else 0,
    }

    # convert to a single-row DataFrame - same format model.predict() expets
    df = pd.DataFrame([features])

    # Ensure column order matches training exactly - XGBoost is sensitive to this
    available_cols = [c for c in FEATURE_COLS if c in df.columns]
    df = df[available_cols]

    return df



# COMPOUND RECOMMENDATION

def reommend_compound(
        current_compound: str,
        laps_remaining: int,
) -> str:
    """
    Recommend which tyre compound to swtich to based on:
    1. How many laps are remaining (determines how long the tyre need to last)
    2. What compound is currently fitted (F1 rules require at least two
        different compounds per race, so we never recommend the same one.)

    3. Whether the car is on wet weather tyres (different logis applies)


    """

    # wet weather tyres - recommend MEDIUM as the default dry compound
    if current_compound in ["INTERMEDIATE", "WET"]:
        return "MEDIUM"
    
    # Choose based on laps remaining
    if laps_remaining < SHORT_STINT_LAPS:
        # very few laps left --> SOFT for maximum pace sprint to finish
        preferred = "SOFT"
    elif laps_remaining < MEDIUM_STINT_LAPS:
        # Moderate laps left --> MEDIUM for balanced performance/durability
        preferred = "MEDIUM"
    else:
        # Many laps left --> HARD for durability, avoid another stop
        preferred = "HARD"

    # never recommend the same compound currently fitted
    if preferred == current_compound:
        # fall back to the next -best option
        fallback_map ={
            "SOFT": "MEDIUM",
            "MEDIUM": "HARD",
            "HARD": "MEDIUM"

        }
        preferred = fallback_map.get(preferred, "MEDIUM")
    return preferred

# REASON GENERATION

def generate_reasons(situation: LapSituation, decision: str) -> list:
    """
    Inspect the most important feature values and generate plain - English
    explanation for why the strategu engine is reommending PIT or STAY OUT.

    for a PIT recommendation:
    - explain what signals are driving the decision (high tyre age, rising lap times,
    significant degradation, late-race timing window)

    for a STAY - OUT recommendation:
    - explain why it's safe to stay (tyres still performing, plenty of pit window remaining,
      early in stint)

      this is the "EXPLANABILITY LAYER" - turning model numbers 
      into human reasoning that an F1 engineer ( or a user of our app)
      an understand and verify againt their own track - side observations.

    """

    reasons = []

    if decision == "PIT":
        # Check tyre age
        if situation.tyre_life >= HIGH_TYRE_AGE:

            reasons.append(
                f" Tyre age critica; - {situation.tyre_life} laps on current set"
            )
        
        # check lap - to lap degradation rate
        if situation.lap_time_delta >= HIGH_DEGRADATION_DELTA:
            reasons.append (
                f" Lap times inscreasing - {situation.lap_time_delta:+.2f}s vs previous lap"
            )

        # check total accumulated degradation since tyre was new
        if situation.degradation_from_stint_start >= HIGH_TOTAL_DEGRADATION:
            reasons.append (
                f"Significant performane loss = {situation.degradation_from_stint_start:+.2f}s"
                f"slower than stint start"
            )

        # check strategic timing window 
        race_pct = (situation.total_laps - situation.laps_remaining) / situation.total_laps
        if race_pct > 0.7 :
            reasons.append (
            f"Late - race strategic window - {situation.laps_remaining} laps remaining"
            )
        
        # if no specific reason triggered bu model still says pit
        if not reasons:
            reasons.append(
                f"Model confidence above threshold - combined tyre metrics suggest pitting now"
            )
    
    else: # STAY OUT
        # explain why it's still safe to stay out
        if situation.tyre_life < HIGH_TYRE_AGE:
            reasons.append (
                f"Tyres still younf - only {situation.lap_time_delta:+.2f}s vs previous lap"
            )
        
        if situation.lap_time_delta < HIGH_TOTAL_DEGRADATION:
            reasons.append(
                f" Lap times stable = {situation.lap_time_delta:+.2f}s vs previous lap"
            )

        if situation.degradation_from_stint_start < HIGH_TOTAL_DEGRADATION:
            reasons.append (
                f" Degradation within acceptable range -"
                f"{situation.degradation_from_stint_start:+.2f}s from stint start"


            )

        if not reasons:
            reasons.append("Tyre performance within acceptable limits - no immediate pit needed")
    return reasons
