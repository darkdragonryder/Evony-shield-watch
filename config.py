"""
Evony Shield Watch - Configuration
"""
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
    
    # SVS reminders: 1h39m + 1h before reset
    SVS_FIRST_REMINDER = timedelta(hours=1, minutes=39)
    SVS_SECOND_REMINDER = timedelta(hours=1)
    SVS_PURGE_OFFSET = timedelta(hours=1)
    
    # KE reminder: 1h before reset
    KE_REMINDER = timedelta(hours=1)
    
    EVENT_END_DAY = 0  # Monday
    
    EVENT_CLEANUP_DELAY = timedelta(minutes=10)
    DEFAULT_CUTOFF_MINUTES = 30
    
    DEFAULT_BUBBLE_CHANNEL = "🫧bubble🫧"
    DEFAULT_BATTLEFIELD_CHANNEL = "battlefield-messages"
    
    SVS = "svs"
    KE = "ke"
    BOC = "boc"
    BOG = "bog"
    ALLSTARS = "allstars"
    BATTLEFIELD = "battlefield"
    CUSTOM_EVENT_TYPES = [BOC, BOG, ALLSTARS, BATTLEFIELD]
    
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_PHONE = os.getenv("TWILIO_PHONE")
    PUSHOVER_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")
    
    @classmethod
    def has_sms(cls):
        return all([cls.TWILIO_SID, cls.TWILIO_TOKEN, cls.TWILIO_PHONE])
    
    @classmethod
    def has_pushover(cls):
        return bool(cls.PUSHOVER_TOKEN)
