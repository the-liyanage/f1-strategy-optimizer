# FastAPI Backend - F1 Pit Stop Strategy Optimizer 
"""
Serves the strategy engine as a REST API

Endpoints: 
    GET / health --> health check (used by Docker)
    GET/  races  --> list of available races
    POST / predict -->  get a pit stop recommendation

Run locally with:
    uvicorn src.api.main:app --reload --port 8000

Then visit:
    http://localhost:8000/docs   ← interactive test UI (free, auto-generated)
    http://localhost:8000/health ← health check

"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))



# HTTPExeption lets us send proper error responses (400 status code, instead of crashing)
from fastapi import FastAPI, HTTPException
# pydantic validates incoming data
from pydantic import BaseModel, Field
# asynccontextmanager lets us handles startup/shutdown events, we use this 
# to load the ML model ONCE
from contextlib import asynccontextmanager
# loads the saved XGBoost model file
import joblib

from config import XGBOOST_MODEL_PATH, RACES_2023
from src.models.strategy_engine import get_recommendation, LapSituation
from src.logger import get_logger


logger = get_logger(__name__)



# APP STARTUP - load model once when server starts 
@asynccontextmanager
async def lifespan(app: FastAPI):

    """
    Runs ONCE when the server starts up, before handling any requests.

    WHY LOAD THE MODEL HERE?
    loading a .joblib file from disk takes ~0.5-1 second.
    If we loaded it inside the /predict endpoint, every sing;e API call
    would wait 1 second just to load the model before doing anything,

    Loading once at startup means every subsequent request is instant

    the 'yield' seperates startup code (before) from shutdown code (after).
    we don't need any shutdown logic here, so nothing goes after yield.
    """
    logger.info("Server starting up - loading XGBoost model....")
    app.state.model = joblib.load(XGBOOST_MODEL_PATH)
    logger.info("Model loaded successfully, server ready")
    yield
    logger.info("Server shutting down")


# Create the FastAPI app
# lifespan = connects our startup function to the app
app = FastAPI (
    title = "F1 Pit Stop Strategy Optimizer",
    description = "Predicts optimal pit stop timing using real F1 telemetry data",
    version = "1.0.0",
    lifespan = lifespan,
)


# REQUEST AND RESPONSE MODELS

class PredictRequest(BaseModel):
    """
    defines exactly what JSON the / predict endpoint expects to receive.

    WHY PYDANTIC MODELS?
    without this, we'd have to manually check every field ourselves:
        if 'driver' not in data: return error
        if not isinstance(data["tyre_life"], int): return error
        ---etc fir every field


    Pydantic does all of this automatically. It a required field is missing
    of the wrong type, it returns a clear error before our code even runs.

    Field(...) means required (no default)
    Field(default = X) means optional with a default value
    description = shows up in the / docs UI automatically.
    ge = means "greater than or equal to" (validation constraint).

    
    """

    driver: str = Field(..., description="Driver code eg: HAM VER LEC")
    lap_number: int = Field(..., ge = 1, description = "Current lap of the race")
    tyre_life: int = Field(..., ge = 0, description = "Laps completed on current tyre set")
    compound: str = Field(..., description = "Current tyre compound: SOFT, MEDIUM, HARD, INTERMEDIATE, WET")
    position: int = Field(..., ge = 1, le = 20, description = "Current race position")
    laps_remaining: int = Field(..., ge = 0, description = "Laps remaining until chequered flag")
    lap_time_delta: float = Field(..., description = "Lap time change vs previous lap (seconds)")
    degradation_from_stint_start: float = Field(..., description = "Total time lost since tyre fitted (seconds)")
    lap_time_rolling3: float = Field(...,description = "Current stint number")
    total_laps: int = Field(default = 57, description = "total race distance in laps")


class PredictResponse(BaseModel):
    """
    defines exactly what JSON / predict endpoint sends back

    This is what the Streamlit frontend will read to display the 
    recommendation 
    Every field here maps directly to a field in StrategyRecommendation.

    """
    driver: str
    lap_number: int
    decision: str                   # "PIT" or "STAY OUT"
    confidence_pct: float           # model's probability as percentage
    reasons: list                   # list of plain - English reason strings
    compound_recommendation: str    # what tyre to switch to
    current_compound: str           # what they're currently on
    laps_remaining: int
    tyre_life: int



# ENDPOINTS
@app.get("/health")
def health_check():
    """
    Simple health check - returns ok if the server is running

    Used by Docker to verify the container is alive and ready.
    also useful for checking the server started correctly after deployment.

    the @app.get("/health") decorator tells FastAPI:
    'when someone makes a GET request to /health, run this function'
    """

    return {"status": "ok", "model_loaded": hasattr(app.state, "model")}

@app.get("/races")
def get_races():
    """
    Returns the list of races available in our training data,

    The Streamlit frontend uses this to populate the race selector dropdownn
    We pull the race names directly from config so there is only one source
    of truth - of you add more races to config, they appear here 
    automatially.

    """

    race_names = [race[1] for race in RACES_2023]
    return {"races": race_names}


@app.post("/predict", response_model = PredictResponse)
def predict(request: PredictRequest):
    """
    Main endpoint - takes a lap situation, returns a pit stop recommendation.

    HOW IT WORKS:
        1. FastAPI receives the JSON request body
        2. Pydantic validates every feild automatically
        3. we convert the validated request into a LapSituation object
        4. Pass it to get_recommendation() from our strategy engine
        5. convert the result into a PredictResponse and return it


    the @app.post decorator means this endpoint only accepts POST requests
    (not GET) because we are sending data IN the request body, not
    just asking for dara.

    response_model = PredictResponse tells FastAPU to validate the OUTPUT
    too - if our code accidentally returns a wrrong field, 
    FastAPI catches it


    HTTPException is raised when something goes wrong, FastAPI converts
    it into a proper HTTP error response with a status code and message, instead
    of crashing with a Python traceback
    """

    try:
        logger.info(f"Received predict request for {request.driver} lap {request.lap_number}")

        # convert the pydantic request model into our LapSituation dataclass
        # (strategy engine expects LapSituation, no PredictRequest)
        situation = LapSituation(
            driver=request.driver,
            lap_number=request.lap_number,
            tyre_life=request.tyre_life,
            compound=request.compound,
            position=request.position,
            laps_remaining=request.laps_remaining,
            lap_time_delta=request.lap_time_delta,
            degradation_from_stint_start=request.degradation_from_stint_start,
            lap_time_rolling3=request.lap_time_rolling3,
            stint=request.stint,
            total_laps=request.total_laps

        )
        # get recommendation from strategy enginer
        rec = get_recommendation(situation)

        # convert StrategyRecommendation into PredictResponse
        return PredictResponse(
            driver = rec.driver,
            lap_number = rec.lap_number,
            decision = rec.decision,
            confidence_pct = rec.confidence_pct,
            reasons = rec.reasons,
            compound_recommendation = rec.compoun_recommendation,
            current_compound = rec.current_compound,
            laps_remaining = rec.laps_remaining,
            tyre_life = rec.tyre_life,
        )
    except Exception as e:
        logger.error(f"Prediction failes: {e}")
        raise HTTPException(status_code = 500, detail=str(e))





# RUN LOCALLY
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)