# core/bot.py
import discord
from discord.ext import commands
from datetime import datetime, timezone
from .logging import logger  # Import the logger
from constants import GUILD_SERVER_ID  # Import from constants

class Client(commands.Bot):
    """
    Custom Discord bot client.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = datetime.now(timezone.utc)
        self.posted_video_ids = set()
        self.first_run = True

    async def on_ready(self):
        logger.info(f"[Logged on as {self.user}!]")
        try:
            guild = discord.Object(id=GUILD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            logger.info(f"[Synced {len(synced)} commands to guild {guild.id}]")
        except Exception as e:
            logger.error(f"[Error syncing commands: {e}]")
        logger.info("Bot is ready.")
        print("###########################")

    async def on_message(self, message):
        await self.process_commands(message)