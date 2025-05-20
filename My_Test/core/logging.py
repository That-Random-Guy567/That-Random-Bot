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
# Modified the asctime format string here
formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)8s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Add a filter to the discord logger to adjust its output
discord_logger = logging.getLogger('discord')
if not discord_logger.handlers:
    discord_handler = logging.StreamHandler(sys.stdout)
    # Modified the asctime format string here
    discord_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)8s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    discord_handler.setFormatter(discord_formatter)
    discord_logger.addHandler(discord_handler)
    discord_logger.setLevel(logging.WARNING) # Or INFO, depending on how much discord.py logs you want.

# Example usage (in other modules):
# from core.logging import logger
# logger.info("This is an info message")
# logger.error("This is an error message")