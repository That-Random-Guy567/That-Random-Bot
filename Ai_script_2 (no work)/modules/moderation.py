import discord
from discord.ext import commands
from utils import log
from config import DELETE_LOG_CHANNEL_ID, EDIT_LOG_CHANNEL_ID


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Logs deleted messages to a specific channel."""
        delete_log_channel = self.bot.get_channel(DELETE_LOG_CHANNEL_ID)

        if not delete_log_channel:
            log(f"Error: Could not find log channel with ID {DELETE_LOG_CHANNEL_ID}", level="ERROR")
            return

        if message.author == self.bot.user:
            return

        # Author info
        if message.author:
            author_ping = message.author.mention
            author_name = message.author.name
            author_id = message.author.id
        else:
            author_ping = "Unknown User"
            author_name = "Unknown User"
            author_id = "Unknown ID"

        # Channel info
        channel_id = f"<#{message.channel.id}>" if message.channel else "Unknown Channel"

        # Message content
        content = message.content if message.content else "No content available"

        # Build the embed
        deleted_message = discord.Embed(color=discord.Color.red())
        deleted_message.description = f"Message sent by {author_ping} Deleted in {channel_id} \n{content}"
        deleted_message.set_footer(text=f"Author: {author_id} | Message ID: {message.id}")
        if message.author:
            deleted_message.set_author(
                name=message.author.name,
                icon_url=message.author.avatar.url if message.author.avatar else None
            )

        deleted_message.timestamp = message.created_at

        await delete_log_channel.send(embed=deleted_message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Logs edited messages to a specific channel."""
        edit_log_channel = self.bot.get_channel(EDIT_LOG_CHANNEL_ID)

        if not edit_log_channel:
            log(f"Error: Could not find log channel with ID {EDIT_LOG_CHANNEL_ID}", level="ERROR")
            return

        # Check if the message author is the bot itself
        if before.author == self.bot.user:
            return  # If it's the bot, exit the function and don't log

        # Author info
        if before.author:
            author_ping = before.author.mention
            author_name = before.author.name
            author_id = before.author.id
        else:
            author_ping = "Unknown User"
            author_name = "Unknown User"
            author_id = "Unknown ID"

        # Channel info
        channel_id = f"<#{before.channel.id}>" if before.channel else "Unknown Channel"

        # Message content
        before_content = before.content if before.content else "No content available"
        after_content = after.content if after.content else "No content available"

        # Build the embed
        edited_message = discord.Embed(color=discord.Color.blue())  # Use a different color for edits
        jump_to_message_url = f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id}"
        edited_message.description = (
            f"**Message edited in** {channel_id} "
            f"[Jump to Message]({jump_to_message_url})\n\n"
            f"**Before**\n"
            f"{before_content} \n\n"
            f"**After** \n"
            f"{after_content}"
        )

        edited_message.set_footer(text=f"User ID: {author_id}")
        if before.author:
            edited_message.set_author(
                name=author_name,  # Use author_name
                icon_url=before.author.avatar.url if before.author.avatar else None  # Use avatar URL if available
            )
        edited_message.timestamp = after.edited_at or after.created_at  # Use edited_at if available, otherwise use created_at

        await edit_log_channel.send(embed=edited_message)

def setup(bot):
    bot.add_cog(Moderation(bot))
