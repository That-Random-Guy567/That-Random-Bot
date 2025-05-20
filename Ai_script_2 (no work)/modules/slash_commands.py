import discord
from discord.ext import commands
from discord import app_commands
import time
from datetime import datetime, timezone, timedelta
from config import GUILD_SERVER_ID, BUMP_CONFIG

GUILD_ID = discord.Object(id=GUILD_SERVER_ID)

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="send", description="Sends a message to a specific channel", guild=GUILD_ID)
    @app_commands.describe(
        channel='The channel you want to send the message to.',
        message="The main message you want to send",
        title='The title of the embed',
        description='The description of the embed',
        color='The color of the embed (e.g., "blurple", "red", "green", or a hex code like #FF5733)',
    )
    async def send_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str = None,
        title: str = None,  # Make title optional
        description: str = None,  # Make description optional
        color: str = "blurple",  # Default to Discord blurple
    ):
        """Sends a message to a specified channel, with optional title, description, and color."""
        # Predefined color mapping
        predefined_colors = {
            "blurple": discord.Color.blurple(),
            "red": discord.Color.red(),
            "green": discord.Color.green(),
            "blue": discord.Color.blue(),
            "yellow": discord.Color.yellow(),
            "orange": discord.Color.orange(),
            "purple": discord.Color.purple(),
            "white": discord.Color.from_rgb(255, 255, 255),  # Custom white color
            "black": discord.Color.from_rgb(0, 0, 0),  # Custom black color
        }

        try:
            # Determine the embed color
            if color.lower() in predefined_colors:
                embed_color = predefined_colors[color.lower()]
            elif color.startswith("#") and len(color) == 7:  # Check if it's a hex code
                try:
                    # Convert hex to RGB and create a discord.Color
                    hex_color = int(color[1:], 16)  # Convert hex string to integer
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

            # If there's a title or description, create an embed
            if title or description:
                embed = discord.Embed(
                    title=title if title else "",  # Use title if provided, otherwise ""
                    description=description if description else "",  # Use description if provided, otherwise ""
                    color=embed_color,
                )
                sent_message = await channel.send(embed=embed)  # Send the embed
            elif message:
                sent_message = await channel.send(message)  # Send just the message
            else:
                await interaction.response.send_message("Please provide a message or something for the embed!", ephemeral=True)
                return

            channel_link = channel.mention
            if interaction.guild:
                message_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}"
            else:
                message_link = ""
            message_sent_embed = discord.Embed(color=discord.Color.green())
            message_sent_embed.description = f"✅ Message has been sent to {channel_link}. You can view it [here]({message_link})."

            await interaction.response.send_message(embed=message_sent_embed, ephemeral=False)  # Send confirmation to user

        except discord.Forbidden:
            # Handle cases where the bot doesn't have permission to send messages in the channel
            await interaction.response.send_message(f"Oops! I don't have permission to send messages in {channel.mention}.", ephemeral=True)
            #logging.info(f"[Permission error: I don't have permission to send messages in {channel.mention}.]") #removed logging

        except discord.NotFound:
            # Handle cases where the specified channel doesn't exist
            await interaction.response.send_message(f"Hmm, I couldn't find the channel {channel.mention}.", ephemeral=True)
            #logging.info(f"[Channel not found: {channel.mention}]") #removed logging

        except Exception as e:
            # Handle any other unexpected errors
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)
            #logging.info(f"[Error: {e}]") #removed logging

    @app_commands.command(name="next_bump", description="Check when the next bump reminders will be sent", guild=GUILD_ID)
    async def next_bump(self, interaction: discord.Interaction) -> None:
        """Checks and returns the time until the next bump reminders."""
        try:
            current_time = time.monotonic()  # Use time.monotonic() for elapsed time

            # Calculate remaining time for the next ping reminder
            last_ping_time = interaction.client.bump["last_ping_time"]
            ping_interval = interaction.client.bump["ping_interval"]
            ping_remaining = max(0, ping_interval - (current_time - last_ping_time))
            ping_time_formatted = str(timedelta(seconds=int(ping_remaining)))

            # Calculate remaining time for the next normal reminder
            last_normal_time = interaction.client.bump["last_normal_message_time"]
            normal_interval = interaction.client.bump["normal_message_interval"]
            normal_remaining = max(0, normal_interval - (current_time - last_normal_time))
            normal_time_formatted = str(timedelta(seconds=int(normal_remaining)))

            # Create and send an embed with the reminder times
            next_bump = discord.Embed(
                title="Next Bump Reminders",
                color=discord.Color.orange()
            )
            next_bump.add_field(name="🔔 Ping Reminder (@Bumper)", value=f"In **{ping_time_formatted}**", inline=False)
            next_bump.add_field(name="💬 Normal Bump Reminder", value=f"In **{normal_time_formatted}**", inline=False)

            await interaction.response.send_message(embed=next_bump)
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong while checking bump timers: `{e}`", ephemeral=True)

    @app_commands.command(name="uptime", description="Shows how long the bot has been online", guild=GUILD_ID)
    async def uptime(self, interaction: discord.Interaction):
        """Displays the bot's uptime."""
        now = datetime.now(timezone.utc)  # ✅ Use timezone-aware UTC
        delta = now - interaction.client.start_time
        uptime_str = str(timedelta(seconds=int(delta.total_seconds())))

        uptime_embed = discord.Embed(
            title="🕒 Bot Uptime",
            description=f"The bot has been running for **{uptime_str}**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=uptime_embed)

    @app_commands.command(name="ping", description="Check the bot's latency", guild=GUILD_ID)
    async def ping(self, interaction: discord.Interaction):
        """Checks and returns the bot's latency."""
        # Measure the start time
        start_time = time.perf_counter()

        # Send an initial response
        await interaction.response.send_message("🏓 Pong!")

        # Measure the end time after the response is sent
        end_time = time.perf_counter()

        # Calculate round-trip latency
        round_trip_latency = round((end_time - start_time) * 1000)  # Convert to milliseconds

        # WebSocket latency
        websocket_latency = round(self.bot.latency * 1000, 2)  # Convert to milliseconds with 2 decimal places

        # Create the embed
        latency_embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.blue()
        )
        latency_embed.add_field(name="Discord Bot Latency", value=f"**{round_trip_latency}ms**", inline=False)
        latency_embed.add_field(name="Discord WebSocket Latency", value=f"**{websocket_latency}ms**", inline=False)

        # Send the embed as a follow-up message
        await interaction.followup.send(embed=latency_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(SlashCommands(bot))
