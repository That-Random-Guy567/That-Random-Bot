import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import time
from core.logging import logger

#---------------- Ping Command ----------------
@app_commands.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    start_time = time.perf_counter()

    # Respond quickly
    await interaction.response.send_message("🏓 Measuring latency...", ephemeral=True)
    end_time = time.perf_counter()
    rest_latency = round((end_time - start_time) * 1000)

    # WebSocket latency
    ws_latency = round(interaction.client.latency * 1000)

    # Typing latency (simulate a lightweight delay)
    typing_start = time.perf_counter()
    try:
        async with interaction.channel.typing():
            pass
    except Exception:
        pass  # Some channels might not allow typing
    typing_latency = round((time.perf_counter() - typing_start) * 1000)

    # Build latency embed
    embed = discord.Embed(
        title="🏓 Pong!",
        description="Latency stats for the bot.",
        color=discord.Color.blue()
    )

    embed.add_field(name="🟢 WebSocket", value=f"**{ws_latency}ms**", inline=True)
    embed.add_field(name="🔵 REST API", value=f"**{rest_latency}ms**", inline=True)
    embed.add_field(name="🟣 Typing Indicator", value=f"**{typing_latency}ms**", inline=True)

    embed.set_footer(text="🟢 Ping from servers| 🔵 Message Delay | 🟣 Typing Indicator Ping")
    await interaction.followup.send(embed=embed)

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