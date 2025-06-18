import discord
from discord import app_commands
import asyncio
from datetime import timedelta
from core.logging import logger
from constants import BUMP_CONFIG

@app_commands.command(name="next_bump", description="Check when the next bump reminders will be sent")
async def next_bump(interaction: discord.Interaction) -> None:
    try:
        bump_cog = interaction.client.get_cog("BumpReminder")
        if bump_cog is None:
            await interaction.response.send_message("BumpReminder Cog is not loaded.", ephemeral=True)
            return

        current_time = asyncio.get_running_loop().time()

        last_normal_time = bump_cog.bump_config.get("last_normal_message_time", 0)
        normal_interval = bump_cog.bump_config.get("normal_message_interval", 0)
        normal_remaining = max(0, normal_interval - (current_time - last_normal_time))
        normal_time_formatted = str(timedelta(seconds=int(normal_remaining)))

        next_bump_embed = discord.Embed(
            title="Next Bump Reminders",
            color=discord.Color.orange()
        )
        next_bump_embed.add_field(name="💬 Normal Bump Reminder", value=f"In **{normal_time_formatted}**", inline=False)

        # Add time remaining until next /bump is available (assumed 2 hours after last normal reminder)
        bump_interval = bump_cog.bump_config.get("normal_message_interval", 7200)
        last_bump_time = bump_cog.bump_config.get("last_normal_message_time", 0)
        bump_remaining = max(0, bump_interval - (current_time - last_bump_time))
        bump_time_formatted = str(timedelta(seconds=int(bump_remaining)))
        next_bump_embed.add_field(name="⬆️ Next Bump", value=f"In **{bump_time_formatted}**", inline=False)

        await interaction.response.send_message(embed=next_bump_embed)
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong while checking bump timers: `{e}`", ephemeral=True)

@app_commands.command(name="send_bump_data", description="Send bump tests to channel to test bot.")
async def send_bump_cmd(interaction: discord.Interaction):
    bump_embed_tests = discord.Embed(
        title="DISBOARD: The Public Server List",
        description="Bump done!",
        color=discord.Color.red(),
    )
    bump_embed_tests.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/1328989641684291597.webp?size=48&name=ThatRandomBlenderGuyLogo")
    await interaction.response.send_message(embed=bump_embed_tests)