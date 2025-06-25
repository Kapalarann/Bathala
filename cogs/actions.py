# cogs/actions.py

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random

from utils.constants import SKILLS
from utils.actions import ACTIONS
from utils.action_handler import ACTION_HANDLERS
from utils.items import ITEMS, roll_loot, format_loot, ABSTRACT_RESOURCES
from utils.base import load_base, save_base
from utils.io import load_characters, save_characters
from utils.rolls import BASE_DICE, roll_dice_pool, calculate_successes, reroll_lowest, format_roll_embed

DATA_PATH = "data/characters.json"

REACTION_ADD = "➕"   # ➕ Add Die
REACTION_REROLL = "🔁"  # 🔁 Reroll Lowest
REACTION_SUBMIT = "✅"  # ✅ Submit

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_actions = {}  # Track users who already acted
        self.active_rolls = {}  # Track ongoing rolls

    @app_commands.command(name="do_action", description="Perform a daily action to help the camp")
    @app_commands.describe(action="The action you want to take")
    async def do_action(self, interaction: discord.Interaction, action: str):
        print("/do_action command received")
        user_id = str(interaction.user.id)

        if self.daily_actions.get(user_id):
            await interaction.response.send_message("You already did an action today.", ephemeral=True)
            return

        characters = load_characters()
        print("Loaded characters")
        if user_id not in characters:
            await interaction.response.send_message("You need to create a character first.", ephemeral=True)
            return

        if action not in ACTIONS:
            await interaction.response.send_message("Invalid action.", ephemeral=True)
            return

        char = characters[user_id]
        skill_name = ACTIONS[action]["skill"]
        skill_value = char["skills"].get(skill_name, 0)
        inventory = char.get("inventory", [])

        equipped = [i[2:] for i in inventory if i.startswith("E:")]
        tool_bonus = sum(
            ITEMS[i].get("bonus", {}).get(skill_name, 0)
            for i in equipped if i in ITEMS
        )

        total_skill = skill_value + tool_bonus
        print(f"Skill value: {skill_value}, Tool bonus: {tool_bonus}, Total skill: {total_skill}")

        rolls = roll_dice_pool(BASE_DICE)
        embed = format_roll_embed(interaction.user, ACTIONS[action], rolls, skill_name, total_skill, [rolls.copy()])

        try:
            await interaction.response.send_message(embed=embed, ephemeral=False)
            message = await interaction.original_response()
            print("Sent initial roll message")
            await message.add_reaction(REACTION_ADD)
            await message.add_reaction(REACTION_REROLL)
            await message.add_reaction(REACTION_SUBMIT)
            print("Added reactions")
        except Exception as e:
            print(f"Error sending message or adding reactions: {e}")
            return

        self.active_rolls[message.id] = {
            "user_id": user_id,
            "action": action,
            "rolls": rolls,
            "skill": skill_name,
            "skill_points": total_skill,
            "message": message,
            "interaction": interaction,
            "history": [rolls.copy()]
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or reaction.message.id not in self.active_rolls:
            return

        data = self.active_rolls[reaction.message.id]
        if str(user.id) != data["user_id"]:
            return

        rolls = data["rolls"]
        skill_points = data["skill_points"]

        print("Reaction valid")
        updated = False

        if reaction.emoji == REACTION_ADD and skill_points >= 3:
            rolls.append(random.randint(1, 6))
            data["skill_points"] -= 3
            print("Added die")
            updated = True

        elif reaction.emoji == REACTION_REROLL and skill_points >= 1:
            rolls, history = reroll_lowest(rolls, data["history"])
            data["skill_points"] -= 1
            data["rolls"] = rolls
            data["history"] = history
            print("Rerolled lowest")
            updated = True

        elif reaction.emoji == REACTION_SUBMIT:
            successes = calculate_successes(rolls)
            handler = ACTION_HANDLERS.get(data["action"])
            extra_message = ""
            if handler:
                result_text = handler(data["user_id"], successes)
                extra_message = f"\n\n📦 Result:\n{result_text}"

            result_embed = discord.Embed(
                title=f"✅ Final Result: {ACTIONS[data['action']]['name']}",
                description=f"{user.display_name} achieved **{successes} successes** with rolls: {', '.join(map(str, rolls))}{extra_message}",
                color=discord.Color.green()
            )
            await reaction.message.channel.send(embed=result_embed)

            self.daily_actions[data["user_id"]] = True
            del self.active_rolls[reaction.message.id]
            print("Submitted result")
            return

        if updated:
            action_data = ACTIONS[data["action"]]
            new_embed = format_roll_embed(user, action_data, rolls, data["skill"], data["skill_points"], data["history"])

            # 🔧 Fetch the latest version of the message
            try:
                channel = reaction.message.channel
                updated_message = await channel.fetch_message(reaction.message.id)
                await updated_message.edit(embed=new_embed)
                await updated_message.remove_reaction(reaction.emoji, user)
                print("✅ Updated embed and removed reaction")
            except Exception as e:
                print(f"❌ Failed to update embed: {e}")

    @app_commands.command(name="list_actions", description="List available actions")
    async def list_actions(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧭 Available Actions", color=discord.Color.blue())
        for key, data in ACTIONS.items():
            embed.add_field(name=f"🛠️ {data['name']} (`{key}`)", value=data["description"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Actions(bot))