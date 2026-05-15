"""
Evony Shield Watch - Web Dashboard
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import aiosqlite

from database import db

app = FastAPI()


# =========================================================
# DASHBOARD HOME
# =========================================================
@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    return """
    <html>
        <head><title>Evony Shield Watch Dashboard</title></head>
        <body>
            <h1>🛡️ Shield Watch Dashboard</h1>
            <p>Status: Online</p>
            <a href="/stats">View Stats</a>
        </body>
    </html>
    """


# =========================================================
# BASIC STATS (ADMIN VIEW LATER)
# =========================================================
@app.get("/stats")
async def stats():
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM member_contacts")
        members = (await cursor.fetchone())[0]

        cursor = await conn.execute("SELECT COUNT(*) FROM custom_events")
        events = (await cursor.fetchone())[0]

    return {
        "members_tracked": members,
        "custom_events": events,
        "status": "online"
    }
