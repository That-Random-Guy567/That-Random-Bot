# modules/youtube_loop.py
import feedparser
import asyncio
import discord
from discord.ext import tasks
from datetime import datetime
from core.bot import Client
from core.logging import logger
from constants import YOUTUBE_CONFIG
import time

# Helper function for logging with timestamp
def log(msg, level="LOG"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{level}] [{now}] {msg}")

@tasks.loop(minutes=60)
async def youtube_upload_loop(bot: Client):
    log("Checking YouTube feed...")
    try:
        # Add a nocache parameter to bypass caching
        feed_url_with_cache_bypass = f"{YOUTUBE_CONFIG['FEED_URL']}&nocache={int(time.time())}"
        # Parse the YouTube feed
        feed = feedparser.parse(feed_url_with_cache_bypass)

        if feed.entries:
            latest_video = feed.entries[0]
            log(f"Latest video entry: {latest_video.title}")

            # Check if the video ID exists in the feed entry
            if hasattr(latest_video, 'yt_videoid'):
                video_id = latest_video.yt_videoid
                log(f"Video ID found: {video_id}")
            else:
                log("No video ID found in the latest feed entry.", level="ERROR")
                return

            # Skip the first video on startup to avoid duplicate alerts
            if bot.first_run:
                log(f"Skipping first video (startup): {video_id}")
                bot.posted_video_ids.add(video_id)
                bot.first_run = False
            elif video_id not in bot.posted_video_ids:
                # Send a notification for new videos
                channel = bot.get_channel(YOUTUBE_CONFIG["UPLOAD_CHANNEL_ID"])
                forum_channel = bot.get_channel(YOUTUBE_CONFIG["FORUM_CHANNEL_ID"])  # Forum channel ID
                video_url = f"https://youtu.be/{video_id}"

                if channel:
                    # Send the announcement in the main channel
                    await channel.send(
                        f"{YOUTUBE_CONFIG['UPLOAD_PING_ROLE']} New video just dropped! 🎬\n{video_url}")
                    log(f"New video uploaded: {video_url}")

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
                    log(
                        f"Forum post created for video: {latest_video.title} with tag: {tag_to_apply.name if tag_to_apply else 'None'}")
                else:
                    log(
                        f"Could not find forum channel ID {YOUTUBE_CONFIG['FORUM_CHANNEL_ID']} or it is not a ForumChannel.",
                        level="ERROR")
                bot.posted_video_ids.add(video_id)
            else:
                log(f"Video already posted: {video_id}")
        else:
            log("No entries found in the feed.")
    except Exception as e:
        log(f"Error checking YouTube feed: {e}", level="ERROR")
        await asyncio.sleep(60)

async def setup_youtube_loop(bot: Client):
    youtube_upload_loop.start(bot)

@youtube_upload_loop.before_loop
async def before_youtube_upload_loop():
    await Client.wait_until_ready()  # Use Client here, assuming it's meant to be called before the loop.
    log("Bot is ready. Starting YouTube upload loop.")
