"""
=========================================================
Evony Shield Watch
Event Engine (SINGLE SOURCE OF TRUTH)
Week-based deterministic SVS / KE rotation
=========================================================
"""

from datetime import datetime
import pytz

from config import Config


class EventEngine:

    @staticmethod
    def get_current_event() -> str:
        """
        Deterministic event system:
        - Alternates weekly based on ISO week number
        - No drift possible
        """

        week = datetime.utcnow().isocalendar()[1]

        # CONFIG: even weeks = KE, odd weeks = SVS
        if week % 2 == 0:
            return Config.KE
        return Config.SVS

    @staticmethod
    def is_ke_week() -> bool:
        return EventEngine.get_current_event() == Config.KE

    @staticmethod
    def is_svs_week() -> bool:
        return EventEngine.get_current_event() == Config.SVS
