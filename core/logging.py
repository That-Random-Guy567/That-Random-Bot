import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Create timestamp for log files
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a logger
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Create formatters
normal_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)8s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
separator_formatter = logging.Formatter('%(message)s')  # Simple formatter for separators

# Set up console logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(normal_formatter)

# Set up file logging with unique timestamp
log_file = os.path.join(logs_dir, f'bot_{timestamp}.log')
file_handler = logging.FileHandler(
    filename=log_file,
    encoding='utf-8',
    mode='w'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(normal_formatter)

# Set up separator handler
separator_handler = logging.StreamHandler(sys.stdout)
separator_handler.setFormatter(separator_formatter)
separator_handler.addFilter(lambda record: record.getMessage() == "------")

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(separator_handler)

# Configure discord.py logger
discord_logger = logging.getLogger('discord')
if not discord_logger.handlers:
    # Add console handler for discord.py logs
    discord_handler = logging.StreamHandler(sys.stdout)
    discord_handler.setFormatter(normal_formatter)
    discord_logger.addHandler(discord_handler)
    
    # Add file handler for discord.py logs with unique timestamp
    discord_file = os.path.join(logs_dir, f'discord_{timestamp}.log')
    discord_file_handler = logging.FileHandler(
        filename=discord_file,
        encoding='utf-8',
        mode='w'
    )
    discord_file_handler.setFormatter(normal_formatter)
    discord_logger.addHandler(discord_file_handler)
    discord_logger.setLevel(logging.WARNING)

# Add a convenience method to logger
def print_separator():
    """Print a separator line that will be logged to both console and file."""
    logger.info("-------------------------------------")

# Make print_separator available when importing logger
logger.print_separator = print_separator