import discord
from discord.ext import commands
from core.logging import logger
from constants import LOG_CHANNEL_IDS
from datetime import datetime, timezone

async def on_member_update(before: discord.Member, after: discord.Member):
    if before.roles == after.roles:
        return  # No change

    added_roles = [r for r in after.roles if r not in before.roles]
    if not added_roles:
        return

    guild = after.guild
    log_channel = guild.get_channel(LOG_CHANNEL_IDS.ROLE_CHANGE)
    if not log_channel:
        logger.error(f"Could not find role log channel with ID {LOG_CHANNEL_IDS.ROLE_CHANGE}")
        return

    # Try to get who changed roles once
    adder = None
    try:
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id:
                adder = entry.user
                break
    except Exception as e:
        logger.warning(f"Error fetching audit logs for role add: {e}")

    role_names = ", ".join([r.name for r in added_roles])
    embed = discord.Embed(
        color=discord.Color.blue(),
        description=f"{after.mention} was given the role{'s' if len(added_roles) > 1 else ''} {role_names}",
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text=f"ID: {after.id}")
    embed.set_author(name=after.display_name, icon_url=after.display_avatar.url)

    if adder:
        embed.add_field(name="Added by", value=f"{adder.mention} ({adder.id})", inline=False)

    await log_channel.send(embed=embed)