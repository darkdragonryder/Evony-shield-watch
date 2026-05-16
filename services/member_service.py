"""
=========================================================
 Evony Shield Watch
 Member Service (LIFECYCLE CORE - CLEAN + SAFE)
 Multi-Guild Consistent Identity System
=========================================================
"""

from database import db


class MemberService:

    # =====================================================
    # MEMBER JOIN (ENSURE + RESTORE)
    # =====================================================

    @staticmethod
    async def on_member_join(member):

        # Ensure record exists
        await db.set_member_contact(member.id)

        # Try restore if previously existed
        await MemberService.restore_if_exists(member)

        # Log event
        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="join"
        )

    # =====================================================
    # MEMBER LEAVE (SOFT REMOVE - PRESERVE DATA)
    # =====================================================

    @staticmethod
    async def on_member_remove(member):

        contact = await db.get_member_contact(member.id)

        if not contact:
            return

        # Soft disable only (DO NOT DELETE)
        await db.set_member_contact(
            member.id,
            opted_in=0,
            telegram_id=contact.get("telegram_id"),
            telegram_username=contact.get("telegram_username"),
            timezone=contact.get("timezone", "UTC"),
            role=contact.get("role", "member")
        )

        await db.log_reminder(
            guild_id=member.guild.id,
            event_type="member",
            reminder_type="leave"
        )

    # =====================================================
    # MEMBER BAN (HARD DELETE ACROSS ALL GUILDS)
    # =====================================================

    @staticmethod
    async def on_member_ban(guild, user):

        # Full purge (corrected safe delete)
        await db.delete_member_contact(user.id)

        await db.log_reminder(
            guild_id=guild.id,
            event_type="member",
            reminder_type="ban"
        )

    # =====================================================
    # RESTORE SYSTEM (REJOIN SAFE)
    # =====================================================

    @staticmethod
    async def restore_if_exists(member):

        contact = await db.get_member_contact(member.id)

        if contact:
            await db.set_member_contact(
                member.id,
                opted_in=1
            )
            return True

        return False
