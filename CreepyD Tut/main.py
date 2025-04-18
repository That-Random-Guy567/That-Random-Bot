# imports
import os
import discord
from discord.ext import commands
from discord import app_commands

# load .env file
from dotenv import load_dotenv

#------ Defining stuff -----
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

############    Main code  ###############
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!")

@bot.event
async def on_message(msg):
    if msg.author.id != bot.user.id:
        await msg.channel.send(f"Interesting message, {msg.author.mention}")

    else:
        print("Message has been sent successfully!")

@bot.tree.command(name="great", description="Sends a greeting to the user")
async def greet(interaction: discord.Interaction):
    username = interaction.user.mention
    await interaction.response.send_message(f"Hello there, {username}!")

# --------- Token ----------
bot.run(TOKEN)