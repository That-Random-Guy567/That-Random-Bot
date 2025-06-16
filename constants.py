# Guild and Channel IDs
import discord

GUILD_SERVER_INT = 1311684718554648637
GUILD_ID = discord.Object(id = GUILD_SERVER_INT) # server id

DELETE_LOG_CHANNEL_ID = 1343485052360720384
EDIT_LOG_CHANNEL_ID = 1356188222119739492
ROLE_LOG_CHANNEL_ID = 1364874169115738222

YOUTUBE_TIME_INTERVAL = 5 # minutes

BUMP_TIME_INTERVAL = 10 #seconds

COUNTING_CHANNEL_ID = 1381569756175269888


TICKET_DATA = {
    "CATEGORY_ID": 1382293749828292638,  # ID of the category where tickets will be created
    "SUPPORT_ROLE_ID": 1311687596098981898,  # ID of the support role that can manage tickets
    "TRANSCRIPTS_CHANNEL_ID": 1384037966749630464,  # ID of the channel where transcripts will be sent
    "TICKET_CHANNEL_ID": 1356184033268203601,  # ID of the channel where ticket creation messages will be sent
}

BOT_PREFIX = "!"


EMOJIS = {
    "PEPE_YES": "<:pepe_yes:1381571891265011772>",
    "PEPE_NO": "<:pepe_no:1381571865063194727>",
    "BOT_PFP": "<:bot_pfp:1381571919958249562>",
}

YOUTUBE_CONFIG = {
    "FEED_URL" : "https://www.youtube.com/feeds/videos.xml?channel_id=UCz_FSOLUPPYSghNQv1pVQTA",
    "UPLOAD_CHANNEL_ID" : 1356190880490324128,
    "FORUM_CHANNEL_ID" : 1364102106939654174,
    "UPLOAD_PING_ROLE" : "<@&1345378358464221204>",
    "RESOURCES_CHANNEL_ID" : 1326207688371212342,
    "DISCUSSION_CHANNEL_ID" : 1364102106939654174,
}

# Bump Reminder Settings
BUMP_CONFIG = {
    "enabled": False,
    "last_ping_time": 0,
    "last_normal_message_time": 0,
    "bump_count": 0,
    "ping_interval": 6 * 60 * 60,  # 6 hours
    "normal_message_interval": 2 * 60 * 60,  # 2 hours
    "channel_id": 1345373029626023999,
    "ping_role": "<@&1355998357033718001>",
}