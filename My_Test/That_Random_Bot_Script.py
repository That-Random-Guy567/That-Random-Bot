# main.py
import discord
from core.bot import Client
from core.logging import logger
from config import TOKEN  # Import only the token from config
from constants import GUILD_SERVER_ID  # Import the global ID from constants
from modules import moderation
from modules import bump_reminder
from modules import youtube_loop
import asyncio
from modules import slash_commands  # Import the slash_commands module


intents = discord.Intents.all()
client = Client(command_prefix="!", intents=intents)

# Register event listeners from moderation.py
client.on_message_delete = moderation.on_message_delete
client.on_message_edit = moderation.on_message_edit

# Register the on_message for bump reminders
client.add_listener(bump_reminder.on_message)


# Setup Tasks
async def setup_tasks():
    await client.wait_until_ready()  # Ensure client is ready before starting tasks
    await bump_reminder.setup_bump_reminder(client)
    await youtube_loop.setup_youtube_loop(client)

# Setup slash commands.  This should be done in a setup_hook
async def setup_hook():
    await slash_commands.setup_slash_commands(client)  # Call the setup function
    client.loop.create_task(setup_tasks()) # Move setup_tasks() here

client.setup_hook = setup_hook  # set the setup hook


# Run the botmy
if __name__ == "__main__":
    try:
        asyncio.run(client.start(TOKEN))  # Use asyncio.run()
    except discord.LoginFailure:
        logger.error("[Invalid token. Please check your .env file.]")
    except Exception as e:
        logger.error(f"[An error occurred: {e}]")
