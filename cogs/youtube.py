import discord
from discord.ext import commands, tasks
import feedparser
import time
import asyncio
from datetime import datetime
from config.constants import YOUTUBE_CONFIG  # Import the YouTube configuration dictionary

class YouTubeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feed_url = YOUTUBE_CONFIG["FEED_URL"]  # Access the feed URL from the dictionary
        self.posted_video_ids = set()
        self.first_run = True
        self.youtube_upload_channel_id = YOUTUBE_CONFIG["UPLOAD_CHANNEL_ID"]  # Access the upload channel ID
        self.youtube_forum_channel_id = YOUTUBE_CONFIG["FORUM_CHANNEL_ID"]  # Access the forum channel ID
        self.youtube_upload_ping_role = YOUTUBE_CONFIG["UPLOAD_PING_ROLE"]  # Access the ping role

    @tasks.loop(minutes=60)
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
                    channel = self.bot.get_channel(self.youtube_upload_channel_id)
                    forum_channel = self.bot.get_channel(self.youtube_forum_channel_id)  # Forum channel ID
                    video_url = f"https://youtu.be/{video_id}"

                    if channel:
                        # Send the announcement in the main channel
                        await channel.send(
                            f"{self.youtube_upload_ping_role} New video just dropped! 🎬\n{video_url}")
                        self.log(f"New video uploaded: {video_url}")

                    # Create a forum post for the video
                    if forum_channel and isinstance(forum_channel, discord.ForumChannel):
                        # Determine the tag to apply based on the presence of '#' in the title
                        tag_to_apply = None
                        if "#" in latest_video.title:  # Check if the title contains a '#'
                            tag_to_apply = next(
                                (tag for tag in forum_channel.available_tags if tag.name.lower() == "shorts"),
                                None)
                        else:
                            tag_to_apply = next(
                                (tag for tag in forum_channel.available_tags if tag.name.lower() == "video"),
                                None)

                        # Create the thread with the appropriate tag
                        forum_post = await forum_channel.create_thread(
                            name=latest_video.title,  # Use the video title as the post title
                            content=f"🎥 **{latest_video.title}**\n{video_url}",  # Use the video link as the post content
                            applied_tags=[tag_to_apply] if tag_to_apply else []  # Apply the tag if found
                        )
                        self.log(
                            f"Forum post created for video: {latest_video.title} with tag: {tag_to_apply.name if tag_to_apply else 'None'}")
                    else:
                        self.log(
                            f"Could not find forum channel ID {self.youtube_forum_channel_id} or it is not a ForumChannel.",
                            level="ERROR")
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
        await self.bot.wait_until_ready()
        self.log("Bot is ready. Starting YouTube upload loop.")

    # Helper function for logging with timestamp
    def log(self, msg, level="LOG"):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{level}] [{now}] {msg}")