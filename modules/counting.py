import discord
from discord.ext import commands
from core.logging import logger
from constants import COUNTING_CHANNEL_ID, EMOJIS

# Counting data storage
count_data = {}  # Stores counting progress

async def setup_counting(bot: commands.Bot) -> None:
    """Setup counting system"""
    logger.info("Initializing counting module...")
    
    async def handle_counting(message: discord.Message):
        """Handle counting messages"""
        # Ignore bot messages
        if message.author.bot:
            logger.debug(f"Ignoring bot message in counting channel from {message.author}")
            return

        # Check if message is in counting channel
        if message.channel.id == COUNTING_CHANNEL_ID:
            logger.info(f"Processing count from {message.author}: {message.content}")
            chan_id = message.channel.id
            data = count_data.get(chan_id, {"last_count": 0, "last_user": None})
            last_count, last_user = data["last_count"], data["last_user"]
            content = message.content.strip()

            try:
                current = int(content)
                logger.info(f"Valid number received: {current} (last: {last_count})")
                
                if last_count == 0 and current != 1:
                    reason = f"wrong number (expected 1, got {current})"
                elif message.author.id == last_user:
                    reason = "You counted twice in a row"
                elif current != last_count + 1:
                    reason = f"wrong number (expected {last_count + 1}, got {current})"
                else:
                    reason = None

                if reason:
                    logger.info(f"Count failed: {reason}")
                    try:
                        await message.add_reaction(EMOJIS['PEPE_NO'])
                        await message.channel.send(
                            f"{message.author.mention} Counting error: {reason}. Counter reset to 0."
                        )
                        count_data[chan_id] = {"last_count": 0, "last_user": None}
                    except discord.HTTPException as e:
                        logger.error(f"Failed to add reaction or send message: {e}")
                else:
                    logger.info(f"Count successful: {current}")
                    try:
                        await message.add_reaction(EMOJIS['PEPE_YES'])
                        count_data[chan_id] = {"last_count": current, "last_user": message.author.id}
                    except discord.HTTPException as e:
                        logger.error(f"Failed to add reaction: {e}")

            except ValueError:
                logger.debug(f"Ignored non-numeric message: {content}")

    # Register the listener
    bot.add_listener(handle_counting, 'on_message')
    logger.info(f"Counting module initialized for channel ID: {COUNTING_CHANNEL_ID}")