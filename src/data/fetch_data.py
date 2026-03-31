"""
Phase 1: Fetch real F1 data using FastF1

"""

import sys
from pathlib import Path



import fastf1
import pandas as pd
import numpy as np

# Enable cache
Path("data/raw/cache").mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache("data/raw/cache")

# Races to download
RACES = [
    (2023, "Bahrain",      "R"),
    (2023, "Saudi Arabia", "R"),
    (2023, "Australia",    "R"),
    (2023, "Monaco",       "R"),
    (2023, "Spain",        "R"),
    (2023, "Silverstone",  "R"),
    (2023, "Hungary",      "R"),
    (2023, "Monza",        "R"),
    (2023, "Singapore",    "R"),
    (2023, "Abu Dhabi",    "R"),
]

all_laps = []

for year, race, session_type in RACES:
    print(f"Fetching {race}...")
    try:
        session = fastf1.get_session(year, race, session_type)
        session.load(telemetry=False, weather=False, messages=False)
        laps = session.laps.copy()
        laps["RaceName"] = race
        laps["Year"] = year
        all_laps.append(laps)
        print(f"  ✓ {race}: {len(laps)} laps")
    except Exception as e:
        print(f"  ✗ {race} failed: {e}")

# Combine all races and save
combined = pd.concat(all_laps, ignore_index=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
combined.to_csv("data/processed/laps_2023.csv", index=False)
print(f"\n✅ Done — {len(combined)} total laps saved")







"""
# Logging - using config settings

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, force = True)
logger = logging.fetLogger(__name__)

# Cache - speeds up repeated loads significantly 
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

def fetch_race_laps(year: str, race: str, session_type: str) -> pd.DataFrame:
    
    Fetch lap-by lap data for a single race.
    Returns a DataFrame with one row per lap per driver.
    

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


def clean_laps(laps: pd.DataFrame) -> pd.DataFrame:
    
    Select and clean rele
    
    """