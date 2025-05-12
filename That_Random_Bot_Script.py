import discord
from discord.ext import commands
from config.settings import TOKEN, GUILD_ID
from cogs.bump_reminder import BumpReminder
from cogs.youtube import YouTubeCog
from cogs.moderation import Moderation
from cogs.utility import Utility

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.start_time = None

    async def setup_hook(self):
        self.start_time = discord.utils.utcnow()
        await self.add_cog(BumpReminder(self))
        await self.add_cog(YouTubeCog(self))
        await self.add_cog(Moderation(self))
        await self.add_cog(Utility(self))

    async def on_ready(self):
        print(f"Logged in as {self.user}")

if __name__ == "__main__":
    bot = Bot()
    bot.run(TOKEN)