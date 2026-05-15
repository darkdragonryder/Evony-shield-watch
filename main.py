import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import db
from config import Config

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True


class ShieldWatchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        await db.init()

        cogs = [
            "cogs.setup",
            "cogs.events",
            "cogs.reminders",
            "cogs.custom_events",
            "cogs.admin",
            "cogs.member_cleanup"
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed {cog}: {e}")

        await self.tree.sync()
        print("Slash commands synced")

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="SVS/KE | /help"
            )
        )


bot = ShieldWatchBot()


async def main():
    async with bot:
        await bot.start(Config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
