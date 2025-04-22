# importing discord modules
import discord
from discord.ext import commands, tasks
from discord import app_commands

#time var
import asyncio
import time
from datetime import datetime, timezone, timedelta

#for yt video
import feedparser

#logging info
import logging

#for safe token keys
import os
from typing import Final
from dotenv import load_dotenv

# token loading from .env file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

#------------------- defining some general stuff  -------------------

# intents
intents = discord.Intents.all()

#logging
logging.basicConfig(level=logging.INFO)

command_prefix = "!"

GUILD_SERVER_ID = 1357697762090549503 # server ID variable 
GUILD_ID = discord.Object(id = GUILD_SERVER_ID) # server id


##################################################################

class Client(commands.Bot):
    """
    Custom Discord bot client for managing bump reminders, YouTube uploads, 
    moderation logs, and other server-related tasks.
    """
    def __init__(self, *args, **kwargs):  # Add this init
        super().__init__(*args, **kwargs)
        #uptime counter
        self.start_time = datetime.now(timezone.utc)
        #bump vars
        self.bump = {
            "enabled": False,
            "last_ping_time": 0,
            "last_normal_message_time": 0,
            "bump_count": 0,
            "ping_interval": 6 * 60 * 60,  # 6 hours
            "normal_message_interval": 2 * 60 * 60,  # 2 hours
            "channel_id": 1361939054328938628  # Set early so it's available
        }
        #yt stuff
        self.youtube_upload_channel_id = 1362814303475859719
        self.youtube_forum_channel_id = 1364102106939654174
        self.youtube_upload_ping_role = "<@&1362813561667190885>"
        self.feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCz_FSOLUPPYSghNQv1pVQTA"
        self.posted_video_ids = set()
        self.first_run = True  # Skip alerts on the first check

#--- login ---
    async def on_ready(self):
        logging.info(f"[Logged on as {self.user}!]")

# ------------------- Force syncing slash commands -------------------
        try:
            guild = discord.Object(id=GUILD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            logging.info(f"[Synced {len(synced)} commands to guild {guild.id}]")


        except Exception as e:
            logging.info(f"[Error syncing commands: {e}]")
        print("###########################")

######## start yt loop #######
        # Start the YouTube upload loop
        if not self.youtube_upload_loop.is_running():
            self.youtube_upload_loop.start()
            logging.info("YouTube upload loop started.")

####### Bump stuff #######
# -------- Bump Reminder Setup ------s
        channel = self.get_channel(self.bump["channel_id"])
        if channel is None:
            logging.info("[Bump reminder channel not found.]")
            return

    # Start the reminder loop
        self.loop.create_task(self.bump_reminder_loop(channel))

#------- bump loop def -------
    # Loop to send bump reminders at regular intervals
    async def bump_reminder_loop(self, channel):
        await self.wait_until_ready()
        while not self.is_closed():
            if not self.bump.get("enabled", False):
                # Skip the loop if bump reminders are disabled
                await asyncio.sleep(60)
                continue

            now = asyncio.get_running_loop().time()

            # Check if it's time to send a ping reminder
            if now - self.bump["last_ping_time"] > self.bump["ping_interval"]:
                bump_ping = "<@&1361940574193586287>"
                await channel.send(f"🔔 **Time to bump the server {bump_ping}!** Don’t forget to use `/bump`.")
                self.bump["last_ping_time"] = now

            # Check if it's time to send a normal reminder
            elif now - self.bump["last_normal_message_time"] > self.bump["normal_message_interval"]:
                await channel.send("⏰ Just a friendly reminder: it's time to bump the server again!")
                self.bump["last_normal_message_time"] = now

            # Wait before checking again
            await asyncio.sleep(60)
            
#----- initializng and using bump loop ------
    async def on_message(self, message):
        await self.process_commands(message)

        if (
            message.author.bot and
            message.embeds and
            message.embeds[0].description and
            "Bump done" in message.embeds[0].description
        ):
            print("----------------------")
            logging.info("[✅ Detected Disboard bump. Resetting timers and enabling reminders.]")

            now = asyncio.get_running_loop().time()
            self.bump["last_ping_time"] = now
            self.bump["last_normal_message_time"] = now
            self.bump["enabled"] = True  # Start the timers after bump

            # Increment the bump count
            self.bump["bump_count"] += 1

            logging.info(f"[📈 Bump count: {self.bump['bump_count']}]")
            print("----------------------")

            if self.bump["bump_count"] >= 12:
                bump_ping = "<@&1361940574193586287>"
                await message.channel.send(f"🎯 **Time to bump {bump_ping}!**")
                self.bump["bump_count"] = 0  # Reset the count

############ Youtube Video upload ping auto -------
    # Helper function for logging with timestamp
    def log(self, msg, level="LOG"):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{level}] [{now}] {msg}")

