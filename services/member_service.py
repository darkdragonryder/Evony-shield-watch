"""
=========================================================
Member Service (CLEAN LIFECYCLE SYSTEM)
=========================================================
"""

from database import db


class MemberService:

    @staticmethod
    async def on_join(member):

        await db.set_member_contact(member.id)

        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="join"
        )

    @staticmethod
    async def on_leave(member):

        await db.set_member_contact(
            member.id,
            opt_in=0
        )

        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="leave"
        )

    @staticmethod
    async def on_ban(guild, user):

        await db.delete_member_data(user.id, guild.id)

        await db.log_reminder(
            guild_id=guild.id,
            event_type="member",
            reminder_type="ban"
        )
