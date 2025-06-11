import discord
from discord.ext import commands
from core.logging import logger
import random

async def setup_auto_responders(bot: commands.Bot) -> None: 
    """Setup auto responders for the bot."""
    
    @bot.event
    async def on_message(message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == bot.user:
            return

        # Process commands first
        await bot.process_commands(message)
        
        # Auto-response commands
        if message.content.lower().startswith("hello"):
            if random.random() < 0.1:  # 10% chance to respond
                agencies = [
                    "-# This user is under the review of the FBI • [Review](<https://www.fbi.gov/investigate>)",
                    "-# This user is under the review of the CIA • [Review](<https://www.cia.gov/>)",
                    "-# This user is under the review of NATO • [Review](<https://www.nato.int/>)",
                    "-# This user is under the review of the Secret Service • [Review](<https://www.secretservice.gov/>)",
                    "-# This user is under the review of Interpol • [Review](<https://www.interpol.int/>)",
                    "-# This user is under the review of the Department of Homeland Security • [Review](<https://www.dhs.gov/>)",
                    "-# This user is under the review of the NSA • [Review](<https://www.nsa.gov/>)",
                    "-# This user is under the review of MI6 • [Review](<https://www.sis.gov.uk/>)",
                    "-# This user is under the review of Mossad • [Review](<https://www.mossad.gov.il/>)",
                    "-# This user is under the review of GCHQ • [Review](<https://www.gchq.gov.uk/>)",
                    "-# This user is under the review of the Defense Intelligence Agency • [Review](<https://www.dia.mil/>)",
                    "-# This user is under the review of ASIS • [Review](<https://www.asis.gov.au/>)",
                    "-# This user is under the review of Bundesnachrichtendienst • [Review](<https://www.bnd.bund.de/>)",
                    "-# This user is under the review of CSIS • [Review](<https://www.csis-scrs.gc.ca/>)",
                    "-# This user is under the review of FSB • [Review](<https://fsb.ru/>)",
                    "-# This user is under the review of the European Union Agency for Law Enforcement Cooperation (Europol) • [Review](<https://www.europol.europa.eu/>)",
                    "-# This user is under the review of the Australian Federal Police • [Review](<https://www.afp.gov.au/>)",
                    "-# This user is under the review of the New Zealand Security Intelligence Service • [Review](<https://www.nzsis.govt.nz/>)",
                    "-# This user is under the review of the Indian Intelligence Bureau • [Review](<https://www.mha.gov.in/>)"
                ]

                chosen_agency = random.choice(agencies)
                await message.channel.send(chosen_agency)
                logger.info(f"Trolled {message.author} with response: {chosen_agency}")

        # Add more auto-responses here following the same pattern