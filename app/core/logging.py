import logging
import sys
from app.core.config import settings

def setup_logging():
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Optional: silence some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def get_logger(name: str):
    return logging.getLogger(name)
