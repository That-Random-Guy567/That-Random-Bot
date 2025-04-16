# import discord files
import discord
from discord.ext import commands
from discord import app_commands

#for safe token keys
import os
from typing import Final
from dotenv import load_dotenv

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

command_prefix = "!"


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
    

#------------------- Force syncing slash commands -------------------
        try:
            guild = discord.Object(id =  1357697762090549503)
            synced = await self.tree.sync(guild = guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")
        

#-------------------response to users -------------------
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.lower().startswith(f"{command_prefix}who"):
            await message.channel.send(f"Hi there {message.author.display_name}")
            await message.channel.send(
                f"Server Exclusive nickname: {message.author.nick} \n"
                f"Your name on discord: {message.author.display_name}\n"
                f"Username: {message.author.name}\n"
                f"<@{message.author.id}>"
)

    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send(f"You reacted with: {reaction.emoji} bruh")


#------------ Message deleting logs ----------
    async def on_message_delete(self, message, *args):
        log_channel_id = 1358712307785404590
        log_channel = client.get_channel(log_channel_id)

        if not log_channel:
            print(f"Error: Could not find log channel with ID {log_channel_id}")
            return

        # Author info
        if message.author:
            author_ping = message.author.mention
            author_id = message.author.id
        else:
            author_ping = "Unknown User"
            author_id = "Unknown ID"

        # Channel info
        channel_id = f"<#{message.channel.id}>" if message.channel else "Unknown Channel"

        # Message content
        content = message.content if message.content else "No content available"

        # Build the embed
        Deleted_Message = discord.Embed(color=discord.Color.red())
        Deleted_Message.add_field(
            name=f"Message sent by {author_ping} Deleted in {channel_id}",
            value=content,
            inline=False
        )
        Deleted_Message.set_footer(text=f"Author: {author_id} | Message ID: {message.id}")
    
        if message.author:
            Deleted_Message.set_author(
                name=message.author.name,
                icon_url=message.author.avatar.url
            )
        
        Deleted_Message.timestamp = message.created_at

        await log_channel.send(embed=Deleted_Message)

#------------------- intents -------------------
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
client = Client(command_prefix="!", intents=intents) # can change the command prefix, may not work.


GUILD_ID = discord.Object(id = 1357697762090549503) # server id




################ TOKEN (remove when sharing code) #################
client.run(TOKEN)