#---- youtube_upload_loop_usage -----
    @tasks.loop(minutes=10)  # Check every 10 minutes
    async def youtube_upload_loop(self):
        print("----------------------")
        self.log("Checking YouTube feed...")

        try:
            # Add a nocache parameter to bypass caching
            feed_url_with_cache_bypass = f"{self.feed_url}&nocache={int(time.time())}"

            # Parse the YouTube feed
            feed = feedparser.parse(feed_url_with_cache_bypass)

            if feed.entries:
                latest_video = feed.entries[0]
                self.log(f"Latest video entry: {latest_video.title}")

                # Check if the video ID exists in the feed entry
                if hasattr(latest_video, 'yt_videoid'):
                    video_id = latest_video.yt_videoid
                    self.log(f"Video ID found: {video_id}")
                else:
                    self.log("No video ID found in the latest feed entry.", level="ERROR")
                    return

                # Skip the first video on startup to avoid duplicate alerts
                if self.first_run:
                    self.log(f"Skipping first video (startup): {video_id}")
                    self.posted_video_ids.add(video_id)
                    self.first_run = False
                elif video_id not in self.posted_video_ids:
                    # Send a notification for new videos
                    channel = self.get_channel(self.youtube_upload_channel_id)
                    forum_channel = self.get_channel(self.youtube_forum_channel_id)  # Forum channel ID
                    video_url = f"https://youtu.be/{video_id}"

                    if channel:
                        # Send the announcement in the main channel
                        await channel.send(f"{self.youtube_upload_ping_role} New video just dropped! 🎬\n{video_url}")
                        self.log(f"New video uploaded: {video_url}")

                    # Create a forum post for the video
                    if forum_channel and isinstance(forum_channel, discord.ForumChannel):
                        # Find the "Youtube Video" tag or use the last tag in the list
                        tag_to_apply = None
                        if forum_channel.available_tags:
                            for tag in forum_channel.available_tags:
                                if tag.name.lower() == "youtube video":
                                    tag_to_apply = tag
                                    break
                            if not tag_to_apply:
                                tag_to_apply = forum_channel.available_tags[-1]  # Use the last tag if "Youtube Video" is not found
                        else:
                            self.log(f"No tags available in forum channel ID {self.youtube_forum_channel_id}.", level="ERROR")
                            return
                        if tag_to_apply:
                            forum_post = await forum_channel.create_thread(
                                name=latest_video.title,  # Use the video title as the post title
                                content=f"🎥 **{latest_video.title}**\n{video_url}",  # Use the video link as the post content
                                applied_tags=[tag_to_apply.id]  # Apply the selected tag
                            )
                            self.log(f"Forum post created for video: {latest_video.title} with tag: {tag_to_apply.name}")
                        else:
                            self.log(f"No tags available in forum channel ID {self.youtube_forum_channel_id}.", level="ERROR")
                    else:
                        self.log(f"Could not find forum channel ID {self.youtube_forum_channel_id} or it is not a ForumChannel.", level="ERROR")
                    self.posted_video_ids.add(video_id)
                else:
                    self.log(f"Video already posted: {video_id}")
            else:
                self.log("No entries found in the feed.")

        except Exception as e:
            self.log(f"Error checking YouTube feed: {e}", level="ERROR")
            await asyncio.sleep(60)

    @youtube_upload_loop.before_loop
    async def before_youtube_upload_loop(self):
        await self.wait_until_ready()
        self.log("Bot is ready. Starting YouTube upload loop.")


###########################     MODERATION      ##############################

