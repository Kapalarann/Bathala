# cogs/hunger_thirst.py

import discord
from discord import app_commands
from discord.ext import commands

from utils.io import load_characters, save_characters
from utils.hunger_thirst import MAX_HUNGER, MAX_THIRST, update_hunger_thirst, eat, drink, get_hunger_thirst_percent
from utils.inventory import remove_item

class HungerThirst(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="eat", description="Consume food to restore hunger.")
    async def eat_command(self, interaction: discord.Interaction, amount: int):
        user_id = str(interaction.user.id)
        characters = load_characters()

        if user_id not in characters:
            await interaction.response.send_message("You don't have a character yet.", ephemeral=True)
            return

        char = characters[user_id]

        success, removed, _ = remove_item(char, "food", amount)
        if not success:
            await interaction.response.send_message(f"❌ You don't have enough food to eat ({removed}/{amount}).", ephemeral=True)
            return

        update_hunger_thirst(char)
        eat(char, amount)
        save_characters(characters)

        percent = get_hunger_thirst_percent(char)["hunger_percent"]
        await interaction.response.send_message(f"🍗 You ate food and restored hunger. Hunger is now {percent}%.")

    @app_commands.command(name="drink", description="Consume water to restore thirst.")
    async def drink_command(self, interaction: discord.Interaction, amount: int):
        user_id = str(interaction.user.id)
        characters = load_characters()

        if user_id not in characters:
            await interaction.response.send_message("You don't have a character yet.", ephemeral=True)
            return

        char = characters[user_id]

        success, removed, _ = remove_item(char, "water", amount)
        if not success:
            await interaction.response.send_message(f"❌ You don't have enough water to drink ({removed}/{amount}).", ephemeral=True)
            return

        update_hunger_thirst(char)
        drink(char, amount)
        save_characters(characters)

        percent = get_hunger_thirst_percent(char)["thirst_percent"]
        await interaction.response.send_message(f"💧 You drank water and restored thirst. Thirst is now {percent}%.")

async def setup(bot):
    await bot.add_cog(HungerThirst(bot))
