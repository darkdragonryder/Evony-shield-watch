"""
Evony Shield Watch
Discord Embed Templates (FIXED + CONSISTENT)
"""

import discord


class Embeds:

    # =====================================================
    # SHIELD ALERTS (UNIFIED SYSTEM)
    # =====================================================

    @staticmethod
    def shield_alert(event_type: str, phase: str = "warning"):

        event_name = (event_type or "EVENT").upper()

        # -------------------------------------------------
        # SVS PURGE WARNING
        # -------------------------------------------------
        if phase == "svs_purge_warning":

            return discord.Embed(
                title="🚨 SVS PURGE IN 39 MINUTES",
                description=(
                    "Purge begins in 39 minutes.\n\n"
                    "🛡️ Put your bubble up NOW if not participating."
                ),
                color=0xff9900
            ).set_footer(text="Evony Shield Watch")

        # -------------------------------------------------
        # SVS PURGE START
        # -------------------------------------------------
        if phase == "svs_purge_start":

            return discord.Embed(
                title="⚔️ SVS PURGE HAS STARTED",
                description=(
                    "Purge is now active.\n\n"
                    "🛡️ Bubble immediately if not fighting."
                ),
                color=0xff0000
            ).set_footer(text="Evony Shield Watch")

        # -------------------------------------------------
        # SVS START
        # -------------------------------------------------
        if phase == "svs_start":

            return discord.Embed(
                title="🔥 SVS HAS STARTED",
                description=(
                    "Server War has begun.\n\n"
                    "🛡️ Bubble up.\n🚫 Avoid tiles and relics."
                ),
                color=0x00cc66
            ).set_footer(text="Evony Shield Watch")

        # -------------------------------------------------
        # KE WARNING
        # -------------------------------------------------
        if phase == "ke_warning":

            return discord.Embed(
                title="⚔️ KE STARTS IN 1 HOUR",
                description=(
                    "Kill Event begins in 1 hour.\n\n"
                    "🛡️ Bubble if needed.\n"
                    "✅ Tiles are safe."
                ),
                color=0xff9900
            ).set_footer(text="Evony Shield Watch")

        # -------------------------------------------------
        # KE START
        # -------------------------------------------------
        if phase == "ke_start":

            return discord.Embed(
                title="🔥 KE HAS STARTED",
                description=(
                    "Kill Event is now active.\n\n"
                    "🛡️ Bubble up if needed.\n"
                    "✅ Tiles remain safe."
                ),
                color=0x00cc66
            ).set_footer(text="Evony Shield Watch")

        # -------------------------------------------------
        # DEFAULT
        # -------------------------------------------------
        return discord.Embed(
            title=f"🛡️ {event_name} ALERT",
            description="Event notification.",
            color=0x3498db
        ).set_footer(text="Evony Shield Watch")

    # =====================================================
    # EVENT START NOTICE
    # =====================================================

    @staticmethod
    def event_start_notice(event_type: str):

        event_type = (event_type or "").lower()

        if event_type == "svs":

            description = (
                "🔥 SVS is now LIVE.\n\n"
                "🛡️ Bubble immediately.\n"
                "🚫 Stay out of tiles and relics."
            )

        else:

            description = (
                "🔥 KE is now LIVE.\n\n"
                "🛡️ Bubble if needed.\n"
                "✅ Tiles are safe."
            )

        return discord.Embed(
            title=f"{event_type.upper()} STARTED",
            description=description,
            color=0x2ecc71
        ).set_footer(text="Good luck and stay safe.")

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
            description=f"{event_type.upper()} event starting soon.",
            color=0x3498db
        )

        embed.add_field(name="🕐 Start Time", value=start_time, inline=True)
        embed.add_field(name="👤 Coordinator", value=coordinator, inline=True)
        embed.add_field(name="⏳ Check-in Cutoff", value=cutoff, inline=False)

        embed.add_field(
            name="✅ Check-in",
            value="React with ✅ or ❌",
            inline=False
        )

        return embed

    # =====================================================
    # EVENT ROSTER
    # =====================================================

    @staticmethod
    def event_roster(event_name: str, participants: list, reserves: list):

        return discord.Embed(
            title=f"🎯 {event_name} - Final Roster",
            description=(
                f"**Confirmed ({len(participants)})**\n" +
                ("\n".join(f"• {p}" for p in participants) or "None") +
                f"\n\n**Opted Out ({len(reserves)})**\n" +
                ("\n".join(f"• {p}" for p in reserves) or "None")
            ),
            color=0x2ecc71
        )

    # =====================================================
    # HELP
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
            value="/setup\n/linktelegram",
            inline=False
        )

        embed.add_field(
            name="⚔️ Events",
            value="/event_create\n/event_list\n/event_roster",
            inline=False
        )

        embed.add_field(
            name="👤 Personal",
            value="/mytime\n/settimezone\n/optout\n/optin",
            inline=False
        )

        embed.add_field(
            name="📊 Utility",
            value="/ping\n/botinfo\n/stats",
            inline=False
        )

        embed.set_footer(text="Evony Shield Watch")

        return embed
