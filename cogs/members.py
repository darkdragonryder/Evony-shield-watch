"""
=========================================================
 Evony Shield Watch
 Member Lifecycle System
 (Join / Leave / Ban / Auto Cleanup / Onboarding)
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import discord
from discord.ext import commands

from database import db
from config import Config


# =========================================================
# MEMBERS COG
# =========================================================

class Members(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # MEMBER JOIN (ONBOARDING FLOW)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.bot:
            return

        # -------------------------------------------------
        # ensure DB record exists (lightweight init)
        # -------------------------------------------------

        await db.set_member_contact(member.id)

        # -------------------------------------------------
        # send onboarding DM
        # -------------------------------------------------

        try:

            embed = discord.Embed(
                title="🛡️ Welcome to Evony Shield Watch",
                description=(
                    "To get full alerts for SVS / KE / Events:\n\n"
                    "1️⃣ Set your timezone\n"
                    "2️⃣ (Optional) Link Telegram for instant alerts\n"
                    "3️⃣ Choose opt-in preferences"
                ),
                color=0x1abc9c
            )

            embed.add_field(
                name="🔗 Link Telegram",
                value="Run `/linktelegram` in the server",
                inline=False
            )

            embed.add_field(
                name="⏰ Set Timezone",
                value="Run `/settimezone Europe/London` (example)",
                inline=False
            )

            embed.add_field(
                name="🔕 Controls",
                value="/optout or /optin anytime",
                inline=False
            )

            await member.send(embed=embed)

        except discord.Forbidden:
            pass

    # =====================================================
    # MEMBER LEAVE (AUTO CLEANUP)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if member.bot:
            return

        await db.delete_user_data(member.id)

    # =====================================================
    # MEMBER BAN (SAFE CLEANUP)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):

        if user.bot:
            return

        await db.delete_user_data(user.id)

    # =====================================================
    # MEMBER UNBAN (OPTIONAL RE-INIT)
    # =====================================================

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):

        # Recreate minimal record so user can re-link if needed
        await db.set_member_contact(user.id)


# =========================================================
# SETUP
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Members(bot))
