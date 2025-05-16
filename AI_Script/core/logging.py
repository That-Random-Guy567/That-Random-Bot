# core/logging.py
import logging
import sys

# Create a logger
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)  # You can change this to DEBUG, WARNING, ERROR, etc.

# Create a handler that writes log messages to the console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the level for the handler

# Create a formatter that defines the format of log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Example usage (in other modules):
# from core.logging import logger
# logger.info("This is an info message")
# logger.error("This is an error message")
