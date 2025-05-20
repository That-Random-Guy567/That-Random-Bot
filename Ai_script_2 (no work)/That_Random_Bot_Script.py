import discord
from discord.ext import commands
import logging
from config import TOKEN, GUILD_SERVER_ID, BUMP_CONFIG
from utils import log
import asyncio
from datetime import datetime, timezone

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Intents
intents = discord.Intents.all()

class Client(commands.Bot):
    """
    Custom Discord bot client.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = datetime.now(timezone.utc)
        self.bump = BUMP_CONFIG
        self.posted_video_ids = set()
        self.first_run = True

    async def setup_hook(self):
        # Load extensions (cogs)
        await self.load_extension("modules.bump_loop")
        await self.load_extension("modules.youtube_loop")
        await self.load_extension("modules.moderation")
        await self.load_extension("modules.slash_commands")
        guild = discord.Object(id=GUILD_SERVER_ID)
        self.tree.copy_global_to(guild=guild)  # This copies the global commands to the specific guild.
        synced = await self.tree.sync(guild=guild)
        log(f"Synced {len(synced)} commands to guild {guild.id}")

    async def on_ready(self):
        log(f"[Logged on as {self.user}!]")

    async def on_message(self, message):
        await self.process_commands(message)
        if (
            message.author.bot and
            message.embeds and
            message.embeds[0].description and
            "Bump done" in message.embeds[0].description
        ):
            print("----------------------")
            log("[✅ Detected Disboard bump. Resetting timers and enabling reminders.]")

            now = asyncio.get_running_loop().time()
            self.bump["last_ping_time"] = now
            self.bump["last_normal_message_time"] = now
            self.bump["enabled"] = True  # Start the timers after bump
            self.bump["bump_count"] += 1
            log(f"[📈 Bump count: {self.bump['bump_count']}]")

            if self.bump["bump_count"] >= 12:
                bump_ping = self.bump["ping_role"]
                await message.channel.send(f"🎯 **Time to bump {bump_ping}!**")
                self.bump["bump_count"] = 0  # Reset the count

# Entry point
if __name__ == "__main__":
    client = Client(command_prefix="!", intents=intents)
    try:
        client.run(TOKEN)
    except discord.LoginFailure:
        log("[Invalid token. Please check your .env file.]", level="ERROR")
    except Exception as e:
        log(f"[An error occurred: {e}]", level="ERROR")
