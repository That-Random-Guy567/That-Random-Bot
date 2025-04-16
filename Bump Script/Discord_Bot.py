import asyncio
import os
from discord.ext import commands
import discord
#from keep_alive import keep_alive

TOKEN = "MTM1NzI3OTczMzQ4OTg2NDgxNg.GtGRZp.nftB2Orw0PxZ8uZhCjED1Ox53T1dpTBKUFeoI4"
CHANNEL_ID = 1345373029626023999  # channel id (edit this for other servers)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# We'll keep track of when to send which type of message
last_ping_time = 0
ping_interval = 10 * 60 * 60  # 10 hours in seconds
normal_message_interval = 2.5 * 60 * 60  # 2.5 hours in seconds
last_normal_message_time = 0


@bot.event
async def on_ready():
    global last_ping_time, last_normal_message_time
    print(f"Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found.")
        return
    last_ping_time = asyncio.get_event_loop().time()
    last_normal_message_time = asyncio.get_event_loop().time()
    while True:
        await bump_reminder(channel)
        await asyncio.sleep(60)  # Check every minute


async def bump_reminder(channel):
    global last_ping_time, last_normal_message_time
    current_time = asyncio.get_event_loop().time()
    role = discord.utils.get(channel.guild.roles,
                             name="Bumper")  # find the @bump role

    if current_time - last_ping_time >= ping_interval:
        if role:
            await channel.send(f"{role.mention}, Time to bump!")  # do @bump
            print("Bump reminder (with ping) sent.")
        else:
            print("Bump role not found for ping.")
        last_ping_time = current_time

    elif current_time - last_normal_message_time >= normal_message_interval:
        await channel.send("Time to bump!")  # normal message
        print("Normal bump reminder sent.")
        last_normal_message_time = current_time


# keep_alive()  # secret hack to get 24/7 on replit
bot.run(TOKEN)
