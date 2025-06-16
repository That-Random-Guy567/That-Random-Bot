import discord
from discord import app_commands
from core.logging import logger
from constants import TICKET_DATA
from modules.tickets import TicketView  # adjust import if needed

@app_commands.command(name="ticket", description="Set up the ticket creation menu.")
async def ticket(interaction: discord.Interaction):
    ticket_channel_id = TICKET_DATA.get("TICKET_CHANNEL_ID")
    if ticket_channel_id is None:
        await interaction.response.send_message("Ticket channel not configured.", ephemeral=True)
        logger.error("TICKET_CHANNEL_ID not found in constants.")
        return

    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
        return

    ticket_channel = guild.get_channel(ticket_channel_id)
    if ticket_channel is None:
        await interaction.response.send_message("Ticket channel not found or inaccessible.", ephemeral=True)
        logger.error(f"Ticket channel with ID {ticket_channel_id} not found in guild {guild.id}")
        return

    embed = discord.Embed(
        title="Ticket System 🎫",
        description="To create a ticket, click the button below. Our support team will assist you as soon as possible.",
        color=discord.Color.blurple()
    )
    view = TicketView()

    try:
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Ticket menu sent to {ticket_channel.mention}.", ephemeral=True)
        logger.info(f"Ticket creation embed sent to channel {ticket_channel.id} by {interaction.user}.")
    except Exception as e:
        await interaction.response.send_message("Failed to send the ticket menu to the configured channel.", ephemeral=True)
        logger.error(f"Error sending ticket embed to channel {ticket_channel_id}: {e}")