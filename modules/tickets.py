import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import json
import io
import os
from datetime import datetime, timezone, timedelta

from core.logging import logger
from constants import TICKET_DATA

# Path to open tickets JSON file
TICKET_FILE_PATH = os.path.join("..", "data", "open_tickets.json")
os.makedirs(os.path.dirname(TICKET_FILE_PATH), exist_ok=True)

# Load open tickets data
def load_open_tickets():
    try:
        with open(TICKET_FILE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding {TICKET_FILE_PATH}. Returning empty dict.")
        return {}

# Save open tickets data
def save_open_tickets(data):
    try:
        with open(TICKET_FILE_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving {TICKET_FILE_PATH}: {e}")

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.open_button = Button(
            label="Create a Ticket ✉️",
            style=discord.ButtonStyle.primary,
            custom_id="persistent_open_ticket"
        )
        self.open_button.callback = self.ticket_callback
        self.add_item(self.open_button)

    async def ticket_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if guild is None:
            await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
            return

        user_id_str = str(interaction.user.id)
        open_tickets = load_open_tickets()

        # Check if user already has an open ticket
        for ticket_info in open_tickets.values():
            if ticket_info["owner"] == user_id_str:
                await interaction.followup.send("You already have an open ticket. Please close it before opening a new one.", ephemeral=True)
                return

        # Check cooldown (5 minutes)
        cooldown_seconds = 5 * 60
        now_ts = datetime.utcnow().timestamp()
        if user_id_str in open_tickets:
            last_closed_ts = open_tickets[user_id_str].get("closed_timestamp", 0)
            if now_ts - last_closed_ts < cooldown_seconds:
                wait_time = int((cooldown_seconds - (now_ts - last_closed_ts)) / 60) + 1
                await interaction.followup.send(f"Please wait {wait_time} more minute(s) before opening a new ticket.", ephemeral=True)
                return

        # Create channel overwrites
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            guild.get_role(TICKET_DATA["SUPPORT_ROLE_ID"]): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }

        category = guild.get_channel(TICKET_DATA["CATEGORY_ID"])
        if category is None:
            await interaction.followup.send("Ticket category not found. Please contact an admin.", ephemeral=True)
            logger.error(f"Ticket category ID {TICKET_DATA['CATEGORY_ID']} not found.")
            return

        # Create ticket channel
        try:
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}".lower(),
                overwrites=overwrites,
                category=category,
                reason=f"Ticket opened by {interaction.user}"
            )
            logger.info(f"Created ticket channel {ticket_channel.name} for {interaction.user}.")
        except discord.Forbidden:
            logger.error("Missing permissions to create ticket channels.")
            await interaction.followup.send("I don't have permission to create ticket channels.", ephemeral=True)
            return
        except Exception as e:
            logger.error(f"Error creating ticket channel: {e}")
            await interaction.followup.send("Failed to create ticket channel. Try again later.", ephemeral=True)
            return

        # Store ticket info: key by channel ID, includes owner and no closed_timestamp (means open)
        open_tickets[str(ticket_channel.id)] = {
            "owner": user_id_str,
            "closed_timestamp": 0
        }
        save_open_tickets(open_tickets)

        embed = discord.Embed(
            title="Ticket Created! 🎟️",
            description="Click the **Close Ticket** button below when finished.",
            color=discord.Color.blue()
        )
        view = CloseTicketView(ticket_channel, user_id_str)
        await ticket_channel.send(f"{interaction.user.mention}", embed=embed, view=view)
        await interaction.followup.send(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self, ticket_channel: discord.TextChannel, ticket_owner: str):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
        self.ticket_owner = ticket_owner

        # Close Ticket button for owner & mods
        self.close_button = Button(
            label="Close Ticket",
            style=discord.ButtonStyle.danger,
            custom_id=f"persistent_close_ticket_{ticket_channel.id}"
        )
        self.close_button.callback = self.close_ticket_callback
        self.add_item(self.close_button)

        # Delete Ticket button for mods only, initially disabled (visible only if user is mod)
        self.delete_button = Button(
            label="Delete Ticket",
            style=discord.ButtonStyle.secondary,
            custom_id=f"persistent_delete_ticket_{ticket_channel.id}",
            disabled=True
        )
        self.delete_button.callback = self.delete_ticket_callback
        self.add_item(self.delete_button)

    async def close_ticket_callback(self, interaction: discord.Interaction):
        # Check if user is ticket owner or mod
        is_owner = str(interaction.user.id) == self.ticket_owner
        mod_role = interaction.guild.get_role(TICKET_DATA["SUPPORT_ROLE_ID"])
        is_mod = mod_role in interaction.user.roles if mod_role else False

        if not (is_owner or is_mod):
            await interaction.response.send_message("Only the ticket owner or moderators can close this ticket.", ephemeral=True)
            return

        await interaction.response.send_modal(CloseTicketModal(
            self.ticket_channel,
            self.ticket_owner,
            TICKET_DATA["TRANSCRIPTS_CHANNEL_ID"],
            is_owner,
            self
        ))

    async def delete_ticket_callback(self, interaction: discord.Interaction):
        # Only mods can delete ticket
        mod_role = interaction.guild.get_role(TICKET_DATA["SUPPORT_ROLE_ID"])
        if not mod_role or mod_role not in interaction.user.roles:
            await interaction.response.send_message("Only moderators can delete the ticket channel.", ephemeral=True)
            return

        try:
            await self.ticket_channel.delete(reason=f"Ticket deleted by {interaction.user}")
            logger.info(f"Ticket channel {self.ticket_channel.name} deleted by {interaction.user}.")
        except Exception as e:
            logger.error(f"Error deleting ticket channel: {e}")
            await interaction.response.send_message("Failed to delete the ticket channel.", ephemeral=True)

