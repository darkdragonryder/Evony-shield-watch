"""
=========================================================
 Evony Shield Watch
 Web Dashboard API (Backend Scaffold)
=========================================================
"""

from fastapi import FastAPI
from database import db

app = FastAPI(title="Evony Shield Watch API")


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# =====================================================
# GET MEMBER
# =====================================================

@app.get("/member/{discord_id}")
async def get_member(discord_id: int):

    data = await db.get_member_contact(discord_id)

    if not data:
        return {"error": "not found"}

    return data


# =====================================================
# LIST ALL MEMBERS (ADMIN USE)
# =====================================================

@app.get("/members")
async def list_members():

    cursor = await db.db.execute("""
    SELECT discord_id, telegram_id, telegram_username
    FROM members
    """)

    rows = await cursor.fetchall()

    return [
        {
            "discord_id": r[0],
            "telegram_id": r[1],
            "telegram_username": r[2]
        }
        for r in rows
    ]
