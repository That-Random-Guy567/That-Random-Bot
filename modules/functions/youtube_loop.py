import feedparser
import asyncio
import discord
from discord.ext import tasks
import time
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.bot import Client

from core.logging import logger
from constants import YOUTUBE_CONFIG
from core.mongo import db

logger.info(f"Using time interval: {YOUTUBE_CONFIG.TIME_INTERVAL} minute(s)")

YOUTUBE_POSTED_COLLECTION = db["youtube_posted_videos"]

def load_posted_video_ids():
    """Load posted video IDs from MongoDB."""
    return set(doc["video_id"] for doc in YOUTUBE_POSTED_COLLECTION.find())

def save_posted_video_id(video_id):
    """Save a new posted video ID to MongoDB."""
    YOUTUBE_POSTED_COLLECTION.update_one(
        {"video_id": video_id},
        {"$set": {"video_id": video_id}},
        upsert=True
    )

@tasks.loop(minutes=YOUTUBE_CONFIG.TIME_INTERVAL)
async def youtube_upload_loop(bot: "Client"):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.print_separator()
    logger.info(f"YouTube loop iteration starting at {current_time}")
    try:
        # Add a nocache parameter to bypass caching
        feed_url_with_cache_bypass = f"{YOUTUBE_CONFIG.FEED_URL}&nocache={int(time.time())}"
        logger.info("Attempting to fetch YouTube feed...")
        # Parse the YouTube feed
        feed = feedparser.parse(feed_url_with_cache_bypass)

        if feed.entries:
            latest_video = feed.entries[0]
            logger.info(f"Latest video entry: {latest_video.title}")

            # Check if the video ID exists in the feed entry
            if hasattr(latest_video, 'yt_videoid'):
                video_id = latest_video.yt_videoid
                logger.info(f"Video ID found: {video_id}")
            else:
                logger.error("No video ID found in the latest feed entry.")
                return

            # Skip the first video on startup to avoid duplicate alerts
            if bot.first_run:
                logger.info(f"Skipping first video (startup): {video_id}")
                bot.posted_video_ids.add(video_id)
                bot.first_run = False
            elif video_id not in bot.posted_video_ids:
                # Send a notification for new videos
                channel = bot.get_channel(YOUTUBE_CONFIG.UPLOAD_CHANNEL_ID)
                forum_channel = bot.get_channel(YOUTUBE_CONFIG.FORUM_CHANNEL_ID)
                video_url = f"https://youtu.be/{video_id}"

                if channel:
                    # Send the announcement in the main channel
                    await channel.send(
                        f"{YOUTUBE_CONFIG.UPLOAD_PING_ROLE} New video just dropped! 🎬\n{video_url}")
                    logger.info(f"New video uploaded: {video_url}")

                # Create a forum post for the video
                if forum_channel and isinstance(forum_channel, discord.ForumChannel):
                    # Determine the tag to apply based on the presence of '#' in the title
                    tag_to_apply = None
                    if "#" in latest_video.title:
                        tag_to_apply = next(
                            (tag for tag in forum_channel.available_tags if tag.name.lower() == "shorts"),
                            None)
                    else:
                        tag_to_apply = next(
                            (tag for tag in forum_channel.available_tags if tag.name.lower() == "video"),
                            None)

                    # Create the thread with the appropriate tag
                    forum_post = await forum_channel.create_thread(
                        name=latest_video.title,
                        content=f"🎥 **{latest_video.title}**\n{video_url}",
                        applied_tags=[tag_to_apply] if tag_to_apply else []
                    )
                    logger.info(f"Forum post created for video: {latest_video.title} with tag: {tag_to_apply.name if tag_to_apply else 'None'}")
                else:
                    logger.error(f"Could not find forum channel ID {YOUTUBE_CONFIG.FORUM_CHANNEL_ID} or it is not a ForumChannel.")
                bot.posted_video_ids.add(video_id)
                save_posted_video_id(video_id)
            else:
                logger.info(f"Video already posted: {video_id}")
        else:
            logger.info("No entries found in the feed.")
    except Exception as e:
        logger.error(f"Error checking YouTube feed: {e}")
        await asyncio.sleep(60)

_bot_instance = None #global var to store bot instance

async def setup_youtube_loop(bot: "Client"):
    """Setup and start the YouTube loop."""
    try:
        global _bot_instance
        _bot_instance = bot  # Store bot instance for before_loop
        logger.info("Initializing YouTube loop...")
        # Make sure bot attributes are set
        if not hasattr(bot, 'first_run'):
            bot.first_run = True
        # Load posted video IDs from MongoDB
        bot.posted_video_ids = load_posted_video_ids()
        logger.info(f"Loaded posted video IDs from database: {bot.posted_video_ids}")
            
        # Start the loop
        if not youtube_upload_loop.is_running():
            youtube_upload_loop.start(bot)
            logger.info(f"YouTube loop started with {YOUTUBE_CONFIG.TIME_INTERVAL} minute interval")
        else:
            logger.warning("YouTube loop was already running")
            
    except Exception as e:
        logger.error(f"Failed to start YouTube loop: {e}", exc_info=True)
        raise

@youtube_upload_loop.before_loop
async def before_youtube_upload_loop():
    """Wait for bot to be ready before starting the loop."""
    try:
        logger.info("Waiting for bot to be ready before starting YouTube loop...")
        global _bot_instance
        if _bot_instance:
            await _bot_instance.wait_until_ready()
            logger.info("Bot is ready, YouTube loop can start now")
        else:
            raise RuntimeError("Bot instance not available")
    except Exception as e:
        logger.error(f"Error in YouTube loop startup: {e}", exc_info=True)
        raise