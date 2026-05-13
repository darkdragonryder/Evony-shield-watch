"""
Notifications, Timezone, SMS/Pushover - Slash Commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import pytz
import aiohttp
from database import db
from utils.time_utils import get_user_local_reset_time, format_local_time
from config import Config

class Reminders(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
    
    async def _send_sms(self, phone: str, message: str) -> bool:
        if not Config.has_sms():
            return False
        from twilio.rest import Client
        try:
            client = Client(Config.TWILIO_SID, Config.TWILIO_TOKEN)
            client.messages.create(body=message, from_=Config.TWILIO_PHONE, to=phone)
            return True
        except Exception as e:
            print(f"SMS Error: {e}")
            return False
    
    async def _send_pushover(self, user_key: str, message: str, title: str = "Evony Shield") -> bool:
        if not Config.has_pushover():
            return False
        try:
            async with self.session.post(
                "https://api.pushover.net/1/messages.json",
                data={"token": Config.PUSHOVER_TOKEN, "user": user_key,
                      "message": message, "title": title, "priority": 1}
            ) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"Pushover Error: {e}")
            return False
    
    async def notify_member(self, user_id: int, message: str, title: str = "Evony Alert"):
        contact = await db.get_member_contact(user_id)
        if not contact:
            return
        results = {"dm": False, "sms": False, "push": False}
        
        user = self.bot.get_user(user_id)
        if user and contact.get("opted_in", 1):
            try:
                embed = discord.Embed(title=title, description=message, color=0xFF0000, timestamp=datetime.now())
                await user.send(embed=embed)
                results["dm"] = True
            except:
                pass
        
        if contact.get("phone"):
            results["sms"] = await self._send_sms(contact["phone"], f"{title}: {message[:100]}")
        if contact.get("pushover_key"):
            results["push"] = await self._send_pushover(contact["pushover_key"], message, title)
        
        return results
    
    # ========== SLASH COMMANDS ==========
    
    @app_commands.command(name="mytime", description="Check your local server reset time")
    async def slash_mytime(self, interaction: discord.Interaction):
        contact = await db.get_member_contact(interaction.user.id)
        user_tz = contact.get("timezone", "UTC") if contact else "UTC"
        local_reset = get_user_local_reset_time(user_tz)
        time_str = format_local_time(local_reset)
        
        embed = discord.Embed(
            title="⏰ Your Local Server Reset Time",
            description=f"When it's 5pm {Config.HOST_TIMEZONE}, it's:\n**{time_str}** for you.",
            color=0x3498db
        )
        embed.add_field(name="Your Timezone", value=user_tz, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="settimezone", description="Set your timezone")
    @app_commands.describe(timezone="Your timezone (e.g., Europe/London, Asia/Tokyo)")
    async def slash_settimezone(self, interaction: discord.Interaction, timezone: str):
        try:
            pytz.timezone(timezone)
            await db.set_member_contact(interaction.user.id, timezone=timezone)
            await interaction.response.send_message(f"✅ Timezone set to **{timezone}**", ephemeral=True)
        except pytz.UnknownTimeZoneError:
            await interaction.response.send_message(
                "❌ Invalid timezone. Examples: `America/New_York`, `Europe/London`, `Asia/Tokyo`", ephemeral=True
            )
    
    @app_commands.command(name="contact", description="Set member contact info (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="Member to set contact for", method="phone or pushover", value="Phone number or Pushover key")
    @app_commands.choices(method=[
        app_commands.Choice(name="Phone (SMS)", value="phone"),
        app_commands.Choice(name="Pushover Key", value="pushover")
    ])
    async def slash_contact(self, interaction: discord.Interaction, user: discord.Member,
                           method: app_commands.Choice[str], value: str):
        if method.value == "phone":
            await db.set_member_contact(user.id, phone=value)
        else:
            await db.set_member_contact(user.id, pushover_key=value)
        await interaction.response.send_message(f"✅ {method.name} set for {user.mention}", ephemeral=True)
    
    @app_commands.command(name="optout", description="Stop receiving PM notifications")
    async def slash_optout(self, interaction: discord.Interaction):
        await db.set_member_contact(interaction.user.id, opted_in=0)
        await interaction.response.send_message("🔕 You've opted out. Use `/optin` to re-enable.", ephemeral=True)
    
    @app_commands.command(name="optin", description="Re-enable PM notifications")
    async def slash_optin(self, interaction: discord.Interaction):
        await db.set_member_contact(interaction.user.id, opted_in=1)
        await interaction.response.send_message("🔔 Notifications re-enabled!", ephemeral=True)
    
    @app_commands.command(name="testnotify", description="Test notifications to a user (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="User to test notifications on")
    async def slash_testnotify(self, interaction: discord.Interaction, user: discord.Member):
        results = await self.notify_member(user.id, "Test notification from Evony Shield Watch!", "Test")
        status = []
        status.append("✅ Discord DM" if results["dm"] else "❌ Discord DM")
        status.append("✅ SMS" if results["sms"] else "❌ SMS")
        status.append("✅ Pushover" if results["push"] else "❌ Pushover")
        await interaction.response.send_message(f"Test results for {user.mention}:\n" + "\n".join(status), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
