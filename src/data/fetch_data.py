"""
Phase 1: Fetch real F1 data using FastF1

"""

import sys
from pathlib import Path



sys.path.append(str(Path(__file__).parent.parent.parent))

import fastf1
import pandas as pd
import numpy as np
import logging
from config import (
    CACHE_DIR,
    RACES_2023,
    LAPS_CSV,
    LOG_FORMAT,
    LOG_LEVEL,
)

# Logging - using config settings

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, force = True)
logger = logging.fetLogger(__name__)

# Cache - speeds up repeated loads significantly 
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

def fetch_race_laps(year: str, race: str, session_type: str) -> pd.DataFrame:
    """
    Fetch lap-by lap data for a single race.
    Returns a DataFrame with one row per lap per driver.
    """

    logger.info(f"Fetching {year} {race}....  ")

    session = fastf1.get_session(int(year), race, session_type)
    session.load(telemetry=False, weather=True, messages=False)

    laps = session.laps.copy()


    # Add weather data (track temp affects tyre degradation rate)
    weather = session.weather_data
    if not weather.empty:
        laps["TrackTemp"] = weather["TrackTemp"].mean()
        laps["AirTemp"] = weather["AirTemp"].mean()
    else:
        laps["TrackTemp"] = np.nan
        laps["AirTemp"] = np.nan

    # Tag with race metadata
    laps["Year"] = year
    laps["RaceName"] = race
    laps["TotalLaps"] = laps["LapNumber"].max()

    return laps
