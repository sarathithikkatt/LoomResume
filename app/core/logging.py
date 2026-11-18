import logging
import sys
import os
import io
from datetime import datetime
from app.core.config import settings

def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log file name with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(logs_dir, f'loom_resume_{current_date}.log')
    
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
    ]
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=handlers,
    )
    
    # Optional: silence some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def get_logger(name: str):
    return logging.getLogger(name)
