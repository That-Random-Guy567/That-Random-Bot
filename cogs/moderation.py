import discord
from discord.ext import commands
from utils.logging import logging
from config.constants import delete_log_channel_id, edit_log_channel_id

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message, *args):
        delete_log_channel = self.get_channel(delete_log_channel_id)

        if not delete_log_channel:
            logging.info(f"Error: Could not find log channel with ID {delete_log_channel_id}")
            return
        
        if message.author == self.user:
            return

        # Author info
        if message.author:
            author_pinsg = message.author.mention  # Get the mention directly
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
        Deleted_Message = discord.Embed(color=discord.Color.red())
        Deleted_Message.description = f"Message sent by {author_ping} Deleted in {channel_id} \n{content}"  # Put the mention in the description!
        Deleted_Message.set_footer(text=f"Author: {author_id} | Message ID: {message.id}")  #Put author name and ID in footer
        if message.author:
            Deleted_Message.set_author(
                name=message.author.name,
                icon_url = message.author.avatar.url if message.author.avatar else None
            )
            
        Deleted_Message.timestamp = message.created_at

        await delete_log_channel.send(embed=Deleted_Message)
        pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        edit_log_channel = self.get_channel(edit_log_channel_id)

        if not edit_log_channel:
            logging.info(f"Error: Could not find log channel with ID {edit_log_channel_id}")
            return
        
        # Check if the message author is the bot itself
        if before.author == self.user:
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
        Edited_Message = discord.Embed(color=discord.Color.blue()) # Use a different color for edits
        jump_to_message_url = f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id}"
        Edited_Message.description = (
            f"**Message edited in** {channel_id} "
            f"[Jump to Message]({jump_to_message_url})\n\n"
            f"**Before**\n"
            f"{before_content} \n\n"
            f"**After** \n"
            f"{after_content}"
        )
        
        Edited_Message.set_footer(text=f"User ID: {author_id}") 
        if before.author:
            Edited_Message.set_author(
                name=author_name, # Use author_name
                icon_url=before.author.avatar.url if before.author.avatar else None # Use avatar URL if available
            )
        Edited_Message.timestamp = after.edited_at or after.created_at # Use edited_at if available, otherwise use created_at

        await edit_log_channel.send(embed=Edited_Message)

        pass