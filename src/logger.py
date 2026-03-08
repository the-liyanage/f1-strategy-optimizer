"""

Centralised logging setup.
Every script imports logger from here instead of configuring it themselves.

Usage:
    from src.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Fetching data...")

"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path so config can be found 
sys.path.append(str(Path(__file__).parent.parent))
from config import LOG_FORMAT, LOG_LEVEL


# create logs directory if it doesn't exist 
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger.
    Logs to both terminal AND a log file simultaneiously.

    Args:
        name: usually pass __name__ so the logger knows which files it's in

    Returns:
        A configured Python logger

    
    """

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times

    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)

    # HANDLER 1: Terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # HANDLER 2: Log file
    log_filename = LOGS_DIR/ f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Return the fully configured logger 
    return logger