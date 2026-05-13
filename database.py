"""
Evony Shield Watch - SQLite Database
"""
import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import Config

class Database:
    def __init__(self, db_path: str = "evony_bot.db"):
        self.db_path = db_path
    
    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    bubble_channel_id INTEGER,
                    battlefield_channel_id INTEGER,
                    event_coordinator_role_id INTEGER,
                    current_event TEXT DEFAULT 'svs',
                    setup_complete INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_schedule (
                    guild_id INTEGER PRIMARY KEY,
                    current_event TEXT DEFAULT 'svs',
                    last_event_end DATE,
                    next_event_date DATE
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS custom_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT,
                    name TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    coordinator_id INTEGER,
                    checkin_cutoff TIMESTAMP,
                    channel_id INTEGER,
                    message_id INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS event_checkins (
                    checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    user_id INTEGER,
                    status TEXT,
                    checked_at TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS member_contacts (
                    user_id INTEGER PRIMARY KEY,
                    phone TEXT,
                    pushover_key TEXT,
                    timezone TEXT DEFAULT 'UTC',
                    opted_in INTEGER DEFAULT 1
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reminder_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT,
                    reminder_type TEXT,
                    sent_at TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bubble_tracking (
                    track_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    event_type TEXT,
                    event_date DATE,
                    reminded_at TIMESTAMP
                )
            """)
            
            await db.commit()
    
    async def get_server_config(self, guild_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM server_config WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def set_server_config(self, guild_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            existing = await self.get_server_config(guild_id)
            if existing:
                sets = ", ".join(f"{k} = ?" for k in kwargs.keys())
                values = list(kwargs.values()) + [guild_id]
                await db.execute(
                    f"UPDATE server_config SET {sets} WHERE guild_id = ?", values
                )
            else:
                cols = ["guild_id"] + list(kwargs.keys())
                vals = [guild_id] + list(kwargs.values())
                placeholders = ", ".join("?" for _ in vals)
                await db.execute(
                    f"INSERT INTO server_config ({', '.join(cols)}) VALUES ({placeholders})",
                    vals
                )
            await db.commit()
    
    async def get_event_schedule(self, guild_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM event_schedule WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def set_event_schedule(self, guild_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            existing = await self.get_event_schedule(guild_id)
            if existing:
                sets = ", ".join(f"{k} = ?" for k in kwargs.keys())
                values = list(kwargs.values()) + [guild_id]
                await db.execute(
                    f"UPDATE event_schedule SET {sets} WHERE guild_id = ?", values
                )
            else:
                cols = ["guild_id"] + list(kwargs.keys())
                vals = [guild_id] + list(kwargs.values())
                placeholders = ", ".join("?" for _ in vals)
                await db.execute(
                    f"INSERT INTO event_schedule ({', '.join(cols)}) VALUES ({placeholders})",
                    vals
                )
            await db.commit()
    
    async def rotate_event(self, guild_id: int):
        schedule = await self.get_event_schedule(guild_id)
        if not schedule:
            await self.set_event_schedule(guild_id, current_event=Config.SVS)
            return Config.SVS
        
        current = schedule.get("current_event", Config.SVS)
        next_event = Config.KE if current == Config.SVS else Config.SVS
        today = datetime.now().date()
        days_until_friday = (4 - today.weekday()) % 7 or 7
        next_friday = today + timedelta(days=days_until_friday)
        
        await self.set_event_schedule(
            guild_id=guild_id,
            current_event=next_event,
            last_event_end=today,
            next_event_date=next_friday
        )
        return next_event
    
    async def create_custom_event(self, guild_id: int, event_type: str, name: str,
                                start_time: datetime, end_time: datetime,
                                coordinator_id: int, checkin_cutoff: datetime,
                                channel_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO custom_events 
                (guild_id, event_type, name, start_time, end_time, 
                 coordinator_id, checkin_cutoff, channel_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (guild_id, event_type, name, start_time, end_time,
                  coordinator_id, checkin_cutoff, channel_id))
            await db.commit()
            return cursor.lastrowid
    
    async def get_custom_event(self, event_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM custom_events WHERE event_id = ?", (event_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def get_active_custom_events(self, guild_id: int) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM custom_events 
                WHERE guild_id = ? AND status = 'active' 
                AND end_time > datetime('now')
                ORDER BY start_time
            """, (guild_id,)) as cursor:
                return [dict(row) async for row in cursor]
    
    async def update_custom_event(self, event_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            sets = ", ".join(f"{k} = ?" for k in kwargs.keys())
            values = list(kwargs.values()) + [event_id]
            await db.execute(
                f"UPDATE custom_events SET {sets} WHERE event_id = ?", values
            )
            await db.commit()
    
    async def delete_custom_event(self, event_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE custom_events SET status = 'deleted' WHERE event_id = ?",
                (event_id,)
            )
            await db.commit()
    
    async def checkin_member(self, event_id: int, user_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO event_checkins (event_id, user_id, status, checked_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT DO UPDATE SET
                status = excluded.status,
                checked_at = excluded.checked_at
            """, (event_id, user_id, status))
            await db.commit()
    
    async def get_event_checkins(self, event_id: int) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM event_checkins WHERE event_id = ?", (event_id,)
            ) as cursor:
                return [dict(row) async for row in cursor]
    
    async def set_member_contact(self, user_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            existing = await self.get_member_contact(user_id)
            if existing:
                sets = ", ".join(f"{k} = ?" for k in kwargs.keys())
                values = list(kwargs.values()) + [user_id]
                await db.execute(
                    f"UPDATE member_contacts SET {sets} WHERE user_id = ?", values
                )
            else:
                cols = ["user_id"] + list(kwargs.keys())
                vals = [user_id] + list(kwargs.values())
                placeholders = ", ".join("?" for _ in vals)
                await db.execute(
                    f"INSERT INTO member_contacts ({', '.join(cols)}) VALUES ({placeholders})",
                    vals
                )
            await db.commit()
    
    async def get_member_contact(self, user_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM member_contacts WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def log_reminder(self, guild_id: int, event_type: str,
                          reminder_type: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO reminder_logs (guild_id, event_type, reminder_type, sent_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (guild_id, event_type, reminder_type))
            await db.commit()
    
    async def was_reminder_sent_today(self, guild_id: int, event_type: str,
                                      reminder_type: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT COUNT(*) FROM reminder_logs 
                WHERE guild_id = ? AND event_type = ? AND reminder_type = ?
                AND date(sent_at) = date('now')
            """, (guild_id, event_type, reminder_type)) as cursor:
                count = await cursor.fetchone()
                return count[0] > 0
    
    async def track_bubble_reminder(self, guild_id: int, user_id: int,
                                    event_type: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO bubble_tracking (guild_id, user_id, event_type, event_date, reminded_at)
                VALUES (?, ?, ?, date('now'), datetime('now'))
            """, (guild_id, user_id, event_type))
            await db.commit()
    
    async def has_bubble_reminder_today(self, guild_id: int, user_id: int,
                                        event_type: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT COUNT(*) FROM bubble_tracking 
                WHERE guild_id = ? AND user_id = ? AND event_type = ?
                AND event_date = date('now')
            """, (guild_id, user_id, event_type)) as cursor:
                count = await cursor.fetchone()
                return count[0] > 0

db = Database()
