# config.py
import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")