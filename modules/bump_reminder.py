import asyncio
import discord
from discord.ext import tasks, commands
from core.logging import logger
from constants import BUMP_CONFIG, BUMP_TIME_INTERVAL

class BumpReminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bump_config = BUMP_CONFIG.copy()
        self.bump_reminder_loop.start()

    def cog_unload(self):
        self.bump_reminder_loop.cancel()

    @tasks.loop(seconds=BUMP_TIME_INTERVAL)
    async def bump_reminder_loop(self):
        if not self.bump_config.get("enabled", False):
            return

        now = asyncio.get_running_loop().time()

        if now - self.bump_config.get("last_normal_message_time", 0) > self.bump_config.get("normal_message_interval", 0):
            self.bump_config["reminder_count"] = self.bump_config.get("reminder_count", 0) + 1
            channel = self.bot.get_channel(self.bump_config.get("channel_id"))
            if channel:
                if self.bump_config["reminder_count"] >= self.bump_config.get("ping_every_n_reminders", 3):
                    bump_ping = self.bump_config.get("ping_role", "@everyone")
                    await channel.send(f"🔔 **Time to bump the server {bump_ping}!** Don’t forget to use `/bump`.")
                    self.bump_config["reminder_count"] = 0
                else:
                    await channel.send("⏰ Just a friendly reminder: it's time to bump the server again!")
            self.bump_config["last_normal_message_time"] = now

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
                self.bump_config["last_normal_message_time"] = now
                self.bump_config["enabled"] = True

                print("###########################")

async def setup(bot: commands.Bot):
    await bot.add_cog(BumpReminder(bot))
    logger.info("[BumpReminder Cog] Loaded and ready.")