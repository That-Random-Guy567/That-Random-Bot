from discord import app_commands
from core.bot import Client
from core.logging import logger
from constants import GUILD_SERVER_ID, GUILD_ID

# Import commands from their respective modules
from .bot import ping, uptime, send_command
from .count import count
from .bump import next_bump
from .Social_Media import subscribe

async def setup_slash_commands(bot: Client):
    """Set up and sync slash commands to the guild."""
    try:
        # Add commands to the tree
        commands = [
            subscribe,
            send_command,
            next_bump,
            uptime,
            ping,
            count
        ]
        
        for cmd in commands:
            bot.tree.add_command(cmd, guild=GUILD_ID)
        
        # Sync commands with Discord
        synced = await bot.tree.sync(guild=GUILD_ID)
        logger.info(f"Synced {len(synced)} commands to guild {GUILD_SERVER_ID}")
        
    except Exception as e:
        logger.error(f"Error setting up slash commands: {e}")
        raise