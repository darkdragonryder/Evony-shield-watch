"""
=========================================================
Evony Shield Watch
Main Entry Point (STABLE ORCHESTRATION LAYER)
=========================================================
"""

import asyncio
import discord

from discord.ext import commands
from dotenv import load_dotenv

from database import db
from config import Config
from services.telegram_bot import TelegramBotService


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.reactions = True
intents.message_content = True


# =========================================================
# BOT CORE
# =========================================================

class ShieldWatchBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        # SINGLE Telegram instance (source of truth)
        self.telegram = TelegramBotService()

        self._telegram_started = False

    # =====================================================
    # SETUP HOOK
    # =====================================================

    async def setup_hook(self):

        print("\n================ DATABASE ================\n")

        await db.init()
        print("✅ Database ready")

        # ---------------- COGS ----------------
        cogs = [
            "cogs.setup",
            "cogs.events",
            "cogs.custom_events",
            "cogs.reminders",
            "cogs.admin",
        ]

        print("\n================ COGS ================\n")

        for cog in cogs:

            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")

            except Exception as e:
                print(f"❌ Failed {cog}: {e}")

        # ---------------- SYNC ----------------
        print("\n================ SLASH SYNC ================\n")

        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} commands")

        except Exception as e:
            print(f"❌ Slash sync failed: {e}")

    # =====================================================
    # READY EVENT
    # =====================================================

    async def on_ready(self):

        print("\n================ ONLINE ================\n")

        print(f"🛡️ Bot: {self.user}")
        print(f"📊 Servers: {len(self.guilds)}")

        # ---------------- PRESENCE ----------------
        try:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="SVS / KE | /help"
                )
            )
        except:
            pass

        # ---------------- TELEGRAM START ----------------
        if not self._telegram_started:

            print("\n================ TELEGRAM ================\n")

            try:

                await self.telegram.start_async()
                self._telegram_started = True

                print("✅ Telegram started safely")

            except Exception as e:
                print(f"❌ Telegram failed: {e}")

    # =====================================================
    # GUILD JOIN
    # =====================================================

    async def on_guild_join(self, guild):

        print(f"➕ Joined {guild.name}")

        await db.set_server_config(guild.id)

    # =====================================================
    # MEMBER JOIN
    # =====================================================

    async def on_member_join(self, member):

        if member.bot:
            return

        try:

            embed = discord.Embed(
                title="🛡️ Welcome to Evony Shield Watch",
                description=(
                    "Get SVS / KE alerts and bubble reminders.\n\n"
                    "Use `/settimezone` to configure your local time."
                ),
                color=0x3498db
            )

            await member.send(embed=embed)

        except:
            pass

    # =====================================================
    # MEMBER CLEANUP
    # =====================================================

    async def on_member_remove(self, member):

        if member.bot:
            return

        await db.delete_member_data(member.id)

    # =====================================================
    # SAFE SHUTDOWN
    # =====================================================

    async def close(self):

        print("\n================ SHUTDOWN ================\n")

        try:

            await self.telegram.stop_async()

        except Exception as e:
            print(f"Telegram shutdown warning: {e}")

        await super().close()


# =========================================================
# ERROR HANDLER
# =========================================================

@commands.Cog.listener()
async def on_app_command_error(interaction, error):

    try:

        if interaction.response.is_done():
            return

        await interaction.response.send_message(
            "❌ Error occurred.",
            ephemeral=True
        )

    except:
        pass


# =========================================================
# RUNNER
# =========================================================

async def main():

    async with ShieldWatchBot() as bot:
        await bot.start(Config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
