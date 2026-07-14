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
                f" Tyre age critical - {situation.tyre_life} laps on current set"
            )
        
        # check lap - to lap degradation rate
        if situation.lap_time_delta >= HIGH_DEGRADATION_DELTA:
            reasons.append (
                f" Lap times increasing - {situation.lap_time_delta:+.2f}s vs previous lap"
            )

        # check total accumulated degradation since tyre was new
        if situation.degradation_from_stint_start >= HIGH_TOTAL_DEGRADATION:
            reasons.append (
                f"Significant performance loss = {situation.degradation_from_stint_start:+.2f}s"
                f" slower than stint start"
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
                f"Tyres still young - only {situation.lap_time_delta:+.2f}s vs previous lap"
            )
        
        if situation.lap_time_delta < HIGH_DEGRADATION_DELTA:
            reasons.append(
                f" Lap times stable - {situation.lap_time_delta:+.2f}s vs previous lap"
            )

        if situation.degradation_from_stint_start < HIGH_TOTAL_DEGRADATION:
            reasons.append (
                f" Degradation within acceptable range -"
                f"{situation.degradation_from_stint_start:+.2f}s from stint start"


            )

        if not reasons:
            reasons.append("Tyre performance within acceptable limits - no immediate pit needed")
    return reasons


# THIS IS THE MAIN RECOMMENDATION FUNCTION
def get_recommendation(situation: LapSituation) -> StrategyRecommendation:
    """
    Main entry point for the strategy engine.
    Takes a Lapsituation, returns a full StrategyRecommendation.

    This is what the FASTAPI endpoint will call for every prediction request.

    FLOW:
    LapSituation
        situation_to_features()  convert to model-ready DataFrame
        model.predict_proba()    get raw probability from XGBoost
        hybrid decision logic    model or domain rules --> PIT? STAY OUT
        generate_reasons()       explain why
        recommend_compound()     which tyre  to put on
        StrategyRecommendation   structured output for API/frontend

    """
    logger.info(f"Generating recommendation for {situation.driver} "
                f"lap {situation.lap_number}, "
                f"TyreLife= {situation.tyre_life}, "
                f"Compound = {situation.compound}"
                )
    # Step 1: prepare features
    # Convert the LapSituation object into a single-row DataFrame that
    # matches exactly what the XGBoost model was trained on
    features_df = situation_to_features(situation)

    # Step 2: get probability from model
    # model.predict_proba() returns two numbers per row:
    #   [probability of class 0 (stay out), probability of class 1 (pit)]
    # We take [0][1] meaning: first row, second column = P(pit)

    model = get_model()
    probability = model.predict_proba(features_df)[0][1]
    confidence_pct = round(probability * 100, 1)
 

    # ================================================================

    # Step 3: Hybrid decision logic
    # Why hybrid :
    # Our XGBoost model has low recall - it misses many genuine pit stops
    # This is a known limitation ( only 325 pit examples in training data)
    # A hybrid system compensates by adding domain knowledge rules alongside
    # the model. Real F1 teams always combine ML predictions with engineer
    # judgement - never reply puerly on one signal

    # SIGNAL 1 - Model probability
    # if model is above 24% confident --> recommend pit
    # (threshold tuned for best F1 on our test set)
    model_says_pit = probability >= DECISION_THRESHOLD

    # SIGNAL 2 - Domain knowledge rules
    # These are validated against real pit stop patterns in our EDA:
    #   HIGH_TYRE_AGE = 20 (average tyre age at pit = 20 laps from EDA
    #   HIGH_DEGRADATION_DELTA = 0.5 (meaningful lap-to-lap slowdown threshold)
    #   HIGH_TOTAL_DEGRADATION = 2.0 (significant total wear since new tyres)

    # Rule A: tyre is old AND has lost significant total performane
    # Rule B: tyre is old AND currently getting notably slower lap by lap

    # Either rule alone is enough to trigger a pit recommendation
    # regardless of what the model says

    domain_says_pit = (
        # Rule A: critical age + siginificant accumulated wear
        (situation.tyre_life >= HIGH_TYRE_AGE and
         situation.degradation_from_stint_start >= HIGH_TOTAL_DEGRADATION)
         or
        # Rule B: critical age + actively getting slower right now
        (situation.tyre_life >= HIGH_TYRE_AGE and
         situation.lap_time_delta >= HIGH_DEGRADATION_DELTA
         ) 
    )

    # FINAL DECISION - either signal is enough
    # If the model says pit OR the domain rules say pit --> recommend pit
    # Both must say "STAY OUT" to keep the driver out
    decision = "PIT" if (model_says_pit or domain_says_pit) else "STAY out"

    # Log which signal(s) triggered the decision 
    decision_source = []
    if model_says_pit:
        decision_source.append(f"model ({confidence_pct}% confidence)")
    if domain_says_pit:
        decision_source.append("domain rules")
    if decision_source:
        logger.info(f"  Triggered by: {', '.join(decision_source)}")
    else:
        logger.info("  Neither signal triggered — staying out")






    # ===================================================================
    # Step 4: generate plain English reasons
    # Inspects the actual feature values and explains WHY we recommended
    # this decision in human-readable text for the frontend to display.
    reasons = generate_reasons(situation, decision)

    # Step 5: recommend a compound (only meaningful if pitting)
    # Domain logic: based on laps remaining + current compound
    # (never recommend same compound currently fitted — F1 rules require
    # at least two different compounds per race)
    # =============================================
    compound_rec = reommend_compound(situation.compound, situation.laps_remaining)


    # Step 6: assemble the full recommendation PHEWWWW
    # Bundle everything into a StrategyRecommendation dataclass
    # that the FastAPI endpoint returns as JSON to the frontend.
    recommendation = StrategyRecommendation(
        driver = situation.driver,
        lap_number=situation.lap_number,
        decision=decision,
        confidence_pct=confidence_pct,
        reasons=reasons,
        compound_recommendation=compound_rec,
        current_compound=situation.compound,
        laps_remaining=situation.laps_remaining,
        tyre_life=situation.tyre_life
    )



    logger.info(f"  Decision: {decision} ({confidence_pct}% confidence)")
    logger.info(f"  Reasons: {reasons}")
    logger.info(f"  Compound: switch from {situation.compound} to {compound_rec}")
 
    return recommendation




# QUICK TEST 

if __name__ == "__main__":
    # simulate Hamilton on lap 34 of Abhu Dhabi with degrading MEDIUM tyres
    test_situation = LapSituation(
        driver = "HAM",
        lap_number=42,
        tyre_life=28,
        compound="MEDIUM",
        position=3,
        laps_remaining=16,
        lap_time_delta=1.8,
        degradation_from_stint_start=4.2,
        lap_time_rolling3=95.2,
        stint=2,
        total_laps=58

    )
    rec = get_recommendation(test_situation)
    print("\n" + "="*50)
    print(f"Driver:     {rec.driver}")
    print(f"Lap:        {rec.lap_number}")
    print(f"Decision:   {rec.decision} ({rec.confidence_pct:.1f}% confidence)")
    print(f"Compound:   {rec.current_compound} → {rec.compound_recommendation}")
    print(f"Reasons:")
    for r in rec.reasons:
        print(f"  • {r}")

 
