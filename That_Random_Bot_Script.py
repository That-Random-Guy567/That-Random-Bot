import discord
import asyncio

from core.bot import Client
from core.logging import logger
from config import TOKEN
from constants import GUILD_SERVER_ID
from modules import moderation
from modules import bump_reminder
from modules import youtube_loop
from modules import slash_commands

class BotClient(Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Register event listeners
        self.on_message_delete = moderation.on_message_delete
        self.on_message_edit = moderation.on_message_edit
        self.add_listener(bump_reminder.on_message)

    async def setup_hook(self):
        """Initialize the bot when it first connects to Discord."""
        self.loop.create_task(self.setup_tasks())

    async def setup_tasks(self):
        """Set up all bot tasks and modules."""
        try:
            await self.wait_until_ready()
            logger.info("Bot is ready, setting up tasks...")
            
            # Setup bump reminder
            await bump_reminder.setup_bump_reminder(self)
            logger.info("Bump reminder setup complete")
            
            # Setup YouTube loop
            await youtube_loop.setup_youtube_loop(self)
            logger.info("YouTube loop setup complete")
            
            # Setup slash commands
            await slash_commands.setup_slash_commands(self)
            logger.info("Slash commands setup complete")
            
            logger.info("All tasks setup complete!")
            
        except Exception as e:
            logger.error(f"[Error in setup_tasks: {e}]")
            raise

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")

async def main():
    """Main entry point for the bot."""
    try:
        # Create and start the bot
        client = BotClient()
        logger.info("Starting bot...")
        
        async with client:
            await client.start(TOKEN)
            
    except discord.LoginFailure:
        logger.error("[Invalid token. Please check your .env file.]")
    except Exception as e:
        logger.error(f"[An error occurred: {e}]")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())