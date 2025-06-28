import discord
from discord import app_commands
from core.logging import logger
from modules.functions.counting import load_count_data
from constants import COUNTING_CHANNEL_ID

#---------------- Counting Channel Command ----------------
@app_commands.command(name="count", description="Shows the current count in the counting channel")
async def count(interaction: discord.Interaction):
    """Shows the current count in the counting channel"""
    try:
        # Get the count data for the counting channel
        chan_id = str(COUNTING_CHANNEL_ID)
        # Always load the latest data from MongoDB
        data = load_count_data().get(chan_id, {"last_count": 0, "last_user": None})
        current_count = data["last_count"]
        last_counter = data["last_user"]

        # Create embed
        count_embed = discord.Embed(
            title="🔢 Current Count",
            color=discord.Color.blue()
        )
        
        # Add count field
        count_embed.add_field(
            name="Current Number", 
            value=f"**{current_count}**",
            inline=False
        )

        # Add last counter if there is one
        if last_counter:
            last_counter_user = interaction.guild.get_member(last_counter)
            counter_name = last_counter_user.display_name if last_counter_user else "Unknown User"
            count_embed.add_field(
                name="Last Counter",
                value=f"**{counter_name}**",
                inline=False
            )

        await interaction.response.send_message(embed=count_embed)
        logger.info(f"Count command used - Current count: {current_count}")

    except Exception as e:
        await interaction.response.send_message(
            "Something went wrong while checking the count.", 
            ephemeral=True
        )
        logger.error(f"Error in count command: {e}")