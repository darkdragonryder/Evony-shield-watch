"""

 Evony Shield Watch
 Web Dashboard (Role-Based Control Panel)

"""

# =========================================================
# IMPORTS
# =========================================================

from flask import Flask, render_template_string, request, session, redirect
from database import db
from config import Config
import asyncio


# =========================================================
# APP INIT
# =========================================================

app = Flask(__name__)
app.secret_key = Config.WEB_SECRET_KEY


# =========================================================
# ROLE SYSTEM (SIMPLE CORE)
# =========================================================

def require_role(roles):
    def wrapper(func):
        def inner(*args, **kwargs):

            if session.get("role") not in roles:
                return "❌ Access Denied"

            return func(*args, **kwargs)

        return inner
    return wrapper


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    discord_id = int(request.form.get("discord_id"))

    user = asyncio.run(db.get_member_contact(discord_id))

    if not user:
        return "Invalid User"

    session["user"] = discord_id
    session["role"] = user["role"]

    return redirect("/")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    if "user" not in session:
        return """
        <form method='post' action='/login'>
            <input name='discord_id' placeholder='Discord ID'>
            <button>Login</button>
        </form>
        """

    role = session.get("role")

    return render_template_string("""
    <h1>🛡️ Evony Shield Watch</h1>
    <h3>Role: {{role}}</h3>

    {% if role in ['owner','admin'] %}
        <h2>⚙️ Admin Panel</h2>
        <p>User management, logs, alerts</p>
    {% endif %}

    {% if role == 'coordinator' %}
        <h2>📡 Coordinator Panel</h2>
        <p>View alerts only</p>
    {% endif %}

    <h2>👤 Member Panel</h2>
    <p>Telegram status + alerts</p>

    """, role=role)


# =========================================================
# RUN WEB SERVER
# =========================================================

def run():
    app.run(
        host=Config.WEB_HOST,
        port=Config.WEB_PORT
    )


if __name__ == "__main__":
    run()
