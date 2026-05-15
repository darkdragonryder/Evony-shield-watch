from fastapi import Request, HTTPException
from services.role_service import RoleService

roles = RoleService()


async def require_role(min_role: str):

    hierarchy = {
        "member": 0,
        "coordinator": 1,
        "admin": 2,
        "owner": 3
    }

    async def checker(request: Request):

        discord_id = request.headers.get("x-discord-id")

        if not discord_id:
            raise HTTPException(status_code=401, detail="Missing auth")

        role = await roles.get_role(int(discord_id))

        if hierarchy[role] < hierarchy[min_role]:
            raise HTTPException(status_code=403, detail="Forbidden")

        return True

    return checker
