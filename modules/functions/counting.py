import discord
from discord.ext import commands
import json
import os

from core.logging import logger
from core.bot import Client
from constants import COUNTING_CHANNEL_ID, EMOJIS
from core.mongo import db

COUNT_COLLECTION = db["counting"]


# File path for saving count data - make it absolute
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'counting.json')

# Create data directory if it doesn't exist
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"Data directory ensured at: {DATA_DIR}")
except Exception as e:
    logger.error(f"Failed to create data directory: {e}")

# Load saved data if it exists
def load_count_data():
    """Load counting data from MongoDB"""
    data = {}
    for doc in COUNT_COLLECTION.find():
        chan_id = str(doc["channel_id"])
        data[chan_id] = {
            "last_count": doc.get("last_count", 0),
            "last_user": doc.get("last_user", None)
        }
    return data

# Initialize count data
count_data = load_count_data()

def save_count_data():
    """Save counting data to MongoDB"""
    for chan_id, values in count_data.items():
        COUNT_COLLECTION.update_one(
            {"channel_id": int(chan_id)},
            {"$set": {"last_count": values["last_count"], "last_user": values["last_user"]}},
            upsert=True
        )


async def handle_counting(message: discord.Message):
    """Handle counting messages"""
    # Ignore bot messages
    if message.author.bot:
        logger.debug(f"Ignoring bot message in counting channel from {message.author}")
        return

    # Check if message is in counting channel and is numeric
    content = message.content.strip()
    try:
        current = int(content)
    except ValueError:
        # Not a number, ignore the message
        return

    if message.channel.id == COUNTING_CHANNEL_ID:
        logger.print_separator()
        logger.info(f"Processing count from {message.author}: {current}")
        # Convert channel ID to string for consistent key lookup
        chan_id = str(message.channel.id)
        data = count_data.get(chan_id, {"last_count": 0, "last_user": None})
        last_count, last_user = data["last_count"], data["last_user"]

        if last_count == 0 and current != 1:
            reason = f"wrong number (expected 1, got {current})"
        elif message.author.id == last_user:
            reason = "You counted twice in a row"
        elif current != last_count + 1:
            reason = f"wrong number (expected {last_count + 1}, got {current})"
        else:
            reason = None

        if reason:
            logger.info(f"Count failed: {reason}")
            try:
                await message.add_reaction(EMOJIS['PEPE_NO'])
                await message.channel.send(
                    f"{message.author.mention} Counting error: {reason}. Counter reset to 0."
                )
                count_data[chan_id] = {"last_count": 0, "last_user": None}
                save_count_data()
            except discord.HTTPException as e:
                logger.error(f"Failed to add reaction or send message: {e}")
        else:
            logger.info(f"Count successful: {current}")
            try:
                await message.add_reaction(EMOJIS['PEPE_YES'])
                count_data[chan_id] = {"last_count": current, "last_user": message.author.id}
                save_count_data()
            except discord.HTTPException as e:
                logger.error(f"Failed to add reaction: {e}")

async def setup_counting(bot: Client) -> None:
    """Setup counting system"""
    try:
        logger.info("Initializing counting module...")
        bot.add_listener(handle_counting, 'on_message')
        logger.info(f"Counting module initialized for channel ID: {COUNTING_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Failed to initialize counting module: {e}")
        raise