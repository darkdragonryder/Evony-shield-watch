"""
=========================================================
 Evony Shield Watch
 Web Dashboard API (ROLE-AWARE)
=========================================================
"""

from fastapi import FastAPI, Depends
from database import db
from services.web_auth import require_role

app = FastAPI(title="Evony Shield Watch Dashboard")


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# =====================================================
# GET OWN PROFILE (ANY USER)
# =====================================================

@app.get("/me")
async def me():
    return {"message": "use /member endpoint with auth header"}


# =====================================================
# GET MEMBER (ADMIN+)
# =====================================================

@app.get("/member/{discord_id}")
async def get_member(
    discord_id: int,
    auth=Depends(require_role("admin"))
):

    return await db.get_member_contact(discord_id)


# =====================================================
# LIST MEMBERS (ADMIN+)
# =====================================================

@app.get("/members")
async def list_members(
    auth=Depends(require_role("admin"))
):

    cursor = await db.db.execute("""
    SELECT discord_id, telegram_id, telegram_username, role
    FROM members
    """)

    rows = await cursor.fetchall()

    return [
        {
            "discord_id": r[0],
            "telegram_id": r[1],
            "telegram_username": r[2],
            "role": r[3]
        }
        for r in rows
    ]


# =====================================================
# SET ROLE (OWNER ONLY)
# =====================================================

@app.post("/role/set")
async def set_role(payload: dict, auth=Depends(require_role("owner"))):

    discord_id = payload.get("discord_id")
    role = payload.get("role")

    await db.db.execute("""
    UPDATE members
    SET role = ?
    WHERE discord_id = ?
    """, (role, discord_id))

    await db.db.commit()

    return {"status": "updated"}
