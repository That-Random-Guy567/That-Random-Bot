from .slash_commands import setup_slash_commands
from .bump import next_bump
from .count import count
from .Social_Media import subscribe
from .bot_info import ping, uptime, send_command



# Export the commands you want available when importing from modules.commands
__all__ = [
    'setup_slash_commands',
    'next_bump',
    'count',
    'subscribe',
    'ping',
    'uptime',
    'send_command'
]

# example usage: from modules.commands import *