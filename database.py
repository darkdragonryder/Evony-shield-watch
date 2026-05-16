"""
=========================================================
 Evony Shield Watch
 Database Layer (SINGLE SOURCE OF TRUTH)
 FIXED SCHEMA + CONSISTENT CONTRACT
=========================================================
"""

import aiosqlite
from config import Config


class Database:

    def __init__(self):
        self.db_path = Config.DB_PATH
        self.db = None

    # =====================================================
    # INIT
    # =====================================================

    async def init(self):

        self.db = await aiosqlite.connect(self.db_path)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS member_contacts (
            user_id INTEGER PRIMARY KEY,
            telegram_id TEXT,
            telegram_username TEXT,
            timezone TEXT DEFAULT 'UTC',
            role TEXT DEFAULT 'member',
            opted_in INTEGER DEFAULT 1
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS server_config (
            guild_id INTEGER PRIMARY KEY,
            bubble_channel_id INTEGER,
            battlefield_channel_id INTEGER,
            setup_complete INTEGER DEFAULT 0
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS event_schedule (
            guild_id INTEGER PRIMARY KEY,
            current_event TEXT DEFAULT 'svs',
            next_event_date TEXT
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS custom_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            name TEXT,
            event_type TEXT,
            start_time TEXT,
            end_time TEXT,
            coordinator_id INTEGER,
            checkin_cutoff TEXT,
            channel_id INTEGER,
            message_id INTEGER
        )
        """)

        await self.db.commit()

    # =====================================================
    # MEMBER CONTACT
    # =====================================================

    async def set_member_contact(self, user_id: int, **kwargs):

        await self.db.execute("""
        INSERT INTO member_contacts (user_id)
        VALUES (?)
        ON CONFLICT(user_id) DO NOTHING
        """, (user_id,))

        for key, value in kwargs.items():

            await self.db.execute(f"""
            UPDATE member_contacts
            SET {key} = ?
            WHERE user_id = ?
            """, (value, user_id))

        await self.db.commit()

    async def get_member_contact(self, user_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM member_contacts
        WHERE user_id = ?
        """, (user_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "user_id": row[0],
            "telegram_id": row[1],
            "telegram_username": row[2],
            "timezone": row[3],
            "role": row[4],
            "opted_in": row[5]
        }

    async def delete_member_contact(self, user_id: int):

        await self.db.execute("""
        DELETE FROM member_contacts
        WHERE user_id = ?
        """, (user_id,))

        await self.db.commit()

    # =====================================================
    # SERVER CONFIG
    # =====================================================

    async def set_server_config(self, guild_id: int, **kwargs):

        await self.db.execute("""
        INSERT INTO server_config (guild_id)
        VALUES (?)
        ON CONFLICT(guild_id) DO NOTHING
        """, (guild_id,))

        for key, value in kwargs.items():

            await self.db.execute(f"""
            UPDATE server_config
            SET {key} = ?
            WHERE guild_id = ?
            """, (value, guild_id))

        await self.db.commit()

    async def get_server_config(self, guild_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM server_config
        WHERE guild_id = ?
        """, (guild_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "guild_id": row[0],
            "bubble_channel_id": row[1],
            "battlefield_channel_id": row[2],
            "setup_complete": row[3]
        }

    # =====================================================
    # EVENT SCHEDULE
    # =====================================================

    async def set_event_schedule(self, guild_id: int, **kwargs):

        await self.db.execute("""
        INSERT INTO event_schedule (guild_id)
        VALUES (?)
        ON CONFLICT(guild_id) DO NOTHING
        """, (guild_id,))

        for key, value in kwargs.items():

            await self.db.execute(f"""
            UPDATE event_schedule
            SET {key} = ?
            WHERE guild_id = ?
            """, (value, guild_id))

        await self.db.commit()

    async def get_event_schedule(self, guild_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM event_schedule
        WHERE guild_id = ?
        """, (guild_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "guild_id": row[0],
            "current_event": row[1],
            "next_event_date": row[2]
        }

    # =====================================================
    # CUSTOM EVENTS (BASIC SAFE OPS)
    # =====================================================

    async def create_custom_event(self, **kwargs):

        cursor = await self.db.execute("""
        INSERT INTO custom_events (
            guild_id, name, event_type, start_time,
            end_time, coordinator_id, checkin_cutoff,
            channel_id, message_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            kwargs.get("guild_id"),
            kwargs.get("name"),
            kwargs.get("event_type"),
            kwargs.get("start_time"),
            kwargs.get("end_time"),
            kwargs.get("coordinator_id"),
            kwargs.get("checkin_cutoff"),
            kwargs.get("channel_id"),
            None
        ))

        await self.db.commit()

        return cursor.lastrowid

    async def get_custom_event(self, event_id: int):

        cursor = await self.db.execute("""
        SELECT * FROM custom_events
        WHERE event_id = ?
        """, (event_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "event_id": row[0],
            "guild_id": row[1],
            "name": row[2],
            "event_type": row[3],
            "start_time": row[4],
            "end_time": row[5],
            "coordinator_id": row[6],
            "checkin_cutoff": row[7],
            "channel_id": row[8],
            "message_id": row[9]
        }

    async def delete_custom_event(self, event_id: int):

        await self.db.execute("""
        DELETE FROM custom_events
        WHERE event_id = ?
        """, (event_id,))

        await self.db.commit()

    async def update_custom_event(self, event_id: int, **kwargs):

        for key, value in kwargs.items():

            await self.db.execute(f"""
            UPDATE custom_events
            SET {key} = ?
            WHERE event_id = ?
            """, (value, event_id))

        await self.db.commit()
