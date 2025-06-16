import discord

from core.logging import logger
from constants import EDIT_LOG_CHANNEL_ID


async def on_message_edit(before: discord.Message, after: discord.Message):
    edit_log_channel = after.guild.get_channel(EDIT_LOG_CHANNEL_ID)

    if not edit_log_channel:
        logger.error(f"Could not find log channel with ID {EDIT_LOG_CHANNEL_ID}")
        return

    if before.author.bot:
        return

    author_ping = before.author.mention if before.author else "Unknown User"
    author_name = before.author.name if before.author else "Unknown User"
    author_id = before.author.id if before.author else "Unknown ID"
    channel_id = f"<#{before.channel.id}>" if before.channel else "Unknown Channel"
    before_content = before.content if before.content else "No content available"
    after_content = after.content if after.content else "No content available"

    embed = discord.Embed(color=discord.Color.blue())
    jump_to_message_url = f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id}"
    embed.description = (
        f"**Message edited in** {channel_id} "
        f"[Jump to Message]({jump_to_message_url})\n\n"
        f"**Before**\n"
        f"{before_content} \n\n"
        f"**After** \n"
        f"{after_content}"
    )

    embed.set_footer(text=f"User ID: {author_id}")
    if before.author:
        embed.set_author(
            name=author_name,
            icon_url=before.author.avatar.url if before.author.avatar else None
        )
    embed.timestamp = after.edited_at or after.created_at

    await edit_log_channel.send(embed=embed)
