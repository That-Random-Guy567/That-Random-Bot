import discord

from core.logging import logger
from constants import LOG_CHANNEL_IDS

def has_image(message: discord.Message) -> bool:
    # Check if any attachment is an image
    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            return True
    # Check if any embed is an image
    for embed in message.embeds:
        if embed.type == "image" or embed.image.url:
            return True
    return False

async def on_message_delete(message: discord.Message):
    if has_image(message):
        return

    delete_log_channel = message.guild.get_channel(LOG_CHANNEL_IDS.DELETE)

    if not delete_log_channel:
        logger.error(f"Could not find log channel with ID {LOG_CHANNEL_IDS.DELETE}")
        return

    if message.author.bot:
        return

    author_ping = message.author.mention if message.author else "Unknown User"
    author_name = message.author.name if message.author else "Unknown User"
    author_id = message.author.id if message.author else "Unknown ID"
    channel_id = f"<#{message.channel.id}>" if message.channel else "Unknown Channel"
    content = message.content if message.content else "No content available"

    embed = discord.Embed(color=discord.Color.red())
    embed.description = f"Message sent by {author_ping} Deleted in {channel_id} \n{content}"
    embed.set_footer(text=f"Author: {author_id} | Message ID: {message.id}")
    if message.author:
        embed.set_author(
            name=author_name,
            icon_url=message.author.avatar.url if message.author.avatar else None
        )
    embed.timestamp = message.created_at

    await delete_log_channel.send(embed=embed)