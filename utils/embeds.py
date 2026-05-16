"""
Evony Shield Watch
Embed Templates (POLISHED UI LAYER)
Clean + Fancy + Stable
"""

import discord


class Embeds:

    # =====================================================
    # SHIELD ALERTS
    # =====================================================

    @staticmethod
    def shield_alert(event_type: str, phase: str = "warning"):

        event_type = (event_type or "svs").lower()

        embed = discord.Embed(
            color=0x2f3136
        )

        if event_type == "svs" and phase == "warning":
            embed.title = "🚨 SVS WARNING"
            embed.description = (
                "Server War is approaching.\n\n"
                "🛡️ Activate shields soon\n"
                "⏳ Prepare for hostilities"
            )
            embed.color = 0xffa500

        elif event_type == "svs" and phase == "start":
            embed.title = "🔥 SVS ACTIVE"
            embed.description = (
                "Server War has begun!\n\n"
                "🛡️ Shield immediately if not fighting\n"
                "⚔️ Avoid high-risk zones"
            )
            embed.color = 0xff3b30

        elif event_type == "ke" and phase == "warning":
            embed.title = "⚔️ KE WARNING"
            embed.description = (
                "Kill Event is approaching.\n\n"
                "🛡️ Prepare shields if needed\n"
                "⚠️ Combat window opening soon"
            )
            embed.color = 0xffa500

        elif event_type == "ke" and phase == "start":
            embed.title = "🔥 KE ACTIVE"
            embed.description = (
                "Kill Event is now LIVE.\n\n"
                "⚔️ PvP enabled\n"
                "🛡️ Stay protected if farming"
            )
            embed.color = 0x2ecc71

        else:
            embed.title = f"🛡️ {event_type.upper()} ALERT"
            embed.description = "Event notification active."
            embed.color = 0x3498db

        embed.set_footer(text="Evony Shield Watch")
        return embed

    # =====================================================
    # EVENT START
    # =====================================================

    @staticmethod
    def event_start_notice(event_type: str):

        event_type = (event_type or "svs").lower()

        if event_type == "svs":
            return discord.Embed(
                title="🔥 SVS HAS BEGUN",
                description=(
                    "Server War is now active.\n\n"
                    "🛡️ Maintain shields\n"
                    "⚔️ Stay alert"
                ),
                color=0xff3b30
            ).set_footer(text="Evony Shield Watch")

        return discord.Embed(
            title="🔥 KE HAS BEGUN",
            description=(
                "Kill Event is now active.\n\n"
                "⚔️ PvP enabled\n"
                "🛡️ Play smart"
            ),
            color=0x2ecc71
        ).set_footer(text="Evony Shield Watch")

    # =====================================================
    # CUSTOM EVENT CHECKIN
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
            description=f"**{event_type.upper()} EVENT CHECK-IN OPEN**",
            color=0x3498db
        )

        embed.add_field(name="🕐 Start Time", value=start_time, inline=True)
        embed.add_field(name="👤 Coordinator", value=coordinator, inline=True)
        embed.add_field(name="⏳ Cutoff", value=cutoff, inline=False)
        embed.add_field(name="✅ Status", value="React ✅ / ❌ to respond", inline=False)

        embed.set_footer(text="Evony Shield Watch")
        return embed

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

        embed.set_footer(text="Evony Shield Watch")
        return embed

    # =====================================================
    # HELP
    # =====================================================

    @staticmethod
    def help_command():

        return discord.Embed(
            title="📖 Evony Shield Watch",
            description="Available Commands",
            color=0x34495e
        ).add_field(
            name="Setup",
            value="/setup • /linktelegram",
            inline=False
        ).add_field(
            name="Events",
            value="/event_create • /event_list",
            inline=False
        ).add_field(
            name="Utility",
            value="/ping • /botinfo • /stats",
            inline=False
        ).add_field(
            name="Personal",
            value="/mytime • /settimezone • /optin • /optout",
            inline=False
        ).set_footer(text="Evony Shield Watch")
