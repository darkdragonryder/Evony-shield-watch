"""
Enterprise Member Service
Handles lifecycle, cleanup, restore, and identity tracking
"""

import datetime
from database import db


class MemberService:

    # =========================================================
    # MEMBER JOIN
    # =========================================================
    @staticmethod
    async def on_member_join(member):
        await db.set_member_contact(member.id)  # ensure exists

        # track join event for dashboard/audit
        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="join"
        )

    # =========================================================
    # MEMBER LEAVE (SOFT DELETE)
    # =========================================================
    @staticmethod
    async def on_member_remove(member):
        contact = await db.get_member_contact(member.id)

        if not contact:
            return

        # mark as inactive instead of deleting immediately
        await db.set_member_contact(
            member.id,
            opted_in=0,
            phone=contact.get("phone"),
            pushover_key=contact.get("pushover_key"),
            timezone=contact.get("timezone", "UTC")
        )

        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="leave"
        )

    # =========================================================
    # MEMBER BAN (HARD DELETE)
    # =========================================================
    @staticmethod
    async def on_member_ban(guild, user):
        # full purge
        async with db.db_path and __import__("aiosqlite").connect(db.db_path) as conn:
            await conn.execute("DELETE FROM member_contacts WHERE user_id = ?", (user.id,))
            await conn.commit()

        await db.log_reminder(
            guild_id=guild.id,
            event_type="member",
            reminder_type="ban"
        )

    # =========================================================
    # RESTORE ON REJOIN
    # =========================================================
    @staticmethod
    async def restore_if_exists(member):
        contact = await db.get_member_contact(member.id)

        if contact:
            await db.set_member_contact(member.id, opted_in=1)
            return True

        return False
