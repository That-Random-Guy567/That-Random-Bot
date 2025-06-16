import discord
from discord import app_commands
import asyncio
from datetime import timedelta
from core.logging import logger
from modules import bump_reminder

#---------------- Next Bump Command ----------------
@app_commands.command(name="next_bump", description="Check when the next bump reminders will be sent")
async def next_bump(interaction: discord.Interaction) -> None:
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
        next_bump.add_field(name="🔔 Ping Reminder (@Bumper)", value=f"In **{ping_time_formatted}**", inline=False)
        next_bump.add_field(name="💬 Normal Bump Reminder", value=f"In **{normal_time_formatted}**", inline=False)

        await interaction.response.send_message(embed=next_bump)
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong while checking bump timers: `{e}`",ephemeral=True)