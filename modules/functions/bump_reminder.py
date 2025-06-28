import asyncio
import discord
from discord.ext import tasks, commands
from core.logging import logger
from core.mongo import db
from constants import BUMP_CONFIG

BUMP_COLLECTION = db["bump_reminder"]

def load_bump_data():
    doc = BUMP_COLLECTION.find_one({"_id": "bump_state"})
    if doc:
        return {
            "enabled": doc.get("enabled", False),
            "last_normal_message_time": doc.get("last_normal_message_time", 0),
            "reminder_count": doc.get("reminder_count", 0)
        }
    return {"enabled": False, "last_normal_message_time": 0, "reminder_count": 0}

def save_bump_data(config):
    BUMP_COLLECTION.update_one(
        {"_id": "bump_state"},
        {"$set": {
            "enabled": config.enabled,
            "last_normal_message_time": config.last_normal_message_time,
            "reminder_count": config.reminder_count
        }},
        upsert=True
    )

class BumpReminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bump_config = BUMP_CONFIG
        # Load bump state from MongoDB
        bump_data = load_bump_data()
        self.bump_config.enabled = bump_data["enabled"]
        self.bump_config.last_normal_message_time = bump_data["last_normal_message_time"]
        self.bump_config.reminder_count = bump_data["reminder_count"]
        self.bump_reminder_loop.change_interval(seconds=self.bump_config.refresh_time)
        self.bump_reminder_loop.start()

    def cog_unload(self):
        self.bump_reminder_loop.cancel()

    @tasks.loop(seconds=BUMP_CONFIG.refresh_time)  # Default, will be changed in __init__
    async def bump_reminder_loop(self):
        if not self.bump_config.enabled:
            return

        now = asyncio.get_running_loop().time()

        if now - self.bump_config.last_normal_message_time > self.bump_config.normal_message_interval:
            self.bump_config.reminder_count += 1
            channel = self.bot.get_channel(self.bump_config.channel_id)
            if channel:
                if self.bump_config.reminder_count >= self.bump_config.ping_every_n_reminders:
                    bump_ping = self.bump_config.ping_role
                    await channel.send(f"🔔 **Time to bump the server {bump_ping}!** Don’t forget to use `/bump`.")
                    self.bump_config.reminder_count = 0
                else:
                    await channel.send("⏰ Just a friendly reminder: it's time to bump the server again!")
            self.bump_config.last_normal_message_time = now
            save_bump_data(self.bump_config)  # <-- Save after update

    @bump_reminder_loop.before_loop
    async def before_bump_reminder(self):
        await self.bot.wait_until_ready()
        logger.info("[BumpReminder Cog] Background loop starting.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.author.bot and
            message.embeds
        ):
            embed = message.embeds[0]
            title = embed.title or ""
            desc = embed.description or ""
            if title.lower() == "disboard: the public server list" and "bump done" in desc.lower():
                logger.info("[✅ Detected Disboard bump. Resetting timers and enabling reminders.]")
                now = asyncio.get_running_loop().time()
                self.bump_config.last_normal_message_time = now
                self.bump_config.enabled = True
                save_bump_data(self.bump_config)  # <-- Save after update

async def setup(bot: commands.Bot):
    await bot.add_cog(BumpReminder(bot))
    logger.info("[BumpReminder Cog] Loaded and ready.")