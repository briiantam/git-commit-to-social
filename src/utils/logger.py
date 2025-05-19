"""Logging utility for the application."""
import os
import logging
from logging.handlers import RotatingFileHandler
from ..config.config import LOG_LEVEL, LOG_FILE

def setup_logging():
    """Set up logging for the application."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
        ]
    )
    
    logging.info("Logging initialized")
