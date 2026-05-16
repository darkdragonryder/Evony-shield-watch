"""
Evony Shield Watch
Role Service (Single Source of Truth - FIXED)
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

        async with db.db_path and __import__("aiosqlite").connect(db.db_path) as conn:

            await conn.execute("""
                UPDATE members
                SET role = ?
                WHERE user_id = ?
            """, (role, discord_id))

            await conn.commit()

    # =====================================================
    # PERMISSION CHECKS
    # =====================================================

    async def is_admin(self, discord_id: int):

        role = await self.get_role(discord_id)
        return role in ("owner", "admin")

    async def is_owner(self, discord_id: int):

        role = await self.get_role(discord_id)
        return role == "owner"
