# modules/bump_reminder.py
import asyncio
import discord
from discord.ext import tasks
from core.bot import Client
from core.logging import logger
from constants import BUMP_CONFIG

# Globals
bump_config = BUMP_CONFIG.copy()  # Create a copy to avoid unintended modifications

# Loop to send bump reminders at regular intervals
@tasks.loop(seconds=60)  # Check every 60 seconds
async def bump_reminder_loop(bot: Client, channel: discord.TextChannel):
    if not bump_config["enabled"]:
        return  # Exit if not enabled

    now = asyncio.get_running_loop().time()

    # Check if it's time to send a ping reminder
    if now - bump_config["last_ping_time"] > bump_config["ping_interval"]:
        bump_ping = bump_config["ping_role"]
        await channel.send(f"🔔 **Time to bump the server {bump_ping}!** Don’t forget to use `/bump`.")
        bump_config["last_ping_time"] = now

    # Check if it's time to send a normal reminder
    elif now - bump_config["last_normal_message_time"] > bump_config["normal_message_interval"]:
        await channel.send("⏰ Just a friendly reminder: it's time to bump the server again!")
        bump_config["last_normal_message_time"] = now

async def setup_bump_reminder(bot: Client):
    channel = bot.get_channel(bump_config["channel_id"])
    if channel is None:
        logger.error("[Bump reminder channel not found.]")
        return
    bump_reminder_loop.start(bot, channel)

async def on_message(bot: Client, message: discord.Message):
    if (
            message.author.bot and
            message.embeds and
            message.embeds[0].description and
            "Bump done" in message.embeds[0].description
    ):
        logger.info("[✅ Detected Disboard bump. Resetting timers and enabling reminders.]")
        now = asyncio.get_running_loop().time()
        bump_config["last_ping_time"] = now
        bump_config["last_normal_message_time"] = now
        bump_config["enabled"] = True  # Start the timers after bump
        bump_config["bump_count"] += 1
        logger.info(f"[📈 Bump count: {bump_config['bump_count']}]")

        if bump_config["bump_count"] >= 12:
            bump_ping = bump_config["ping_role"]
            await message.channel.send(f"🎯 **Time to bump {bump_ping}!**")
            bump_config["bump_count"] = 0  # Reset the count

        print("###########################")
