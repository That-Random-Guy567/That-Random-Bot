# main.py
import discord
import asyncio


from core.bot import Client
from core.logging import logger
from config import TOKEN  # Import only the token from config
from constants import GUILD_SERVER_ID  # Import the global ID from constants
from modules import moderation
from modules import bump_reminder
from modules import youtube_loop
from modules import slash_commands  # Import the slash_commands module


intents = discord.Intents.all()
client = Client(command_prefix="!", intents=intents)

# Register event listeners from moderation.py
client.on_message_delete = moderation.on_message_delete
client.on_message_edit = moderation.on_message_edit

# Register the on_message for bump reminders
client.add_listener(bump_reminder.on_message)


async def setup_tasks():
    try:
        await client.wait_until_ready()  # Ensure client is ready before starting tasks
        logger.info("Bot is ready, setting up tasks...")
        
        await bump_reminder.setup_bump_reminder(client)
        logger.info("Bump reminder setup complete")
        
        await youtube_loop.setup_youtube_loop(client)
        logger.info("YouTube loop setup complete")
        
        await slash_commands.setup_slash_commands(client)
        logger.info("Slash commands setup complete")
        
    except Exception as e:
        logger.error(f"[Error in setup_tasks: {e}]")
        raise  # Re-raise the exception to ensure the bot doesn't silently fail

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        client.loop.create_task(setup_tasks())
        asyncio.run(client.start(TOKEN))
    except discord.LoginFailure:
        logger.error("[Invalid token. Please check your .env file.]")
    except Exception as e:
        logger.error(f"[An error occurred: {e}]")
    finally:
        logger.info("Bot shutdown complete")