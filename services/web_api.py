"""
Evony Shield Watch
Web Dashboard API (Backend Scaffold - FIXED)
"""

from fastapi import FastAPI, HTTPException
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

    try:

        data = await db.get_member_contact(discord_id)

        if not data:
            raise HTTPException(status_code=404, detail="Member not found")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# LIST ALL MEMBERS (ADMIN USE ONLY)
# =====================================================

@app.get("/members")
async def list_members():

    try:

        cursor = await db.db.execute("""
            SELECT user_id, telegram_id, telegram_username, opt_in, timezone
            FROM members
        """)

        rows = await cursor.fetchall()

        return [
            {
                "discord_id": r[0],
                "telegram_id": r[1],
                "telegram_username": r[2],
                "opt_in": r[3],
                "timezone": r[4]
            }
            for r in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
