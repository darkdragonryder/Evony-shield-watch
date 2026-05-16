"""
=========================================================
 Evony Shield Watch
 Embed Templates (FINAL UNIFIED FORMAT LAYER)
 SINGLE EVENT LANGUAGE: SVS / KE ONLY
=========================================================
"""

import discord


class Embeds:

    # =====================================================
    # SHIELD ALERT (UNIFIED PHASE SYSTEM)
    # =====================================================

    @staticmethod
    def shield_alert(event_type: str, phase: str = "warning"):

        event_type = (event_type or "svs").lower()

        # -------------------------------------------------
        # SVS PURGE WARNING
        # -------------------------------------------------

        if event_type == "svs" and phase == "warning":

            return discord.Embed(
                title="🚨 SVS WARNING",
                description=(
                    "Server War (SVS) is approaching.\n\n"
                    "🛡️ Prepare shields now.\n"
                    "⏳ Avoid unnecessary exposure."
                ),
                color=0xff9900
            )

        # -------------------------------------------------
        # SVS START
        # -------------------------------------------------

        if event_type == "svs" and phase == "start":

            return discord.Embed(
                title="🔥 SVS STARTED",
                description=(
                    "Server War is now LIVE.\n\n"
                    "🛡️ Bubble immediately if not fighting.\n"
                    "🚫 Avoid tiles & relics."
                ),
                color=0xff0000
            )

        # -------------------------------------------------
        # KE WARNING
        # -------------------------------------------------

        if event_type == "ke" and phase == "warning":

            return discord.Embed(
                title="⚔️ KE WARNING",
                description=(
                    "Kill Event is approaching.\n\n"
                    "🛡️ Prepare shields if needed.\n"
                    "⚠️ Combat window opening soon."
                ),
                color=0xff9900
            )

        # -------------------------------------------------
        # KE START
        # -------------------------------------------------

        if event_type == "ke" and phase == "start":

            return discord.Embed(
                title="🔥 KE STARTED",
                description=(
                    "Kill Event is now ACTIVE.\n\n"
                    "🛡️ Bubble if required.\n"
                    "⚔️ PvP is fully enabled."
                ),
                color=0x00cc66
            )

        # -------------------------------------------------
        # DEFAULT FALLBACK
        # -------------------------------------------------

        return discord.Embed(
            title=f"🛡️ {event_type.upper()} ALERT",
            description="Event notification active.",
            color=0x3498db
        )

    # =====================================================
    # EVENT START NOTICE (STATE ENTRY POINT)
    # =====================================================

    @staticmethod
    def event_start_notice(event_type: str):

        event_type = (event_type or "svs").lower()

        if event_type == "svs":

            return discord.Embed(
                title="🔥 SVS HAS BEGUN",
                description=(
                    "Server War is now active.\n\n"
                    "🛡️ Maintain shield discipline.\n"
                    "🚫 Avoid high-risk zones."
                ),
                color=0xff0000
            )

        return discord.Embed(
            title="🔥 KE HAS BEGUN",
            description=(
                "Kill Event is now active.\n\n"
                "🛡️ Engage safely.\n"
                "⚔️ PvP zones enabled."
            ),
            color=0x00cc66
        )

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

        return discord.Embed(
            title=f"📋 {event_name}",
            description=f"{event_type.upper()} event check-in open.",
            color=0x3498db
        ).add_field(
            name="🕐 Start",
            value=start_time,
            inline=True
        ).add_field(
            name="👤 Coordinator",
            value=coordinator,
            inline=True
        ).add_field(
            name="⏳ Cutoff",
            value=cutoff,
            inline=False
        ).add_field(
            name="✅ Status",
            value="React ✅ to join / ❌ to decline",
            inline=False
        )

    # =====================================================
    # EVENT ROSTER
    # =====================================================

    @staticmethod
    def event_roster(event_name: str, participants: list, reserves: list):

        embed = discord.Embed(
            title=f"🎯 {event_name} Roster",
            color=0x2ecc71
        )

        embed.add_field(
            name=f"✅ Confirmed ({len(participants)})",
            value="\n".join(f"• {p}" for p in participants) or "None",
            inline=False
        )

        embed.add_field(
            name=f"❌ Declined ({len(reserves)})",
            value="\n".join(f"• {p}" for p in reserves) or "None",
            inline=False
        )

        return embed

    # =====================================================
    # HELP
    # =====================================================

    @staticmethod
    def help_command():

        return discord.Embed(
            title="📖 Evony Shield Watch",
            description="Available commands",
            color=0x34495e
        ).add_field(
            name="Setup",
            value="/setup, /linktelegram",
            inline=False
        ).add_field(
            name="Events",
            value="/event_create, /event_list",
            inline=False
        ).add_field(
            name="Personal",
            value="/mytime, /settimezone, /optout, /optin",
            inline=False
        ).add_field(
            name="Utility",
            value="/ping, /botinfo, /stats",
            inline=False
        ).set_footer(
            text="Evony Shield Watch"
        )
