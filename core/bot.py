"""
Core bot client implementation.
Handles basic bot functionality including command syncing and message processing.
"""
import discord
from discord.ext import commands
from datetime import datetime, timezone
from typing import Set

from .logging import logger
from constants import BOT_PREFIX, GUILD_SERVER_INT

class Client(commands.Bot):
    """Custom Discord bot client with extended functionality.
    
    Attributes:
        start_time (datetime): Bot's start time in UTC
        posted_video_ids (set): Set of processed YouTube video IDs
        first_run (bool): Flag to track first run status
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_time: datetime = datetime.now(timezone.utc)
        self.posted_video_ids: Set[str] = set()
        self.first_run: bool = True

    async def on_ready(self) -> None:
        try:
            guild = discord.Object(id=GUILD_SERVER_INT)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                f"Bot {self.user} is ready! Synced {len(synced)} commands to guild {guild.id}"
            )
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")
            raise

    async def on_message(self, message: discord.Message) -> None:
        # Disboard bump detection logic
        if (
            message.author.bot and
            message.embeds and
            message.embeds[0].description and
            "Bump done!" in message.embeds[0].description
        ):
            # Import here to avoid circular import
            from modules import bump_reminder
            await bump_reminder.on_disboard_bump(self, message)

        # Always call this to keep command handling working
        await self.process_commands(message)

    async def setup_hook(self) -> None:
        """Set up bot modules asynchronously after bot is ready."""
        logger.info("Setting up extensions and modules...")

        # Import setup functions here to avoid circular imports
        from modules.bump_reminder import setup_bump_reminder
        from modules.youtube_loop import setup_youtube_loop

        await setup_bump_reminder(self)
        await setup_youtube_loop(self)

        logger.info("Modules setup complete.")


# Instantiate the bot with intents and prefix
intents = discord.Intents.all()
bot = Client(command_prefix=BOT_PREFIX, intents=intents)

# Import modules at the end to avoid circular imports
import modules.bump_reminder
import modules.youtube_loop

import modules.moderation.message_events.edit_message
import modules.moderation.message_events.delete_message

import modules.moderation.role_events.member_role_add
import modules.moderation.role_events.member_role_remove

import modules.tickets

import modules.commands
import modules.auto_responders
import modules.counting