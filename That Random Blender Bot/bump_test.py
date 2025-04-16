# importing discord modules
import discord
from discord.ext import commands
from discord import app_commands

# for safe token keys
import os
from typing import Final
from dotenv import load_dotenv
import asyncio  # Import asyncio

# token loading from .env file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# ------------------- defining some general stuff  -------------------

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

command_prefix = "!"

GUILD_SERVER_ID = 1311684718554648637 # server ID variable
GUILD_ID = discord.Object(id=GUILD_SERVER_ID)  # server id


##################################################################


class Client(commands.Bot):
    def __init__(self, *args, **kwargs):  # Add this init
        super().__init__(*args, **kwargs)
        self.last_ping_time = 0  # Initialize here
        self.last_normal_message_time = 0

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

        # ------------------- Force syncing slash commands -------------------
        try:
            guild = discord.Object(id=GUILD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")

        # --- Bump Reminder Setup ---
        self.channel_id = 1345373029626023999  # channel id (edit this for other servers)
        self.ping_interval = 10 * 60 * 60  # 10 hours in seconds            # time for bump reminders
        self.normal_message_interval = 2.5 * 60 * 60  # 2.5 hours in seconds

        channel = self.get_channel(self.channel_id)
        if channel is None:
            print("Bump reminder channel not found.")
            return

        self.last_ping_time = asyncio.get_event_loop().time()
        self.last_normal_message_time = asyncio.get_event_loop().time()

        # Start the bump reminder loop
        self.loop.create_task(self.bump_reminder_loop(channel))  # Use create_task

    async def bump_reminder_loop(self, channel):  # Separate loop function
        while True:
            await self.bump_reminder(channel)
            await asyncio.sleep(60)  # Refreshing script to see when to execute command. 

    async def bump_reminder(self, channel):
        current_time = asyncio.get_event_loop().time()
        role = discord.utils.get(channel.guild.roles, name="Bumper")  # find the @bump role

        if current_time - self.last_ping_time >= self.ping_interval:
            if role:
                await channel.send(f"{role.mention}, Time to bump!")  # do @bump
                print("Bump reminder (with ping) sent.")
            else:
                print("Bump role not found for ping.")
            self.last_ping_time = current_time

        elif current_time - self.last_normal_message_time >= self.normal_message_interval:
            await channel.send("Time to bump!")  # normal message
            print("Normal bump reminder sent.")
            self.last_normal_message_time = current_time

    # -------------------message responses -------------------
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(f"{command_prefix}who"):
            await message.channel.send(f"Hi there {message.author}")

            if message.author == client.user:
                return
            await message.channel.send(
                f"Server Exclusive nickname: {message.author.nick} \n"
                f"Your name on discord: {message.author.display_name}\n"
                f"Username: {message.author.name}\n"
                f"<@{message.author.id}>"
            )

    # ------------ Message deleting logs ----------
    async def on_message_delete(self, message, *args):
        delete_log_channel_id = 1361330875161116873
        delete_log_channel = client.get_channel(delete_log_channel_id)

        if not delete_log_channel:
            print(f"Error: Could not find log channel with ID {delete_log_channel_id}")
            return

        if message.author == self.user:
            return

        # Author info
        if message.author:
            author_ping = message.author.mention  # Get the mention directly
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
        Deleted_Message.description = (
            f"Message sent by {author_ping} Deleted in {channel_id} \n{content}"
        )  # Put the mention in the description!
        Deleted_Message.set_footer(
            text=f"Author: {author_id} | Message ID: {message.id}"
        )  # Put author name and ID in footer
        if message.author:
            Deleted_Message.set_author(
                name=message.author.name, icon_url=message.author.avatar.url
            )

        Deleted_Message.timestamp = message.created_at

        await delete_log_channel.send(embed=Deleted_Message)

    # ------------ Message editing logs ----------
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        edit_log_channel_id = 1361330924263964692
        edit_log_channel = client.get_channel(edit_log_channel_id)

        if not edit_log_channel:
            print(f"Error: Could not find log channel with ID {edit_log_channel_id}")
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
        Edited_Message = discord.Embed(color=discord.Color.blue())  # Use a different color for edits
        jump_to_message_url = (
            f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id}"
        )
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
                name=author_name,  # Use author_name
                icon_url=before.author.avatar.url,
            )

        Edited_Message.timestamp = (
            after.edited_at or after.created_at
        )  # Use edited_at if available, otherwise use created_at

        await edit_log_channel.send(embed=Edited_Message)


################################################### Slash Commands ##########################################
client = Client(
    command_prefix="!", intents=intents
)  # defining client, but not too early before the main loop


# -------- Send Command ------
@client.tree.command(
    name="send",
    description="Sends a message to a specific channel",
    guild=GUILD_ID,
)
@app_commands.describe(
    channel="The channel you want to send the message to.",
    message="The main message you want to send",
    title='The title of the embed',
    description='The description of the embed',
    color='The color of the embed (e.g., "0x3498db" for blue)',
)
async def send_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str = None,
    title: str = None,  # Make title optional
    description: str = None,  # Make description optional
    color: str = "0x000000",  # Make color optional, default to black
):
    try:
        # If there's a title or description, create an embed
        if title or description:
            # Convert the color string to an integer
            try:
                color_int = int(color, 16)  # Base 16 for hex
            except ValueError:
                await interaction.response.send_message(
                    "Invalid color format. Please use a hexadecimal color code (e.g., '0x3498db').",
                    ephemeral=True,
                )
                return  # Stop if the color is invalid

            # Construct the embed
            embed = discord.Embed(
                title=title if title else "",  # Use title if provided, otherwise ""
                description=description if description else "",  # Use description if provided, otherwise ""
                color=color_int,
            )
            sent_message = await channel.send(embed=embed)  # Send the embed
        elif message:
            sent_message = await channel.send(message)  # Send just the message
        else:
            await interaction.response.send_message(
                "Please provide a message or something for the embed!",
                ephemeral=True,
            )
            return

        channel_link = channel.mention
        if interaction.guild:
            message_link = (
                f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}"
            )
        else:
            message_link = ""
        message_sent_embed = discord.Embed(color=discord.Color.green())
        message_sent_embed.description = (
            f"✅ Message has been sent to {channel_link} You can view it [here]({message_link})."
        )

        await interaction.response.send_message(
            embed=message_sent_embed, ephemeral=False
        )  # send embed to user

    except discord.Forbidden:
        await interaction.response.send_message(
            f"Oops! I don't have permission to send messages in {channel.mention}.",
            ephemeral=True,
        )

    except discord.NotFound:
        await interaction.response.send_message(
            f"Hmm, I couldn't find the channel {channel.mention}.", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)


################ TOKEN #################
client.run(TOKEN)