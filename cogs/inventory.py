# cogs/character.py

import discord
import copy
import traceback
from discord import app_commands
from discord.ext import commands
import json
import os

from utils.items import ITEMS, normalize_item_name, ABSTRACT_RESOURCES
from utils.inventory import transfer_item

DATA_PATH = "data/characters.json"

from utils.io import load_characters, save_characters
from utils.base import load_base, save_base

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="equip", description="Equip an item from your inventory.")
    async def equip(self, interaction: discord.Interaction, item: str):
        user_id = str(interaction.user.id)
        characters = load_characters()

        if user_id not in characters:
            await interaction.response.send_message("You have no character.", ephemeral=True)
            return

        char = characters[user_id]
        inv = char["inventory"]

        if f"E:{item}" in inv:
            await interaction.response.send_message("You're already using that.", ephemeral=True)
            return

        if item not in inv:
            await interaction.response.send_message("That item isn't in your inventory.", ephemeral=True)
            return

        inv.remove(item)
        inv.append(f"E:{item}")
        save_characters(characters)

        await interaction.response.send_message(f"✅ Equipped **{item}**.", ephemeral=True)

    @app_commands.command(name="unequip", description="Unequip an equipped item.")
    async def unequip(self, interaction: discord.Interaction, item: str):
        user_id = str(interaction.user.id)
        characters = load_characters()

        if user_id not in characters:
            await interaction.response.send_message("You have no character.", ephemeral=True)
            return

        char = characters[user_id]
        inv = char["inventory"]

        if f"E:{item}" not in inv:
            await interaction.response.send_message("You're not using that item.", ephemeral=True)
            return

        inv.remove(f"E:{item}")
        inv.append(item)
        save_characters(characters)

        await interaction.response.send_message(f"🛑 Unequipped **{item}**.", ephemeral=True)
    
    @app_commands.command(name="give", description="Give an item to another player.")
    @app_commands.describe(
        target="The user to give the item to",
        item="Item to transfer",
        amount="How many to give (for stackable items)"
    )
    async def give(self, interaction: discord.Interaction, target: discord.User, item: str, amount: int = 1):
        giver_id = str(interaction.user.id)
        receiver_id = str(target.id)
        characters = load_characters()

        if giver_id not in characters or receiver_id not in characters:
            await interaction.response.send_message("Both users must have characters.", ephemeral=True)
            return

        success, count, item_name = transfer_item(characters, giver_id, receiver_id, item, amount)
        if not success:
            await interaction.response.send_message(f"❌ You don't have enough **{item_name.title()}** to give.", ephemeral=True)
            return

        save_characters(characters)
        await interaction.response.send_message(f"🎁 You gave {target.display_name} **{count}x {item_name.title()}**.", ephemeral=False)
        
    @app_commands.command(name="store", description="Store an item in the base inventory.")
    @app_commands.describe(
        item="Item to store",
        amount="How many to store (default 1)"
    )
    async def store(self, interaction: discord.Interaction, item: str, amount: int = 1):
        user_id = str(interaction.user.id)
        print(f"🛠️ /store command triggered by user {interaction.user.display_name} ({user_id})")
        print(f"📦 Item: {item}, Amount: {amount}")

        characters = load_characters()
        base = load_base()

        print(f"🔍 Loaded character data: {'yes' if user_id in characters else 'no'}")
        print(f"🏕️ Loaded base inventory: {base.get('inventory', [])}")

        if user_id not in characters:
            print(f"❌ Character for user {user_id} not found.")
            await interaction.response.send_message("❌ You have no character.", ephemeral=True)
            return

        success, count, item_name = transfer_item(characters, user_id, "base", item, amount, base)
        print(f"🔄 transfer_item result: success={success}, count={count}, item_name={item_name}")

        if not success:
            print(f"❌ Transfer failed. User does not have enough '{item_name}'.")
            await interaction.response.send_message(f"❌ You don't have enough **{item_name.title()}** to store.", ephemeral=True)
            return

        save_characters(characters)
        save_base(base)
        print(f"✅ Stored {count}x {item_name} to base inventory")

        await interaction.response.send_message(f"📦 Stored **{count}x {item_name.title()}** in base inventory.", ephemeral=False)

    @app_commands.command(name="take", description="Take an item from the base inventory.")
    @app_commands.describe(
        item="Item to take from base",
        amount="How many to take (default 1)"
    )
    async def take(self, interaction: discord.Interaction, item: str, amount: int = 1):
        user_id = str(interaction.user.id)
        characters = load_characters()
        base = load_base()

        if user_id not in characters:
            await interaction.response.send_message("❌ You have no character.", ephemeral=True)
            return

        success, count, item_name = transfer_item(characters, "base", user_id, item, amount, base)
        if not success:
            await interaction.response.send_message(f"❌ Base doesn't have enough **{item_name.title()}** to take.", ephemeral=True)
            return

        save_characters(characters)
        save_base(base)

        await interaction.response.send_message(f"📥 Took **{count}x {item_name.title()}** from base inventory.", ephemeral=False)
    
    @app_commands.command(name="storage", description="View items stored in the base inventory.")
    async def storage(self, interaction: discord.Interaction):
        base = load_base()
        print("🔍 base loaded:", base)
        print("🔍 type of base:", type(base))
        inventory = base.get("inventory", [])

        if not inventory:
            await interaction.response.send_message("📦 The base inventory is currently empty.", ephemeral=True)
            return
            
        # Count items
        item_counts = {}
        for item in inventory:
            item_counts[item] = item_counts.get(item, 0) + 1

        # Separate abstract resources from gear
        abstract_lines = []
        other_lines = []

        for item, count in item_counts.items():
            item_key = item.lower()
            if item_key in ABSTRACT_RESOURCES:
                emoji_label = ABSTRACT_RESOURCES[item_key]
                abstract_lines.append(f"{emoji_label}: **{count} units**")
            else:
                other_lines.append(f"• {item} x{count}")

        # Create embed
        embed = discord.Embed(
            title="🏕️ Base Storage",
            color=discord.Color.dark_teal()
        )

        if abstract_lines:
            embed.add_field(name="📊 Resources", value="\n".join(abstract_lines), inline=False)

        if other_lines:
            embed.add_field(name="📦 Items", value="\n".join(other_lines), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Inventory(bot))