import logging
from datetime import datetime, timezone

def log(msg, level="INFO"):
    """Helper function for logging with timestamp."""
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    if level == "INFO":
        logging.info(f"[{now}] {msg}")
    elif level == "ERROR":
        logging.error(f"[{now}] {msg}")
    else:
        print(f"[{level}] [{now}] {msg}")
