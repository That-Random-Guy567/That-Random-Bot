import discord
from discord.ext import commands, tasks
import time
from config.constants import BUMP_CONFIG

class BumpReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Create a local copy of the BUMP_CONFIG to avoid modifying the original
        self.bump = BUMP_CONFIG.copy()

    @tasks.loop(seconds=60)
    async def bump_reminder_loop(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.bump["channel_id"])
        if not channel:
            return

        now = time.monotonic()
        if self.bump["enabled"]:
            if now - self.bump["last_ping_time"] > self.bump["ping_interval"]:
                await channel.send(
                    f"{self.bump['ping_role']} 🔔 Time to bump the server! Don’t forget to use `/bump`."
                )
                self.bump["last_ping_time"] = now
            elif now - self.bump["last_normal_message_time"] > self.bump["normal_message_interval"]:
                await channel.send(
                    f"{self.bump['ping_role']} ⏰ Just a friendly reminder: it's time to bump the server again!"
                )
                self.bump["last_normal_message_time"] = now

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot and "Bump done" in (message.embeds[0].description if message.embeds else ""):
            now = time.monotonic()
            self.bump["last_ping_time"] = now
            self.bump["last_normal_message_time"] = now
            self.bump["enabled"] = True
            self.bump["bump_count"] += 1

            if self.bump["bump_count"] >= 12:
                channel = self.bot.get_channel(self.bump["channel_id"])
                if channel:
                    await channel.send(f"{self.bump['ping_role']} 🎯 Time to bump!")
                self.bump["bump_count"] = 0