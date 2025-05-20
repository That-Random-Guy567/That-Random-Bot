import discord
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "game_config.json"
DEFAULT_CONFIG = {
    "yo": {"channel_id": None, "offender_role_id": None},
    "count": {"channel_id": None, "offender_role_id": None}
}
yo_state = {"current": "Yo", "last_user_id": None}
count_state = {"current": 1, "last_user_id": None}

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f)

config = load_config()

async def set_game_channel(game: str, channel: discord.TextChannel):
    config[game]["channel_id"] = channel.id
    save_config(config)

async def set_offender_role(game: str, role: discord.Role):
    config[game]["offender_role_id"] = role.id
    save_config(config)

async def create_offender_role(guild: discord.Guild) -> discord.Role:
    try:
        role = await guild.create_role(name="O-Offender", reason="YO/Count game sequence fail")
        return role
    except discord.Forbidden:
        return None

async def handle_message(message: discord.Message):
    for game_name, state, handler in [
        ("yo", yo_state, handle_yo_message),
        ("count", count_state, handle_count_message)
    ]:
        if config[game_name]["channel_id"] == message.channel.id:
            await handler(message, config[game_name])
            break

async def handle_yo_message(message: discord.Message, game_cfg):
    if message.author.bot: return
    content = message.content.strip()
    role = message.guild.get_role(game_cfg["offender_role_id"]) if game_cfg["offender_role_id"] else None

    # Only allow variations of Yo with variable O's
    if not content.lower().startswith("y") or not all(c == "o" for c in content.lower()[1:]):
        await assign_offender(message, role)
        return

    o_count = len(content) - 1
    prev_count = len(yo_state["current"]) - 1
    # Must alternate user, and O's can only go up or down by 1
    if message.author.id == yo_state["last_user_id"] or abs(o_count - prev_count) != 1:
        await assign_offender(message, role)
        return

    yo_state["current"] = content
    yo_state["last_user_id"] = message.author.id

async def handle_count_message(message: discord.Message, game_cfg):
    if message.author.bot: return
    role = message.guild.get_role(game_cfg["offender_role_id"]) if game_cfg["offender_role_id"] else None
    try:
        val = int(message.content.strip())
    except ValueError:
        await assign_offender(message, role)
        return

    if message.author.id == count_state["last_user_id"] or abs(val - count_state["current"]) != 1:
        await assign_offender(message, role)
        return

    count_state["current"] = val
    count_state["last_user_id"] = message.author.id

async def assign_offender(message: discord.Message, role: discord.Role):
    if role:
        await message.author.add_roles(role, reason="Sequence break in game")
    await message.channel.send(f"{message.author.mention} broke the game sequence and is now an O-Offender!")