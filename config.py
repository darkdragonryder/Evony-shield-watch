import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    TOKEN = os.getenv("DISCORD_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))

    HOST_TIMEZONE = os.getenv("HOST_TIMEZONE", "America/New_York")
    RESET_HOUR = int(os.getenv("RESET_HOUR", "17"))
    RESET_MINUTE = int(os.getenv("RESET_MINUTE", "0"))

    SVS_FIRST_REMINDER = timedelta(hours=1, minutes=39)
    SVS_SECOND_REMINDER = timedelta(hours=1)
    SVS_PURGE_OFFSET = timedelta(hours=1)

    KE_REMINDER = timedelta(hours=1)

    EVENT_CLEANUP_DELAY = timedelta(minutes=10)

    SVS = "svs"
    KE = "ke"

    CUSTOM_EVENT_TYPES = ["boc", "bog", "allstars", "battlefield"]
