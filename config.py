# config.py
import os
from dotenv import load_dotenv
from typing import Final
from constants import TOKEN_NAME

load_dotenv()
TOKEN: Final[str] = os.getenv(TOKEN_NAME)