import discord
from discord.ext import commands
from datetime import timedelta

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command()
    async def uptime(self, ctx):
        now = discord.utils.utcnow()
        delta = now - self.bot.start_time
        await ctx.send(f"Uptime: {str(timedelta(seconds=int(delta.total_seconds())))}")