# ------------ Message deleting logs ----------
    async def on_message_delete(self, message, *args):
        delete_log_channel_id = 1358712307785404590
        delete_log_channel = self.get_channel(delete_log_channel_id)

        if not delete_log_channel:
            logging.info(f"Error: Could not find log channel with ID {delete_log_channel_id}")
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
        Deleted_Message.description = f"Message sent by {author_ping} Deleted in {channel_id} \n{content}"  # Put the mention in the description!
        Deleted_Message.set_footer(text=f"Author: {author_id} | Message ID: {message.id}")  #Put author name and ID in footer
        if message.author:
            Deleted_Message.set_author(
                name=message.author.name,
                icon_url = message.author.avatar.url if message.author.avatar else None
            )
            
        Deleted_Message.timestamp = message.created_at

        await delete_log_channel.send(embed=Deleted_Message)

# ------------ Message editing logs ----------
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        edit_log_channel_id = 1361609258810085407
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

###########################################         Slash Commands          #############################################
client = Client(command_prefix="!", intents=intents) # defining client, but not too early before the main loop

""" Subscribe
@client.tree.command(name="subscribe", description="Subscribe to That Random Blender Guy", guild=GUILD_ID)
async def subscribe(interaction: discord.Interaction):
    subscribe_embed = discord.Embed(
        title="Subscribe Here",
        url="https://www.youtube.com/user/@thatrandomblenderguy?sub_confirmation=1",
        description="Click the link above to subscribe to That Random Blender Guy on YouTube!",  # Added description
        color=discord.Color.red(), 
    )
    subscribe_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1328989641684291597.webp?size=48&name=ThatRandomBlenderGuyLogo")
    await interaction.response.send_message(embed=subscribe_embed)
"""

#-------------- Send command -----------
@client.tree.command(name="send", description="Sends a message to a specific channel", guild=GUILD_ID)
@app_commands.describe(
    channel='The channel you want to send the message to.',
    message="The main message you want to send",
    title='The title of the embed',
    description='The description of the embed',
    color='The color of the embed (e.g., "blurple", "red", "green", or a hex code like #FF5733)',
)
async def send_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str = None,
    title: str = None,  # Make title optional
    description: str = None,  # Make description optional
    color: str = "blurple",  # Default to Discord blurple
):
    # Predefined color mapping
    predefined_colors = {
        "blurple": discord.Color.blurple(),
        "red": discord.Color.red(),
        "green": discord.Color.green(),
        "blue": discord.Color.blue(),
        "yellow": discord.Color.yellow(),
        "orange": discord.Color.orange(),
        "purple": discord.Color.purple(),
        "white": discord.Color.from_rgb(255, 255, 255),  # Custom white color
        "black": discord.Color.from_rgb(0, 0, 0),  # Custom black color
    }

    try:
        # Determine the embed color
        if color.lower() in predefined_colors:
            embed_color = predefined_colors[color.lower()]
        elif color.startswith("#") and len(color) == 7:  # Check if it's a hex code
            try:
                # Convert hex to RGB and create a discord.Color
                hex_color = int(color[1:], 16)  # Convert hex string to integer
                embed_color = discord.Color(hex_color)
            except ValueError:
                await interaction.response.send_message(
                    "Invalid hex color code. Please use a valid hex code (e.g., `#FF5733`).",
                    ephemeral=True,
                )
                return
        else:
            await interaction.response.send_message(
                f"Invalid color. Please choose from: {', '.join(predefined_colors.keys())} or provide a valid hex code (e.g., `#FF5733`).",
                ephemeral=True,
            )
            return

        # If there's a title or description, create an embed
        if title or description:
            embed = discord.Embed(
                title=title if title else "",  # Use title if provided, otherwise ""
                description=description if description else "",  # Use description if provided, otherwise ""
                color=embed_color,
            )
            sent_message = await channel.send(embed=embed)  # Send the embed
        elif message:
            sent_message = await channel.send(message)  # Send just the message
        else:
            await interaction.response.send_message("Please provide a message or something for the embed!", ephemeral=True)
            return

        channel_link = channel.mention
        if interaction.guild:
            message_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}"
        else:
            message_link = ""
        message_sent_embed = discord.Embed(color=discord.Color.green())
        message_sent_embed.description = f"✅ Message has been sent to {channel_link}. You can view it [here]({message_link})."

        await interaction.response.send_message(embed=message_sent_embed, ephemeral=False)  # Send confirmation to user

    except discord.Forbidden:
        # Handle cases where the bot doesn't have permission to send messages in the channel
        await interaction.response.send_message(f"Oops! I don't have permission to send messages in {channel.mention}.", ephemeral=True)
        logging.info(f"[Permission error: I don't have permission to send messages in {channel.mention}.]")

    except discord.NotFound:
        # Handle cases where the specified channel doesn't exist
        await interaction.response.send_message(f"Hmm, I couldn't find the channel {channel.mention}.", ephemeral=True)
        logging.info(f"[Channel not found: {channel.mention}]")

    except Exception as e:
        # Handle any other unexpected errors
        await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)
        logging.info(f"[Error: {e}]")

