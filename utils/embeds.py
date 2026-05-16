"""
=========================================================
Evony Shield Watch
Discord Embed Templates
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord


# =========================================================
# EMBED FACTORY
# =========================================================

class Embeds:

    # =====================================================
    # SHIELD ALERTS
    # =====================================================

    @staticmethod
    def shield_alert(
        event_type: str,
        phase: str = "warning"
    ):

        event_name = event_type.upper()

        # -------------------------------------------------
        # SVS PURGE WARNING
        # -------------------------------------------------

        if phase == "svs_purge_warning":

            embed = discord.Embed(
                title="🚨 SVS PURGE IN 39 MINUTES",
                description=(
                    "Purge begins in 39 minutes.\n\n"
                    "🛡️ Put your bubble up NOW if "
                    "you are not participating."
                ),
                color=0xff9900
            )

        # -------------------------------------------------
        # SVS PURGE START
        # -------------------------------------------------

        elif phase == "svs_purge_start":

            embed = discord.Embed(
                title="⚔️ SVS PURGE HAS STARTED",
                description=(
                    "Purge is now active.\n\n"
                    "🛡️ Bubble immediately if "
                    "you are not fighting."
                ),
                color=0xff0000
            )

        # -------------------------------------------------
        # SVS START
        # -------------------------------------------------

        elif phase == "svs_start":

            embed = discord.Embed(
                title="🔥 SVS HAS STARTED",
                description=(
                    "Server War has officially begun.\n\n"
                    "🛡️ Bubble up.\n"
                    "🚫 Stay out of ALL tiles and relics."
                ),
                color=0x00cc66
            )

        # -------------------------------------------------
        # KE WARNING
        # -------------------------------------------------

        elif phase == "ke_warning":

            embed = discord.Embed(
                title="⚔️ KE STARTS IN 1 HOUR",
                description=(
                    "Kill Event begins in 1 hour.\n\n"
                    "🛡️ Bubble now if needed.\n"
                    "✅ Tiles and relics are SAFE."
                ),
                color=0xff9900
            )

        # -------------------------------------------------
        # KE START
        # -------------------------------------------------

        elif phase == "ke_start":

            embed = discord.Embed(
                title="🔥 KE HAS STARTED",
                description=(
                    "Kill Event is now active.\n\n"
                    "🛡️ Bubble up.\n"
                    "✅ Tiles and relics remain SAFE."
                ),
                color=0x00cc66
            )

        # -------------------------------------------------
        # DEFAULT
        # -------------------------------------------------

        else:

            embed = discord.Embed(
                title=f"🛡️ {event_name} ALERT",
                description="Event notification.",
                color=0x3498db
            )

        embed.set_footer(
            text="Evony Shield Watch"
        )

        return embed

    # =====================================================
    # PERSONAL REMINDER
    # =====================================================

    @staticmethod
    def personal_reminder(
        event_type: str,
        local_time: str,
        instruction: str
    ):

        embed = discord.Embed(
            title=f"⏰ {event_type.upper()} Reminder",
            description=(
                f"🕒 Your local reset time:\n\n"
                f"{local_time}"
            ),
            color=0x9b59b6
        )

        embed.add_field(
            name="📢 Action Required",
            value=instruction,
            inline=False
        )

        embed.set_footer(
            text="Evony Shield Watch"
        )

        return embed

    # =====================================================
    # EVENT START NOTICE
    # =====================================================

    @staticmethod
    def event_start_notice(event_type: str):

        if event_type == "svs":

            description = (
                "🔥 SVS is now LIVE.\n\n"
                "🛡️ Bubble immediately.\n"
                "🚫 Stay out of all tiles and relics."
            )

        else:

            description = (
                "🔥 KE is now LIVE.\n\n"
                "🛡️ Bubble immediately.\n"
                "✅ Tiles and relics are SAFE."
            )

        embed = discord.Embed(
            title=f"{event_type.upper()} STARTED",
            description=description,
            color=0x2ecc71
        )

        embed.set_footer(
            text="Good luck and stay safe."
        )

        return embed

    # =====================================================
    # CUSTOM EVENT CHECK-IN
    # =====================================================

    @staticmethod
    def custom_event_checkin(
        event_name: str,
        event_type: str,
        start_time: str,
        coordinator: str,
        cutoff: str
    ):

        embed = discord.Embed(
            title=f"📋 {event_name}",
            description=(
                f"{event_type.upper()} "
                "event starting soon."
            ),
            color=0x3498db
        )

        embed.add_field(
            name="🕐 Start Time",
            value=start_time,
            inline=True
        )

        embed.add_field(
            name="👤 Coordinator",
            value=coordinator,
            inline=True
        )

        embed.add_field(
            name="⏳ Check-in Cutoff",
            value=cutoff,
            inline=False
        )

        embed.add_field(
            name="✅ Check-in",
            value=(
                "React with ✅ to confirm\n"
                "React with ❌ to opt out"
            ),
            inline=False
        )

        return embed

    # =====================================================
    # EVENT ROSTER
    # =====================================================

    @staticmethod
    def event_roster(
        event_name: str,
        participants: list,
        reserves: list
    ):

        embed = discord.Embed(
            title=f"🎯 {event_name} - Final Roster",
            color=0x2ecc71
        )

        embed.add_field(
            name=f"✅ Confirmed ({len(participants)})",
            value="\n".join(
                f"• {p}" for p in participants
            ) or "None",
            inline=False
        )

        embed.add_field(
            name=f"❌ Opted Out ({len(reserves)})",
            value="\n".join(
                f"• {p}" for p in reserves
            ) or "None",
            inline=False
        )

        return embed

    # =====================================================
    # HELP COMMAND
    # =====================================================

    @staticmethod
    def help_command():

        embed = discord.Embed(
            title="📖 Evony Shield Watch Commands",
            description="Available slash commands",
            color=0x34495e
        )

        embed.add_field(
            name="🛠️ Setup",
            value=(
                "/setup - Setup the server\n"
                "/linktelegram - Link Telegram alerts"
            ),
            inline=False
        )

        embed.add_field(
            name="⚔️ Events",
            value=(
                "/currentevent - Show current event\n"
                "/forceevent - Force SVS or KE"
            ),
            inline=False
        )

        embed.add_field(
            name="👤 Personal",
            value=(
                "/mytime - Show local reset time\n"
                "/settimezone - Set timezone\n"
                "/optout - Disable alerts\n"
                "/optin - Enable alerts"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Utility",
            value=(
                "/ping - Bot latency\n"
                "/botinfo - Bot information\n"
                "/stats - Server stats"
            ),
            inline=False
        )

        embed.set_footer(
            text="Evony Shield Watch"
        )

        r