class CloseTicketModal(Modal):
    def __init__(self, ticket_channel: discord.TextChannel, ticket_owner: str, transcripts_channel_id: int, is_owner: bool, parent_view: CloseTicketView):
        super().__init__(title="Close Ticket")
        self.ticket_channel = ticket_channel
        self.ticket_owner = ticket_owner
        self.transcripts_channel_id = transcripts_channel_id
        self.is_owner = is_owner
        self.parent_view = parent_view

        self.reason_input = TextInput(
            label="Reason for Closing",
            style=discord.TextStyle.paragraph,
            placeholder="Enter reason for closing (optional)",
            required=False
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if guild is None:
            await interaction.followup.send("This action can only be performed in a server.", ephemeral=True)
            return

        transcripts_channel = guild.get_channel(self.transcripts_channel_id)
        if not transcripts_channel:
            logger.error(f"Transcripts channel not found: {self.transcripts_channel_id}")
            await interaction.followup.send("Transcript channel not found. Closing ticket anyway.", ephemeral=True)

        # Collect transcript messages
        transcript_lines = []
        try:
            async for message in self.ticket_channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                attachments = "\n".join([f"Attachment: {att.url}" for att in message.attachments]) if message.attachments else ""
                content = message.content if message.content else "(No text content)"
                transcript_lines.append(f"`{timestamp}` **{message.author.display_name}**: {content}\n{attachments}")
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            transcript_lines.append("Could not retrieve full transcript due to an error.")

        transcript_text = "\n".join(transcript_lines)
        transcript_file = discord.File(io.BytesIO(transcript_text.encode('utf-8')), filename=f"transcript_{self.ticket_channel.name}.txt")

        # Send transcript embed + file
        summary_embed = discord.Embed(
            title="Ticket Summary 🔒",
            color=discord.Color.dark_green(),
            timestamp=datetime.now(timezone.utc)
        )
        summary_embed.add_field(name="User", value=f"<@{self.ticket_owner}>", inline=False)
        summary_embed.add_field(name="Closed by", value=interaction.user.mention, inline=False)
        summary_embed.add_field(name="Reason", value=self.reason_input.value or "No reason provided", inline=False)
        summary_embed.set_footer(text=f"Ticket Channel: #{self.ticket_channel.name} | ID: {self.ticket_channel.id}")

        try:
            if transcripts_channel:
                await transcripts_channel.send(embed=summary_embed, file=transcript_file)
                logger.info(f"Transcript sent to {transcripts_channel.name}")
        except Exception as e:
            logger.error(f"Error sending transcript: {e}")
            await interaction.followup.send("Failed to send transcript to transcripts channel.", ephemeral=True)

        open_tickets = load_open_tickets()

        if self.is_owner:
            # For ticket owner closing:
            # Kick user from ticket channel, don't delete it, start cooldown
            try:
                member = guild.get_member(int(self.ticket_owner))
                if member:
                    await self.ticket_channel.set_permissions(member, view_channel=False)
                    logger.info(f"Kicked ticket owner {member} from ticket channel {self.ticket_channel.name}.")
            except Exception as e:
                logger.error(f"Error removing user permissions on close: {e}")

            # Store cooldown timestamp keyed by user ID
            # We store cooldown keyed by user ID (not channel ID) to track cooldowns per user
            # But also remove the open ticket keyed by channel id (since ticket remains open for mods, we keep channel id)
            # We'll store cooldown timestamp alongside user id under a special key for cooldown tracking

            # Remove ticket keyed by channel ID, then store cooldown keyed by user id
            if str(self.ticket_channel.id) in open_tickets:
                del open_tickets[str(self.ticket_channel.id)]
            open_tickets[self.ticket_owner] = {"closed_timestamp": datetime.now(timezone.utc).timestamp()}
            save_open_tickets(open_tickets)

            await interaction.followup.send("You have been removed from the ticket. Moderators will handle closing the ticket channel.", ephemeral=True)

            # Enable delete button for mods in this view
            self.parent_view.delete_button.disabled = False
            try:
                await interaction.message.edit(view=self.parent_view)
            except Exception:
                pass

        else:
            # For mods closing the ticket completely (delete channel)
            # Actually here mods close ticket only via modal, so we just mark it closed here and prompt them to use Delete button
            # We just remove ticket entry keyed by channel id but don't set cooldown for mods
            if str(self.ticket_channel.id) in open_tickets:
                del open_tickets[str(self.ticket_channel.id)]
            save_open_tickets(open_tickets)

            await interaction.followup.send("Ticket marked closed. Use the Delete Ticket button to delete the channel.", ephemeral=True)

async def setup_tickets(bot: commands.Bot):
    bot.add_view(TicketView())
    logger.info("Persistent TicketView added.")

    open_tickets = load_open_tickets()
    for channel_id_str, ticket_data in open_tickets.items():
        try:
            channel_id = int(channel_id_str)
            channel = bot.get_channel(channel_id)
            if channel and "owner" in ticket_data:
                bot.add_view(CloseTicketView(channel, ticket_data["owner"]))
                logger.info(f"Re-added CloseTicketView for channel {channel_id}.")
        except Exception as e:
            logger.error(f"Failed to re-add CloseTicketView for {channel_id_str}: {e}")