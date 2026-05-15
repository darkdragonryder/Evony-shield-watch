import aiosqlite
from typing import Dict, Optional, List


class Database:
    def __init__(self, db_path="evony.db"):
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
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS event_schedule (
                guild_id INTEGER PRIMARY KEY,
                current_event TEXT DEFAULT 'svs',
                next_event_date TEXT
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS custom_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                event_type TEXT,
                name TEXT,
                start_time TEXT,
                end_time TEXT,
                coordinator_id INTEGER,
                checkin_cutoff TEXT,
                channel_id INTEGER,
                message_id INTEGER,
                status TEXT DEFAULT 'active'
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS event_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                user_id INTEGER,
                status TEXT,
                checked_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS member_contacts (
                user_id INTEGER PRIMARY KEY,
                phone TEXT,
                pushover_key TEXT,
                timezone TEXT DEFAULT 'UTC',
                opted_in INTEGER DEFAULT 1
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS reminder_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                event_type TEXT,
                reminder_type TEXT,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

            await db.commit()

    # ---------- SERVER ----------
    async def get_server_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM server_config WHERE guild_id=?", (guild_id,))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def set_server_config(self, guild_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            existing = await db.execute("SELECT 1 FROM server_config WHERE guild_id=?", (guild_id,))
            exists = await existing.fetchone()

            if exists:
                await db.execute(
                    f"UPDATE server_config SET {','.join([k+'=?' for k in kwargs])} WHERE guild_id=?",
                    list(kwargs.values()) + [guild_id]
                )
            else:
                cols = ",".join(["guild_id"] + list(kwargs.keys()))
                vals = [guild_id] + list(kwargs.values())
                await db.execute(
                    f"INSERT INTO server_config ({cols}) VALUES ({','.join(['?']*len(vals))})",
                    vals
                )
            await db.commit()

    # ---------- SCHEDULE ----------
    async def get_event_schedule(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM event_schedule WHERE guild_id=?", (guild_id,))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def set_event_schedule(self, guild_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            exists = await db.execute("SELECT 1 FROM event_schedule WHERE guild_id=?", (guild_id,))
            exists = await exists.fetchone()

            if exists:
                await db.execute(
                    f"UPDATE event_schedule SET {','.join([k+'=?' for k in kwargs])} WHERE guild_id=?",
                    list(kwargs.values()) + [guild_id]
                )
            else:
                cols = ",".join(["guild_id"] + list(kwargs.keys()))
                vals = [guild_id] + list(kwargs.values())
                await db.execute(
                    f"INSERT INTO event_schedule ({cols}) VALUES ({','.join(['?']*len(vals))})",
                    vals
                )
            await db.commit()

    # ---------- CUSTOM EVENTS ----------
    async def create_custom_event(self, **data):
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("""
                INSERT INTO custom_events
                (guild_id,event_type,name,start_time,end_time,coordinator_id,checkin_cutoff,channel_id)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                data["guild_id"],
                data["event_type"],
                data["name"],
                data["start_time"],
                data["end_time"],
                data["coordinator_id"],
                data["checkin_cutoff"],
                data["channel_id"]
            ))
            await db.commit()
            return cur.lastrowid

    async def get_custom_event(self, event_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM custom_events WHERE event_id=?", (event_id,))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def get_active_custom_events(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM custom_events WHERE guild_id=? AND status='active'",
                (guild_id,)
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def update_custom_event(self, event_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE custom_events SET {','.join([k+'=?' for k in kwargs])} WHERE event_id=?",
                list(kwargs.values()) + [event_id]
            )
            await db.commit()

    async def delete_member(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM member_contacts WHERE user_id=?", (user_id,))
            await db.commit()


db = Database()
