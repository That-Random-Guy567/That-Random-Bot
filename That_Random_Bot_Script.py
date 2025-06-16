from keep_alive import keep_alive
keep_alive()

import discord
import asyncio
import signal

from core.bot import Client
from core.logging import logger
from config import TOKEN

from constants import BOT_PREFIX

from modules.moderation.message_events import (
    delete_message, 
    edit_message, 
)
from modules.moderation.role_events import member_role_add, member_role_remove
from modules.moderation.role_events.member_role_remove import MemberRoleRemove

from modules.bump_reminder import BumpReminder

from modules import (
    bump_reminder,
    youtube_loop,
    auto_responders,
    counting,
    tickets,
    )

from modules.commands.slash_commands import setup_slash_commands

class BotClient(Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=BOT_PREFIX, intents=intents)
        
        # Register event listeners
        self.add_listener(delete_message.on_message_delete)

        self.on_message_edit = edit_message.on_message_edit
        self.on_member_update = member_role_add.on_member_update

    async def setup_hook(self):
        """Initialize the bot when it first connects to Discord."""
        self.loop.create_task(self.setup_tasks())
        
        # Setup signal handlers here instead
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, lambda: self.loop.create_task(self.close()))

    async def setup_tasks(self):
        """Set up all bot tasks and modules."""
        try:
            await self.wait_until_ready()
            logger.info("Bot is ready, setting up tasks...")
            
            # Setup YouTube loop
            await youtube_loop.setup_youtube_loop(self)
            logger.info("YouTube loop setup complete")
            
            # Setup slash commands
            await setup_slash_commands(self)
            logger.info("Slash commands setup complete")

            await counting.setup_counting(self)
            logger.info("Counting module setup complete")

            # Setup auto responders
            await auto_responders.setup_auto_responders(self)
            logger.info("Auto responders setup complete")

            # Setup member role add listener
            await self.add_cog(MemberRoleRemove(self))
            logger.info("Member role removal logging setup complete")

            # Setup Bump Reminder COG
            await self.add_cog(BumpReminder(self))
            logger.info("Bump Reminder COG setup complete")

            # Setup ticket system
            await tickets.setup_tickets(self)
            logger.info("Ticket system setup complete")

            logger.info("All tasks setup complete!")
            
        except Exception as e:
            logger.error(f"[Error in setup_tasks: {e}]")
            raise

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info("------")
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")

    async def close(self):
        """Clean shutdown of the bot."""
        try:
            logger.info("Shutting down bot...")
            # Clean up tasks
            if hasattr(self, 'youtube_loop'):
                youtube_loop.youtube_upload_loop.stop()
            await super().close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def create_signal_handler(client: BotClient):
    """Create signal handler with client reference"""
    def signal_handler():
        """Handle system shutdown signals"""
        logger.info("Received shutdown signal")
        client.loop.create_task(client.close())
    return signal_handler

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