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
