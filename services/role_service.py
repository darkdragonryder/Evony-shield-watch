"""
=========================================================
 Evony Shield Watch
 Role Service (Single Source of Truth)
=========================================================
"""

from database import db


class RoleService:

    # =====================================================
    # GET ROLE
    # =====================================================

    async def get_role(self, discord_id: int):

        user = await db.get_member_contact(discord_id)

        if not user:
            return "member"

        return user.get("role", "member")

    # =====================================================
    # SET ROLE
    # =====================================================

    async def set_role(self, discord_id: int, role: str):

        await db.db.execute("""
        UPDATE members
        SET role = ?
        WHERE discord_id = ?
        """, (role, discord_id))

        await db.db.commit()

    # =====================================================
    # PERMISSION CHECKS
    # =====================================================

    async def is_admin(self, discord_id: int):

        role = await self.get_role(discord_id)
        return role in ["owner", "admin"]

    async def is_owner(self, discord_id: int):

        role = await self.get_role(discord_id)
        return role == "owner"
