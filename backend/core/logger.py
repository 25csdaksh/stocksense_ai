"""
Structured Logging Module for MARKETMIND AI.
"""
import logging
import sys
from config import settings


def setup_logger(name: str = "marketmind") -> logging.Logger:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(log_level)

    # Avoid duplicate handlers if already configured
    if not logger_instance.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(name)s] %(filename)s:%(lineno)d — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)

    return logger_instance


logger = setup_logger()
