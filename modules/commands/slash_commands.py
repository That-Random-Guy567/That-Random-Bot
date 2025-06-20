from discord import app_commands
from core.bot import Client
from core.logging import logger
from constants import GUILD_SERVER_INT, GUILD_ID

# Import commands from their respective modules
from .bot_info import ping, uptime, send_command, resources
from .count import count
from .bump import next_bump, send_bump_cmd
from .social_media import subscribe
from .ticket_creation import ticket
from .help import help


async def setup_slash_commands(bot: Client):
    """Set up and sync slash commands to the guild."""
    try:
        # Add commands to the tree
        commands = [
            subscribe,
            send_command,
            next_bump,
            send_bump_cmd,
            resources,
            uptime,
            ping,
            count,
            ticket,
            help,
        ]
        
        for cmd in commands:
            bot.tree.add_command(cmd, guild=GUILD_ID)
        
        # Sync commands with Discord
        synced = await bot.tree.sync(guild=GUILD_ID)
        logger.info(f"Synced {len(synced)} commands to guild {GUILD_SERVER_INT}")
        
    except Exception as e:
        logger.error(f"Error setting up slash commands: {e}")
        raise