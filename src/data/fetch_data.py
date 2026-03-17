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
