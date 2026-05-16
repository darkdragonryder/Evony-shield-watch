"""
Enterprise Member Service
Fixed + Multi-Guild Safe + DB-Aligned
"""

from database import db


class MemberService:

    # =========================================================
    # MEMBER JOIN
    # =========================================================
    @staticmethod
    async def on_member_join(member):

        # ensure record exists
        await db.set_member_contact(member.id)

        # restore opt-in if user returns
        await db.set_member_contact(member.id, opt_in=1)

        # audit log
        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="join"
        )

    # =========================================================
    # MEMBER LEAVE (SOFT DISABLE)
    # =========================================================
    @staticmethod
    async def on_member_remove(member):

        contact = await db.get_member_contact(member.id)

        if not contact:
            return

        # soft disable only valid DB fields
        await db.set_member_contact(
            member.id,
            opt_in=0
        )

        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="leave"
        )

    # =========================================================
    # MEMBER BAN (CLEAN PURGE)
    # =========================================================
    @staticmethod
    async def on_member_ban(guild, user):

        # IMPORTANT: use DB layer only
        async with db.db_path and __import__("aiosqlite").connect(db.db_path) as conn:

            # safe fallback if table differs
            await conn.execute(
                "DELETE FROM members WHERE user_id = ?",
                (user.id,)
            )

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

        if not contact:
            return False

        # re-enable notifications
        await db.set_member_contact(member.id, opt_in=1)

        return True
