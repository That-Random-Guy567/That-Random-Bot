"""
Core bot client implementation.
Handles basic bot functionality including command syncing and message processing.
"""
import discord
from discord.ext import commands
from datetime import datetime, timezone
from typing import Set

from .logging import logger
from constants import GUILD_SERVER_ID

class Client(commands.Bot):
    """Custom Discord bot client with extended functionality.
    
    Attributes:
        start_time (datetime): Bot's start time in UTC
        posted_video_ids (set): Set of processed YouTube video IDs
        first_run (bool): Flag to track first run status
    """
    
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the bot client with custom attributes."""
        super().__init__(*args, **kwargs)
        self.start_time: datetime = datetime.now(timezone.utc)
        self.posted_video_ids: Set[str] = set()
        self.first_run: bool = True

    async def on_ready(self) -> None:
        """Handle bot ready event and sync commands."""
        try:
            guild = discord.Object(id=GUILD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                f"Bot {self.user} is ready! Synced {len(synced)} commands to guild {guild.id}"
            )
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")
            raise  # Re-raise to ensure errors aren't silently ignored

    async def on_message(self, message: discord.Message) -> None:
        """Process incoming messages for commands."""
        await self.process_commands(message)