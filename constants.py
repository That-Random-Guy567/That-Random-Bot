# Guild and Channel IDs
import discord
GUILD_SERVER_ID = 1311684718554648637
GUILD_ID = discord.Object(id = GUILD_SERVER_ID) # server id

DELETE_LOG_CHANNEL_ID = 1361330875161116873
EDIT_LOG_CHANNEL_ID = 1361330924263964692

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