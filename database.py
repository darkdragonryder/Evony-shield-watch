"""
Evony Shield Watch - Database (Enterprise Telegram Upgrade)
"""

import aiosqlite
from datetime import datetime


class Database:

    def __init__(self, db_path="evony_bot.db"):
        self.db_path = db_path

    # =========================================================
    # INIT (ADD TELEGRAM TABLES)
    # =========================================================

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:

            # existing tables assumed already here...

            await db.execute("""
                CREATE TABLE IF NOT EXISTS member_contacts (
                    user_id INTEGER PRIMARY KEY,
                    phone TEXT,
                    telegram_id TEXT,
                    telegram_username TEXT,
                    telegram_link_token TEXT,
                    telegram_link_expiry TIMESTAMP,
                    timezone TEXT DEFAULT 'UTC',
                    opted_in INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active',
                    last_seen TIMESTAMP,
                    left_at TIMESTAMP,
                    banned_at TIMESTAMP
                )
            """)

            await db.commit()

    # =========================================================
    # MEMBER CONTACT UPSERT (SAFE)
    # =========================================================

    async def set_member_contact(self, user_id: int, **kwargs):

        if not kwargs:
            return

        async with aiosqlite.connect(self.db_path) as db:

            async with db.execute(
                "SELECT 1 FROM member_contacts WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                exists = await cursor.fetchone()

            if exists:
                set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [user_id]

                await db.execute(
                    f"UPDATE member_contacts SET {set_clause} WHERE user_id = ?",
                    values
                )

            else:
                cols = ["user_id"] + list(kwargs.keys())
                vals = [user_id] + list(kwargs.values())
                placeholders = ", ".join(["?"] * len(vals))

                await db.execute(
                    f"INSERT INTO member_contacts ({', '.join(cols)}) VALUES ({placeholders})",
                    vals
                )

            await db.commit()

    # =========================================================
    # GET MEMBER
    # =========================================================

    async def get_member_contact(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT * FROM member_contacts WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # =========================================================
    # TELEGRAM TOKEN CREATE
    # =========================================================

    async def create_telegram_link_token(self, user_id: int, token: str, expiry: datetime):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                UPDATE member_contacts
                SET telegram_link_token = ?,
                    telegram_link_expiry = ?
                WHERE user_id = ?
            """, (token, expiry.isoformat(), user_id))

            await db.commit()

    # =========================================================
    # TELEGRAM LINK FINALIZE
    # =========================================================

    async def link_telegram_user(self, token: str, telegram_id: str, username: str):

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute("""
                SELECT user_id, telegram_link_expiry
                FROM member_contacts
                WHERE telegram_link_token = ?
            """, (token,)) as cursor:

                row = await cursor.fetchone()

                if not row:
                    return False

                # expiry check
                if row["telegram_link_expiry"]:
                    exp = datetime.fromisoformat(row["telegram_link_expiry"])
                    if datetime.utcnow() > exp:
                        return False

                await db.execute("""
                    UPDATE member_contacts
                    SET telegram_id = ?,
                        telegram_username = ?,
                        telegram_link_token = NULL,
                        telegram_link_expiry = NULL
                    WHERE user_id = ?
                """, (telegram_id, username, row["user_id"]))

                await db.commit()
                return True
