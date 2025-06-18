import discord
from discord import app_commands
from core.logging import logger
from constants import EMOJIS

@app_commands.command(name="help", description="Display all available slash commands")
async def help(interaction: discord.Interaction):
    help_embed = discord.Embed(
        title=f"That Random Bot {EMOJIS['BOT_PFP']} Commands",
        description="**Bot Commands**\nList of available slash commands:",
        color=discord.Color.yellow()
    )
    help_embed.add_field(name="/subscribe", value="Advertise @thatrandomblenderguy Socials", inline=False)
    help_embed.add_field(name="/send_command", value="Send stuff using the bot. (Only available for ADMIN)", inline=False)
    help_embed.add_field(name="/next_bump", value="Shows when the next bump will be, and when to ping users.", inline=False)
    help_embed.add_field(name="/uptime", value="Shows Bot Uptime", inline=False)
    help_embed.add_field(name="/ping", value="Shows Bot Latency", inline=False)
    help_embed.add_field(name="/count", value="Shows the current number up to in #bots", inline=False)
    help_embed.add_field(name="/ticket", value="Send Ticket Control Panel. (Only available for admin)", inline=False)
    help_embed.add_field(name="/help", value="Displays all available slash commands with descriptions", inline=False)
 
    help_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1381571795185832117.webp?size=48&name=bot_pfp")

    await interaction.response.send_message(embed=help_embed)