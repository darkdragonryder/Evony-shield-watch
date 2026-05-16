from fastapi import Request, HTTPException, Depends
from services.role_service import RoleService

roles = RoleService()

# =====================================================
# ROLE HIERARCHY
# =====================================================

ROLE_HIERARCHY = {
    "member": 0,
    "coordinator": 1,
    "admin": 2,
    "owner": 3
}


# =====================================================
# BASE AUTH (SAFE PARSER)
# =====================================================

async def get_user_role(request: Request) -> str:

    discord_id = request.headers.get("x-discord-id")

    if not discord_id:
        raise HTTPException(status_code=401, detail="Missing auth header")

    try:
        discord_id = int(discord_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid discord ID")

    role = await roles.get_role(discord_id)

    return role or "member"


# =====================================================
# ROLE CHECK FACTORY (CORRECT FASTAPI PATTERN)
# =====================================================

def require_role(min_role: str):

    async def checker(role: str = Depends(get_user_role)):

        user_level = ROLE_HIERARCHY.get(role, 0)
        required_level = ROLE_HIERARCHY.get(min_role, 0)

        if user_level < required_level:
            raise HTTPException(status_code=403, detail="Forbidden")

        return role  # return useful context

    return checker
