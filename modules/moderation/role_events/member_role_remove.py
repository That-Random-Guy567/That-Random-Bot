import discord
from discord.ext import commands
from constants import LOG_CHANNEL_IDS
import logging
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger('discord')

class MemberRoleRemove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        removed_roles = [role for role in before.roles if role not in after.roles]
        if not removed_roles:
            return

        guild = after.guild
        channel = guild.get_channel(LOG_CHANNEL_IDS.ROLE_CHANGE)
        if channel is None:
            logger.error(f"Role log channel with ID {LOG_CHANNEL_IDS.ROLE_CHANGE} not found in guild {guild.name} ({guild.id})")
            return

        # Attempt to get the user who removed the role(s) from audit logs
        remover = None
        try:
            async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id:
                    # Check if roles were removed in this entry
                    before_roles = set(before.roles)
                    after_roles_set = set(after.roles)
                    removed = before_roles - after_roles_set
                    if removed:
                        remover = entry.user
                        break
        except Exception as e:
            logger.error(f"Failed to fetch audit logs for role removal: {e}")

        timestamp_str = datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M")

        role_names = ", ".join(role.name for role in removed_roles)

        embed = discord.Embed(
            description=f"{after.mention} was removed from the role{'s' if len(removed_roles) > 1 else ''} {role_names}",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(name=after.name, icon_url=after.display_avatar.url)
        embed.set_footer(text=f"ID: {after.id} • {timestamp_str}")

        if remover:
            embed.add_field(name="Removed by", value=remover.mention, inline=False)

        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send role removal log message: {e}")

def setup(bot):
    bot.add_cog(MemberRoleRemove(bot))
