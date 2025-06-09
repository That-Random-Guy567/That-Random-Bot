"""
# ─── COUNTING CHANNEL COMMANDS ────────────────────────────────────────────────
@bot.tree.command(name="count_setchannel", description="Sets the counting channel")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def count_setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    count_channel_map[interaction.guild.id] = channel.id
    await interaction.response.send_message(f":white_check_mark: Counting channel is now {channel.mention}")

@bot.tree.command(name="count_unsetchannel", description="Removes the counting channel setting")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def count_unsetchannel(interaction: discord.Interaction):
    if interaction.guild.id in count_channel_map:
        del count_channel_map[interaction.guild.id]
        await interaction.response.send_message(":octagonal_sign: Counting channel setting has been removed.")
    else:
        await interaction.response.send_message(":information_source: No counting channel was set.")


    # Handling counting in configured channel
    if (
        message.guild and 
        message.guild.id in count_channel_map and 
        message.channel.id == count_channel_map[message.guild.id]
    ):
        chan_id = message.channel.id
        data = count_data.get(chan_id, {"last_count": 0, "last_user": None})
        last_count, last_user = data["last_count"], data["last_user"]
        content = message.content.strip()

        reason_error = None
        try:
            current = int(content)
            is_numeric = True
        except ValueError:
            is_numeric = False

        if is_numeric:
            if last_count == 0:
                if current != 1:
                    reason_error = f"wrong number (expected 1, got {current})"
            else:
                if message.author.id == last_user:
                    reason_error = "You counted twice in a row"
                elif current != last_count + 1:
                    reason_error = f"wrong number (expected {last_count + 1}, got {current})"

            if reason_error:
                await message.add_reaction(":pepeno:")
                await message.channel.send(f"{message.author.mention} Counting error: {reason_error}. The counter has been reset to 0.")
                count_data[chan_id] = {"last_count": 0, "last_user": None}
            else:
                await message.add_reaction(":pepeyes:")
                count_data[chan_id] = {"last_count": current, "last_user": message.author.id}

    await bot.process_commands(message) 
"""