"""
Evony Shield Watch
Member Service (FIXED + DB ALIGNED)
"""

from database import db


class MemberService:

    @staticmethod
    async def on_member_join(member):

        await db.set_member_contact(member.id)

    @staticmethod
    async def on_member_remove(member):

        contact = await db.get_member_contact(member.id)

        if not contact:
            return

        await db.set_member_contact(
            member.id,
            opt_in=0
        )

    @staticmethod
    async def on_member_ban(guild, user):

        await db.set_member_contact(
            user.id,
            opt_in=0
        )

    @staticmethod
    async def restore_if_exists(member):

        contact = await db.get_member_contact(member.id)

        if contact:
            await db.set_member_contact(
                member.id,
                opt_in=1
            )
            return True

        return False
