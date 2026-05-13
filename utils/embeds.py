"""
Discord Embed Templates
"""
import discord
from config import Config

class Embeds:
    @staticmethod
    def shield_alert(event_type: str, is_purge: bool = False):
        if is_purge:
            title = "⚔️ PURGE ATTACK INCOMING!"
            desc = "Purge attack starts in 1 hour! Put up your **BUBBLE NOW** if not participating!"
            color = 0xFF0000
        else:
            title = f"🛡️ {event_type.upper()} - SHIELD UP!"
            desc = f"Server reset approaching! Put up your **bubble** if you are NOT participating in {event_type.upper()}!"
            color = 0xFFA500
        
        embed = discord.Embed(title=title, description=desc, color=color)
        embed.add_field(name="⏰ Time Remaining", value="Check your PM for your local time!", inline=False)
        embed.set_footer(text="Evony Shield Watch | Stay safe, bubble up!")
        return embed
    
    @staticmethod
    def event_start_notice(event_type: str):
        embed = discord.Embed(
            title=f"🔥 {event_type.upper()} HAS STARTED!",
            description=f"The server has reset! {event_type.upper()} is now LIVE!",
            color=0x00FF00
        )
        embed.set_footer(text="Good luck in battle!")
        return embed
    
    @staticmethod
    def custom_event_checkin(event_name: str, event_type: str,
                          start_time: str, coordinator: str, cutoff: str):
        embed = discord.Embed(
            title=f"📋 {event_name}",
            description=f"**{event_type.upper()}** event starting soon!",
            color=0x3498db
        )
        embed.add_field(name="🕐 Start Time", value=start_time, inline=True)
        embed.add_field(name="👤 Coordinator", value=coordinator, inline=True)
        embed.add_field(name="⏳ Check-in Cutoff", value=cutoff, inline=False)
        embed.add_field(
            name="✅ Check-in",
            value="React with ✅ to confirm\nReact with ❌ to opt out",
            inline=False
        )
        return embed
    
    @staticmethod
    def event_roster(event_name: str, participants: list, reserves: list):
        embed = discord.Embed(title=f"🎯 {event_name} - Final Roster", color=0x2ecc71)
        embed.add_field(
            name=f"✅ Confirmed ({len(participants)})",
            value="\n".join(f"• {p}" for p in participants) or "None",
            inline=False
        )
        embed.add_field(
            name=f"❌ Opted Out ({len(reserves)})",
            value="\n".join(f"• {p}" for p in reserves) or "None",
            inline=False
        )
        return embed
    
    @staticmethod
    def personal_reminder(event_type: str, local_time: str, instruction: str):
        embed = discord.Embed(
            title=f"⏰ {event_type.upper()} Reminder",
            description=f"**Your local time:** {local_time}",
            color=0x9b59b6
        )
        embed.add_field(name="📢 Action Required", value=instruction, inline=False)
        embed.set_footer(text="Reply STOP to opt out of notifications")
        return embed
    
    @staticmethod
    def setup_welcome():
        embed = discord.Embed(
            title="🛡️ Evony Shield Watch Setup",
            description="Let's configure your server!",
            color=0x1abc9c
        )
        embed.add_field(name="Step 1", value="Set bubble notification channel", inline=False)
        embed.add_field(name="Step 2", value="Set battlefield messages channel", inline=False)
        embed.add_field(name="Step 3", value="Assign event coordinator role", inline=False)
        return embed
    
    @staticmethod
    def help_command():
        embed = discord.Embed(
            title="📖 Evony Shield Watch Commands",
            description="All available slash commands",
            color=0x34495e
        )
        embed.add_field(
            name="🔧 Setup",
            value="`/setup` - Start server configuration\n"
                  "`/setbubble` - Set/Create bubble channel\n"
                  "`/setbattlefield` - Set/Create battlefield channel\n"
                  "`/setcoordinator` - Set coordinator role",
            inline=False
        )
        embed.add_field(
            name="📅 Events",
            value="`/event create` - Create custom event\n"
                  "`/event cancel` - Cancel event\n"
                  "`/event list` - List active events\n"
                  "`/event roster` - Show final roster",
            inline=False
        )
        embed.add_field(
            name="⚙️ Admin",
            value="`/forceevent` - Force set current event\n"
                  "`/addeventcoord` - Add event coordinator\n"
                  "`/contact` - Set member phone/pushover",
            inline=False
        )
        embed.add_field(
            name="👤 Personal",
            value="`/mytime` - Check your local reset time\n"
                  "`/settimezone` - Set your timezone\n"
                  "`/optout` - Stop PM notifications\n"
                  "`/optin` - Re-enable PM notifications",
            inline=False
        )
        return embed
