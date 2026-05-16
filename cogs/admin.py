"""

 Evony Shield Watch
 Admin & Utility Commands

"""

import discord

from discord.ext import commands
from discord import app_commands

from utils.embeds import Embeds
from database import db


# =========================================================
# ADMIN COG
# =========================================================

class Admin(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # HELP
    # =====================================================

    @app_commands.command(
        name="help",
        description="Show all available commands"
    )
    async def slash_help(self, interaction: discord.Interaction):

        embed = Embeds.help_command()

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # BOT INFO
    # =====================================================

    @app_commands.command(
        name="botinfo",
        description="Show bot information"
    )
    async def slash_botinfo(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🛡️ Evony Shield Watch",
            description=(
                "Automated shield and event management "
                "for Evony: Return of the King"
            ),
            color=0x1abc9c
        )

        embed.add_field(
            name="Version",
            value="2.0.0",
            inline=True
        )

        embed.add_field(
            name="Servers",
            value=str(len(self.bot.guilds)),
            inline=True
        )

        embed.add_field(
            name="Users",
            value=str(len(self.bot.users)),
            inline=True
        )

        embed.add_field(
            name="Features",
            value=(
                "• Auto SVS / KE rotation\n"
                "• Bubble reminders\n"
                "• Battlefield alerts\n"
                "• Telegram notifications\n"
                "• Custom event tracking\n"
                "• Event check-in system\n"
                "• Auto member cleanup\n"
                "• Dashboard-ready structure"
            ),
            inline=False
        )

        embed.set_footer(
            text="Evony Shield Watch"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # PING
    # =====================================================

    @app_commands.command(
        name="ping",
        description="Check bot latency"
    )
    async def slash_ping(self, interaction: discord.Interaction):

        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"🏓 Pong! `{latency}ms`",
            ephemeral=True
        )

    # =====================================================
    # SERVER STATS
    # =====================================================

    @app_commands.command(
        name="stats",
        description="Show server stats"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_stats(self, interaction: discord.Interaction):

        config = await db.get_server_config(
            interaction.guild_id
        )

        schedule = await db.get_event_schedule(
            interaction.guild_id
        )

        embed = discord.Embed(
            title=f"📊 {interaction.guild.name} Stats",
            color=0x34495e
        )

        # -------------------------------------------------
        # CHANNELS
        # -------------------------------------------------

        if config:

            bubble_channel = interaction.guild.get_channel(
                config.get("bubble_channel_id", 0)
            )

            battlefield_channel = interaction.guild.get_channel(
                config.get("battlefield_channel_id", 0)
            )

            embed.add_field(
                name="🫧 Bubble Channel",
                value=(
                    bubble_channel.mention
                    if bubble_channel
                    else "Not set"
                ),
                inline=True
            )

            embed.add_field(
                name="⚔️ Battlefield Channel",
                value=(
                    battlefield_channel.mention
                    if battlefield_channel
                    else "Not set"
                ),
                inline=True
            )

            embed.add_field(
                name="✅ Setup Complete",
                value=(
                    "Yes"
                    if config.get("setup_complete")
                    else "No"
                ),
                inline=True
            )

        # -------------------------------------------------
        # EVENT INFO
        # -------------------------------------------------

        if schedule:

            current_event = schedule.get(
                "current_event",
                "unknown"
            ).upper()

            next_event_date = schedule.get(
                "next_event_date",
                "Unknown"
            )

            embed.add_field(
                name="📅 Current Event",
                value=current_event,
                inline=False
            )

            embed.add_field(
                name="⏰ Next Event Date",
                value=str(next_event_date),
                inline=False
            )

        # -------------------------------------------------
        # MEMBER COUNTS
        # -------------------------------------------------

        total_members = len(
            [m for m in interaction.guild.members if not m.bot]
        )

        bot_count = len(
            [m for m in interaction.guild.members if m.bot]
        )

        embed.add_field(
            name="👥 Human Members",
            value=str(total_members),
            inline=True
        )

        embed.add_field(
            name="🤖 Bots",
            value=str(bot_count),
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # BROADCAST
    # =====================================================

    @app_commands.command(
        name="broadcast",
        description="Send a DM to all server members"
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        message="Message to broadcast"
    )
    async def slash_broadcast(
        self,
        interaction: discord.Interaction,
        message: str
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        sent = 0
        failed = 0

        for member in interaction.guild.members:

            if member.bot:
                continue

            try:

                embed = discord.Embed(
                    title=f"📢 Message from {interaction.guild.name}",
                    description=message,
                    color=0x3498db
                )

                await member.send(embed=embed)

                sent += 1

            except Exception:
                failed += 1

        await interaction.followup.send(
            (
                f"✅ Sent to: {sent}\n"
                f"❌ Failed: {failed}"
            ),
            ephemeral=True
        )


# =========================================================
# COG SETUP
# =========================================================

async def setup(bot: commands.Bot):

    await bot.add_cog(Admin(bot))
