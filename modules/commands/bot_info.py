import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import time
from core.logging import logger
import psutil

#---------------- Ping Command ----------------
@app_commands.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    """Responds with the bot's WebSocket and REST API latency."""
    # Measure REST API latency
    rest_start = time.perf_counter()
    await interaction.response.send_message("🏓 Pong!", ephemeral=True)
    rest_end = time.perf_counter()
    rest_latency = round((rest_end - rest_start) * 1000)

    # WebSocket latency
    ws_latency = round(interaction.client.latency * 1000)

    ping_embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.blurple(),
        description=(
            "Here are the current latency stats:\n\n"
            "**WebSocket latency** measures the real-time connection delay between the bot and Discord (event delivery).\n"
            "**REST API latency** measures how fast the bot can send a request (like sending a message) to Discord's servers."
        )
    )
    ping_embed.add_field(name="WebSocket Latency", value=f"**{ws_latency}ms**", inline=True)
    ping_embed.add_field(name="REST API Latency", value=f"**{rest_latency}ms**", inline=True)

    await interaction.followup.send(embed=ping_embed)

#---------------- Uptime Command ----------------
@app_commands.command(name="uptime", description="Shows how long the bot has been online")
async def uptime(interaction: discord.Interaction):
    now = datetime.now(timezone.utc)
    delta = now - interaction.client.start_time # Access start_time from interaction.client
    uptime_str = str(timedelta(seconds=int(delta.total_seconds())))

    uptime_embed = discord.Embed(
        title="🕒 Bot Uptime",
        description=f"The bot has been running for **{uptime_str}**",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=uptime_embed)


#---------------- Resource Usage Command ----------------
@app_commands.command(name="resources", description="Shows the bot's current CPU and RAM usage")
async def resources(interaction: discord.Interaction):
    """
    Responds with the bot's current CPU and RAM usage.
    """
    process = psutil.Process()
    cpu_percent = process.cpu_percent(interval=0.5)
    mem_info = process.memory_info()
    ram_mb = mem_info.rss / 1024 / 1024  # Convert bytes to MB

    resource_embed = discord.Embed(
        title="🖥️ Bot Resource Usage",
        color=discord.Color.gold(),
        description=(
            f"**CPU Usage:** {cpu_percent:.2f}%\n"
            f"**RAM Usage:** {ram_mb:.2f} MB"
        )
    )
    await interaction.response.send_message(embed=resource_embed)

#---------------- Send Command ----------------
@app_commands.command(name="send", description="Sends a message to a specific channel")
@app_commands.describe(
    channel='The channel you want to send the message to.',
    message="The main message you want to send",
    title='The title of the embed',
    description='The description of the embed',
    color='The color of the embed (e.g., "blurple", "red", "green", or a hex code like #FF5733)',
)
async def send_command(
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str = None,
        title: str = None,
        description: str = None,
        color: str = "blurple",
):
    predefined_colors = {
        "blurple": discord.Color.blurple(),
        "red": discord.Color.red(),
        "green": discord.Color.green(),
        "blue": discord.Color.blue(),
        "yellow": discord.Color.yellow(),
        "orange": discord.Color.orange(),
        "purple": discord.Color.purple(),
        "white": discord.Color.from_rgb(255, 255, 255),
        "black": discord.Color.from_rgb(0, 0, 0),
    }

    try:
        if color.lower() in predefined_colors:
            embed_color = predefined_colors[color.lower()]
        elif color.startswith("#") and len(color) == 7:
            try:
                hex_color = int(color[1:], 16)
                embed_color = discord.Color(hex_color)
            except ValueError:
                await interaction.response.send_message(
                    "Invalid hex color code. Please use a valid hex code (e.g., `#FF5733`).",
                    ephemeral=True,
                )
                return
        else:
            await interaction.response.send_message(
                f"Invalid color. Please choose from: {', '.join(predefined_colors.keys())} or provide a valid hex code (e.g., `#FF5733`).",
                ephemeral=True,
            )
            return

        if title or description:
            embed = discord.Embed(
                title=title if title else "",
                description=description if description else "",
                color=embed_color,
            )
            sent_message = await channel.send(embed=embed)
        elif message:
            sent_message = await channel.send(message)
        else:
            await interaction.response.send_message("Please provide a message or something for the embed!",
                                                    ephemeral=True)
            return

        channel_link = channel.mention
        if interaction.guild:
            message_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}"
        else:
            message_link = ""
        message_sent_embed = discord.Embed(color=discord.Color.green())
        message_sent_embed.description = f"✅ Message has been sent to {channel_link}. You can view it [here]({message_link})."

        await interaction.response.send_message(embed=message_sent_embed, ephemeral=False)

    except discord.Forbidden:
        await interaction.response.send_message(
            f"Oops! I don't have permission to send messages in {channel.mention}.", ephemeral=True)
        logger.error(f"[Permission error: I don't have permission to send messages in {channel.mention}.]")

    except discord.NotFound:
        await interaction.response.send_message(f"Hmm, I couldn't find the channel {channel.mention}.", ephemeral=True)
        logger.error(f"[Channel not found: {channel.mention}]")

    except Exception as e:
        await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)
        logger.error(f"[Error: {e}]")