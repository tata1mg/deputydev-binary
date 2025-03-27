import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from pythonjsonlogger import jsonlogger

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Define log files
ACCESS_LOG_FILE = os.path.join(LOG_DIR, "access.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")


# Define JSON log format
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def parse(self):
        return ["time", "level", "message"]


# Function to create a file logger
def get_file_logger(log_file, level):
    handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    formatter = CustomJsonFormatter()
    handler.setFormatter(formatter)

    logger = logging.getLogger(log_file)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False  # Prevent duplicate logs
    return logger


# Configure loggers
access_logger = get_file_logger(ACCESS_LOG_FILE, logging.INFO)
error_logger = get_file_logger(ERROR_LOG_FILE, logging.ERROR)
app_logger = get_file_logger(APP_LOG_FILE, logging.INFO)

# Disable default Sanic console logging
logging.getLogger("sanic.root").handlers.clear()
logging.getLogger("sanic.access").handlers.clear()
logging.getLogger("sanic.error").handlers.clear()
