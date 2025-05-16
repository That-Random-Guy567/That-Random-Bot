# core/utils.py
"""
This module contains utility functions for the Discord bot.
"""

import discord
from typing import Optional

async def get_channel_by_name_or_id(guild: discord.Guild, channel_name_or_id: str) -> Optional[discord.TextChannel]:
    """
    Retrieves a Discord text channel from a guild, either by name or ID.

    Args:
        guild (discord.Guild): The guild to search in.
        channel_name_or_id (str): The name or ID of the channel.

    Returns:
        Optional[discord.TextChannel]: The found channel, or None if not found.
    """
    # Try to convert to integer (ID)
    try:
        channel_id = int(channel_name_or_id)
        channel = guild.get_channel(channel_id)
        if channel:
            return channel
    except ValueError:
        pass  # Not an integer, try by name

    # Try to find by name (case-insensitive)
    channel = discord.utils.get(guild.text_channels, name=channel_name_or_id)
    return channel

# Example usage (in other modules):
# from core.utils import get_channel_by_name_or_id
# channel = await get_channel_by_name_or_id(guild, "general")
# if channel:
#     await channel.send("Found the channel!")