#------- next bump -------
# Slash command to check when the next bump reminders will be sent
@client.tree.command(name="next_bump", description="Check when the next bump reminders will be sent", guild=GUILD_ID)
async def next_bump(interaction: discord.Interaction) -> None:
    try:
        current_time = time.monotonic()  # Use time.monotonic() for elapsed time

        # Calculate remaining time for the next ping reminder
        last_ping_time = interaction.client.bump["last_ping_time"]
        ping_interval = interaction.client.bump["ping_interval"]
        ping_remaining = max(0, ping_interval - (current_time - last_ping_time))
        ping_time_formatted = str(timedelta(seconds=int(ping_remaining)))

        # Calculate remaining time for the next normal reminder
        last_normal_time = interaction.client.bump["last_normal_message_time"]
        normal_interval = interaction.client.bump["normal_message_interval"]
        normal_remaining = max(0, normal_interval - (current_time - last_normal_time))
        normal_time_formatted = str(timedelta(seconds=int(normal_remaining)))

        # Create and send an embed with the reminder times
        next_bump = discord.Embed(
            title="Next Bump Reminders",
            color=discord.Color.orange()
        )
        next_bump.add_field(name="🔔 Ping Reminder (@Bumper)", value=f"In **{ping_time_formatted}**", inline=False)
        next_bump.add_field(name="💬 Normal Bump Reminder", value=f"In **{normal_time_formatted}**", inline=False)

        await interaction.response.send_message(embed=next_bump)
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong while checking bump timers: `{e}`", ephemeral=True)
       
#------------ uptime counter ----------
@client.tree.command(name="uptime", description="Shows how long the bot has been online", guild=GUILD_ID)
async def uptime(interaction: discord.Interaction):
    now = datetime.now(timezone.utc)  # ✅ Use timezone-aware UTC
    delta = now - interaction.client.start_time
    uptime_str = str(timedelta(seconds=int(delta.total_seconds())))

    uptime_embed = discord.Embed(
        title="🕒 Bot Uptime",
        description=f"The bot has been running for **{uptime_str}**",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=uptime_embed)

#-------- latency check --------
@client.tree.command(name="ping", description="Check the bot's latency", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    # Measure the start time
    start_time = time.perf_counter()

    # Send an initial response
    await interaction.response.send_message("🏓 Pong!")

    # Measure the end time after the response is sent
    end_time = time.perf_counter()

    # Calculate round-trip latency
    round_trip_latency = round((end_time - start_time) * 1000)  # Convert to milliseconds

    # WebSocket latency
    websocket_latency = round(client.latency * 1000, 2)  # Convert to milliseconds with 2 decimal places

    # Create the embed
    latency_embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.blue()
    )
    latency_embed.add_field(name="Discord Bot Latency", value=f"**{round_trip_latency}ms**", inline=False)
    latency_embed.add_field(name="Discord WebSocket Latency", value=f"**{websocket_latency}ms**", inline=False)

    # Send the embed as a follow-up message
    await interaction.followup.send(embed=latency_embed, ephemeral=True)

    
################ TOKEN #################
# Run the bot with the token from the .env file
# Handle invalid tokens or other errors gracefully
try:
    client.run(TOKEN)
except discord.LoginFailure:
    logging.info("[Invalid token. Please check your .env file.]")
except Exception as e:
    logging.info(f"[An error occurred: {e}]")