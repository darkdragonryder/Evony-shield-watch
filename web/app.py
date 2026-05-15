"""
=========================================================
 Evony Shield Watch
 Web Dashboard (FULL UI + API)
=========================================================
"""

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database import db
from services.web_auth import require_role
from services.role_service import RoleService

app = FastAPI(title="Evony Shield Dashboard")
templates = Jinja2Templates(directory="web/templates")

roles = RoleService()


# =====================================================
# HOME (LOGIN ENTRY)
# =====================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# =====================================================
# DASHBOARD
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    cursor = await db.db.execute("""
    SELECT discord_id, telegram_username, role
    FROM members
    """)

    members = await cursor.fetchall()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "members": members
        }
    )


# =====================================================
# ROLE PANEL (OWNER ONLY)
# =====================================================

@app.post("/dashboard/set-role")
async def set_role(
    discord_id: int = Form(...),
    role: str = Form(...),
    auth=Depends(require_role("owner"))
):

    await roles.set_role(discord_id, role)

    return RedirectResponse("/dashboard", status_code=302)
