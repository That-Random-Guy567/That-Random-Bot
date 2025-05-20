import discord
from discord import app_commands
from core.bot import Client
from core.logging import logger
from constants import GUILD_SERVER_ID  # Import the global ID from constants
from datetime import datetime, timezone, timedelta
import asyncio
import time
from modules import bump_reminder
from modules import games

@app_commands.guilds(discord.Object(id=GUILD_SERVER_ID))
class General(app_commands.Group):
    @app_commands.command(name="subscribe", description="Subscribe to That Random Blender Guy")
    async def subscribe(self, interaction: discord.Interaction):
        subscribe_embed = discord.Embed(
            title="Subscribe Here",
            url="https://www.youtube.com/user/@thatrandomblenderguy?sub_confirmation=1",
            description="Click the link above to subscribe to That Random Blender Guy on YouTube!",
            color=discord.Color.red(),
        )
        subscribe_embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1328989641684291597.webp?size=48&name=ThatRandomBlenderGuyLogo")
        await interaction.response.send_message(embed=subscribe_embed)

    @app_commands.command(name="send", description="Sends a message to a specific channel")
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
            message_sent_embed.description = f"\u2705 Message has been sent to {channel_link}. You can view it [here]({message_link})."

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

    @app_commands.command(name="next_bump", description="Check when the next bump reminders will be sent")
    async def next_bump(self, interaction: discord.Interaction) -> None:
        try:
            current_time = asyncio.get_running_loop().time()
            last_ping_time = bump_reminder.bump_config["last_ping_time"]
            ping_interval = bump_reminder.bump_config["ping_interval"]
            ping_remaining = max(0, ping_interval - (current_time - last_ping_time))
            ping_time_formatted = str(timedelta(seconds=int(ping_remaining)))

            last_normal_time = bump_reminder.bump_config["last_normal_message_time"]
            normal_interval = bump_reminder.bump_config["normal_message_interval"]
            normal_remaining = max(0, normal_interval - (current_time - last_normal_time))
            normal_time_formatted = str(timedelta(seconds=int(normal_remaining)))

            next_bump = discord.Embed(
                title="Next Bump Reminders",
                color=discord.Color.orange()
            )
            next_bump.add_field(name="\ud83d\udd14 Ping Reminder (@Bumper)", value=f"In **{ping_time_formatted}**", inline=False)
            next_bump.add_field(name="\ud83d\udcac Normal Bump Reminder", value=f"In **{normal_time_formatted}**", inline=False)

            await interaction.response.send_message(embed=next_bump)
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong while checking bump timers: `{e}`",
                                                    ephemeral=True)

    @app_commands.command(name="uptime", description="Shows how long the bot has been online")
    async def uptime(self, interaction: discord.Interaction):
        now = datetime.now(timezone.utc)
        delta = now - interaction.client.start_time
        uptime_str = str(timedelta(seconds=int(delta.total_seconds())))

        uptime_embed = discord.Embed(
            title="\ud83d\udd52 Bot Uptime",
            description=f"The bot has been running for **{uptime_str}**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=uptime_embed)

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        start_time = time.perf_counter()
        await interaction.response.send_message("\ud83c\udfd3 Pong!")
        end_time = time.perf_counter()
        round_trip_latency = round((end_time - start_time) * 1000)
        websocket_latency = round(interaction.client.latency * 1000, 2)
        latency_embed = discord.Embed(
            title="\ud83c\udfd3 Pong!",
            color=discord.Color.blue()
        )
        latency_embed.add_field(name="Discord Bot Latency", value=f"**{round_trip_latency}ms**", inline=False)
        latency_embed.add_field(name="Discord WebSocket Latency", value=f"**{websocket_latency}ms**", inline=False)
        await interaction.followup.send(embed=latency_embed, ephemeral=True)

class Games(app_commands.Group):
    @app_commands.command(name="setgame", description="Set the game type (yo/count) and channel")
    @app_commands.describe(game="The game to play", channel="Channel to play the game in")
    async def setgame(self, interaction: discord.Interaction, game: str, channel: discord.TextChannel):
        if game not in ("yo", "count"):
            await interaction.response.send_message("Game must be 'yo' or 'count'.", ephemeral=True)
            return
        await games.set_game_channel(game, channel)
        await interaction.response.send_message(f"Set {game} game to channel {channel.mention}.")

    @app_commands.command(name="autocreate_offender_role", description="Auto-create the O-Offender role for the game")
    @app_commands.describe(game="The game to assign the O-Offender role for")
    async def autocreate_offender_role(self, interaction: discord.Interaction, game: str):
        role = await games.create_offender_role(interaction.guild)
        if role:
            await games.set_offender_role(game, role)
            await interaction.response.send_message(f"Created and attached {role.mention} as O-Offender for {game} game.")
        else:
            await interaction.response.send_message("Could not create role (permission issue).", ephemeral=True)

    @app_commands.command(name="attach_offender_role", description="Attach an existing role as O-Offender")
    @app_commands.describe(game="The game to assign the O-Offender role for", role="The role to use")
    async def attach_offender_role(self, interaction: discord.Interaction, game: str, role: discord.Role):
        await games.set_offender_role(game, role)
        await interaction.response.send_message(f"Attached {role.mention} as O-Offender for {game} game.")

async def setup_slash_commands(bot: Client):
    bot.tree.add_command(General())
    bot.tree.add_command(Games())