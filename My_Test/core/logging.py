# core/logging.py
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Create a logger
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Create formatters
formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)8s %(name)s: %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S')

# Set up console logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Set up file logging with rotation
log_file = os.path.join(logs_dir, f'bot_{datetime.now().strftime("%Y-%m-%d")}.log')
file_handler = RotatingFileHandler(
    filename=log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configure discord.py logger
discord_logger = logging.getLogger('discord')
if not discord_logger.handlers:
    # Add console handler for discord.py logs
    discord_handler = logging.StreamHandler(sys.stdout)
    discord_handler.setFormatter(formatter)
    discord_logger.addHandler(discord_handler)
    
    # Add file handler for discord.py logs
    discord_file_handler = RotatingFileHandler(
        filename=os.path.join(logs_dir, f'discord_{datetime.now().strftime("%Y-%m-%d")}.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    discord_file_handler.setFormatter(formatter)
    discord_logger.addHandler(discord_file_handler)
    discord_logger.setLevel(logging.WARNING)  # Or INFO for more verbose discord.py logs

# Example usage (in other modules):
# from core.logging import logger
# logger.info("This is an info message")
# logger.error("This is an error message")