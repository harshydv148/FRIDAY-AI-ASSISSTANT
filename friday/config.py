"""
Configuration — load environment variables and app-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Server identity
    SERVER_NAME: str = os.getenv("SERVER_NAME", "Friday")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # External API keys (add as needed)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")

    # Voice assistant settings
    WAKE_WORD: str = "friday"

    ACTIVE_DURATION: int = 20

    VOICE_RATE: int = 180

    MODEL_NAME: str = "llama-3.1-8b-instant"

    MAX_CHROME_TABS: int = 30

    STANDBY_ENABLED: bool = True


config = Config()
