# bot.py
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True  # Needed for legacy commands
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}!")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s): {[cmd.name for cmd in synced]}")

async def main():
    async with bot:
        await bot.load_extension("cogs.hunger_thirst")
        await bot.load_extension("cogs.group_actions")
        await bot.load_extension("cogs.actions")
        await bot.load_extension("cogs.character")
        await bot.load_extension("cogs.inventory")
        await bot.start("MTM4NjM4OTY1Mzc5NTYzOTM4Nw.GOCYl7.ktU2SAAEOAFrXwXuZiOkr2xXJ8t82bYCfQHb-I")
        
if __name__ == "__main__":
    asyncio.run(main())