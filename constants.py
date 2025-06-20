# Guild and Channel IDs
import discord
from bot_choice import get_bot_config

"""How to use from class: print(BUMP_CONFIG.channel_id)"""

WHICH_BOT = True  # True for That Random Bot, False for Ze Random Test Bot

# Get both emojis and token name from the config
bot_config = get_bot_config()
EMOJIS = bot_config['emojis']
TOKEN_NAME = bot_config['token_name']

BOT_PREFIX = "!"
COUNTING_CHANNEL_ID = 1385173659991146536

GUILD_SERVER_INT = 1311684718554648637
GUILD_ID = discord.Object(id = GUILD_SERVER_INT) # server id


class LogChannelIDs:
    DELETE: int = 1343485052360720384
    EDIT: int = 1356188222119739492
    ROLE_CHANGE: int = 1364874169115738222
LOG_CHANNEL_IDS = LogChannelIDs()

class BumpConfig:
    enabled: bool = False
    last_normal_message_time: float = 0
    normal_message_interval: int = 2 * 60 * 60  # 2 hours
    channel_id: int = 1345373029626023999
    ping_role: str = "<@&1355998357033718001>"
    ping_every_n_reminders: int = 5
    reminder_count: int = 0
    refresh_time: int = 10  # seconds
BUMP_CONFIG = BumpConfig()

class TicketData:
    CATEGORY_ID: int = 1382293749828292638
    SUPPORT_ROLE_ID: int = 1311687596098981898
    TRANSCRIPTS_CHANNEL_ID: int = 1384037966749630464
    TICKET_CHANNEL_ID: int = 1356184033268203601
TICKET_DATA = TicketData()

class YoutubeConfig:
    FEED_URL: str = "https://www.youtube.com/feeds/videos.xml?channel_id=UCz_FSOLUPPYSghNQv1pVQTA"
    UPLOAD_CHANNEL_ID: int = 1356190880490324128
    FORUM_CHANNEL_ID: int = 1364102106939654174
    UPLOAD_PING_ROLE: str = "<@&1345378358464221204>"
    RESOURCES_CHANNEL_ID: int = 1326207688371212342
    DISCUSSION_CHANNEL_ID: int = 1364102106939654174
    TIME_INTERVAL: int = 5 # minutes
YOUTUBE_CONFIG = YoutubeConfig()