import discord
from discord import app_commands
from core.logging import logger

@app_commands.command(name="subscribe", description="Subscribe to That Random Blender Guy")
async def subscribe(interaction: discord.Interaction):
    subscribe_embed = discord.Embed(
        title="Subscribe Here",
        url="https://www.youtube.com/user/@thatrandomblenderguy?sub_confirmation=1",
        description="Click the link above to subscribe to That Random Blender Guy on YouTube!",
        color=discord.Color.red(),
    )
    subscribe_embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/1328989641684291597.webp?size=48&name=ThatRandomBlenderGuyLogo")
    await interaction.response.send_message(embed=subscribe_embed)
