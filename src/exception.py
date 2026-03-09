"""
Custom exception handling.

Gives cleaner, more informative error messages when things go wrong.

Usage:
    from src.exception import F1ProjectExecption
    raise F1ProjectException("falied to load race data", detailes = "bahrain 2023 not found in cache")

"""

import sys
import traceback

def get_error_details(error: Exception) -> str:
    """
    Extraccts the filename, line number and message from an exception.
    Much more useful than a raw Python traceback.
    
    """
    exc_type, exc_value, exc_tb = sys.exc_info()

    if exc_tb is not None:
        filename = exc_tb.tb_frame.f_code.co_filename
        line_no = exc_tb.tb_lineno
        return f"Error in [{filename}] at the line [{line_no}]: {str(error)}"
    else:
        return str(error)
    

class F1ProjectException(Exception):
    """
    Custom exception for the F1 Strategy Optimizer.
    Wraps standard Python exceptions with more context.

    eg:
        F1ProjectException: Failed to fetch race data
        -> Error in [src/data/fetch_data.py] at the line [43]: Connection timeout
    
    """

    def __init__(self, message:str, error: Exception = None, details: str = None):
        self.message = message
        self.details = get_error_details(error) if error else details

        full_message = f"{message}"
        if self.details:
            full_message += f"\n -> {self.details}"
        
        super().__init__(full_message)


    def __str__(self):
        return self.args[0]