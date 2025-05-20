import asyncio
import time
from discord.ext import commands
from datetime import timedelta
from utils import log
from config import BUMP_CONFIG

async def bump_reminder_loop(bot: commands.Bot):
    """Loop to send bump reminders at regular intervals."""
    await bot.wait_until_ready()
    channel = bot.get_channel(BUMP_CONFIG["channel_id"])
    if channel is None:
        log("[Bump reminder channel not found.]", level="ERROR")
        return

    while not bot.is_closed():
        if not bot.bump.get("enabled", False):
            await asyncio.sleep(60)
            continue

        now = time.monotonic()

        if now - bot.bump["last_ping_time"] > bot.bump["ping_interval"]:
            bump_ping = BUMP_CONFIG["ping_role"]
            await channel.send(f"🔔 **Time to bump the server {bump_ping}!** Don't forget to use `/bump`.")
            bot.bump["last_ping_time"] = now

        elif now - bot.bump["last_normal_message_time"] > bot.bump["normal_message_interval"]:
            await channel.send("⏰ Just a friendly reminder: it's time to bump the server again!")
            bot.bump["last_normal_message_time"] = now

        await asyncio.sleep(60)

def setup(bot):
    bot.loop.create_task(bump_reminder_loop(bot))
