# cogs/character.py

import discord
import copy
import traceback
from discord import app_commands
from discord.ext import commands
import json
import os

from utils.constants import get_default_character, SKILLS, STARTING_SKILL_POINTS, BACKGROUNDS

DATA_PATH = "data/characters.json"

from utils.io import load_characters, save_characters
from utils.hunger_thirst import update_hunger_thirst, get_hunger_thirst_percent

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_character", description="Create your survivor character")
    async def create_character(self, interaction: discord.Interaction,
                               name: str,
                               background: str):
        try:
            print("🟩 Command called.")
            user_id = str(interaction.user.id)
            print(f"User ID: {user_id}")

            characters = load_characters()
            print("Characters loaded.")

            if user_id in characters:
                await interaction.response.send_message("You already have a character.", ephemeral=True)
                print("❗ Character already exists.")
                return

            if background not in BACKGROUNDS:
                await interaction.response.send_message("Invalid background. Use `/backgrounds` to see available options.", ephemeral=True)
                print(f"❗ Invalid background: {background}")
                return

            new_character = get_default_character()
            print("Default character copied.")

            new_character["name"] = name
            new_character["background"] = background
            new_character["skills"] = get_default_character()["skills"].copy()
            
            # Give Skill Bonus
            bonuses = BACKGROUNDS[background]["skills"]
            for skill, bonus in bonuses.items():
                if skill in new_character["skills"]:
                    new_character["skills"][skill] += bonus
                    
            # Give starting equipment
            char_equipment = BACKGROUNDS[background].get("equipment", [])
            new_character["inventory"] = char_equipment.copy()

            characters[user_id] = new_character
            save_characters(characters)
            print("Character saved.")

            await interaction.response.send_message(
                f"✅ Character **{name}** created with background **{background}**!\n"
                f"Now use `/allocate_skills` to assign your skill points.",
                ephemeral=True
            )
            print("✅ Interaction responded successfully.")

        except Exception as e:
            traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"🟥 Error in /create_character:\n{traceback_str}")
            try:
                await interaction.response.send_message("❌ An error occurred. Please try again.", ephemeral=True)
            except:
                pass  # prevents double-send crash

    @app_commands.command(name="allocate_skills", description="Distribute your starting skill points.")
    async def allocate_skills(self, interaction: discord.Interaction,
                              scavenging: int = 0,
                              crafting: int = 0,
                              farming: int = 0,
                              cooking: int = 0,
                              melee: int = 0,
                              ranged: int = 0,
                              medical: int = 0,
                              stealth: int = 0):
        user_id = str(interaction.user.id)
        characters = load_characters()

        if user_id not in characters:
            await interaction.response.send_message("You don't have a character. Use `/create_character`.", ephemeral=True)
            return

        char = characters[user_id]

        if char.get("allocated"):
            await interaction.response.send_message("You've already allocated your skill points.", ephemeral=True)
            return

        inputs = {
            "Scavenging": scavenging,
            "Crafting": crafting,
            "Farming": farming,
            "Cooking": cooking,
            "Melee": melee,
            "Ranged": ranged,
            "Medical": medical,
            "Stealth": stealth,
        }

        total = sum(inputs.values())
        if total > char["unallocated_points"]:
            await interaction.response.send_message(f"You have {char['unallocated_points']} points. You tried to spend {total}.", ephemeral=True)
            return

        # Soft cap enforcement
        for skill, value in inputs.items():
            if value > 3:
                await interaction.response.send_message(f"You cannot assign more than 3 points to {skill} at creation.", ephemeral=True)
                return

        for skill, value in inputs.items():
            char["skills"][skill] += value

        char["unallocated_points"] -= total
        char["allocated"] = True
        save_characters(characters)

        await interaction.response.send_message("✅ Skills allocated successfully!", ephemeral=True)
    
    @app_commands.command(name="backgrounds", description="List all available backgrounds")
    async def backgrounds(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Available Backgrounds",
            description="Each background grants skill bonuses and starting equipment.",
            color=discord.Color.green()
        )

        for name, info in BACKGROUNDS.items():
            skills = info.get("skills", {})
            equipment = info.get("equipment", [])

            # Create skill table
            skill_table = "\n".join([f"> {skill}: +{bonus}" for skill, bonus in skills.items()])

            # Create equipment list
            equipment_table = "\n".join([f"> {item}" for item in equipment]) if equipment else "> None"

            # Final compact field
            value = (
                f"*{info['description']}*\n"
                f" 🧠 **Skills:**\n{skill_table}\n"
                f" 🎒 **Equipment:**\n{equipment_table}"
            )

            embed.add_field(name=f"\n🧍 {name}", value=value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="set_character_image", description="Set your character's profile image using a direct image URL.")
    @app_commands.describe(image_url="Direct image URL (must end in .png, .jpg, etc.)")
    async def set_character_image(self, interaction: discord.Interaction, image_url: str):
        try:
            user_id = str(interaction.user.id)
            characters = load_characters()

            if user_id not in characters:
                await interaction.response.send_message("You don't have a character yet. Use `/create_character` first.", ephemeral=True)
                return

            characters[user_id]["image"] = image_url
            save_characters(characters)

            await interaction.response.send_message("🖼️ Character image set successfully!", ephemeral=True)

        except Exception as e:
            traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"🟥 Error in /set_character_image:\n{traceback_str}")
            try:
                await interaction.response.send_message("❌ An error occurred while setting the image.", ephemeral=True)
            except:
                pass

        
    @app_commands.command(name="check", description="Check character stats")
    async def check(self, interaction: discord.Interaction):
        try:
            print(f"🟢 /check triggered by {interaction.user}")
            user_id = str(interaction.user.id)
            characters = load_characters()

            if user_id not in characters:
                await interaction.response.send_message("You don't have a character yet. Use `/create_character` to begin.", ephemeral=True)
                return

            char = characters[user_id]

            # ⏱️ Update hunger/thirst on every check
            update_hunger_thirst(char)
            save_characters(characters)

            # Extract data
            name = char["name"]
            background = char["background"]
            hp = char["hp"]
            injury = char.get("injury", "None")
            skills = char.get("skills", {})
            inventory = char.get("inventory", [])
            equipped = [item for item in inventory if item.startswith("E:")]

            hunger_thirst = get_hunger_thirst_percent(char)
            hunger_percent = hunger_thirst["hunger_percent"]
            thirst_percent = hunger_thirst["thirst_percent"]

            # Build embed
            embed = discord.Embed(title=f"🧍 {name}'s Character Sheet", color=discord.Color.orange())
            if "image" in char and char["image"]:
                embed.set_thumbnail(url=char["image"])
            embed.add_field(name="Background", value=background, inline=True)
            embed.add_field(name="HP", value=f"{hp}/100", inline=True)
            embed.add_field(name="Injury", value=injury or "None", inline=True)
            embed.add_field(name="🍗 Hunger", value=f"{hunger_percent}%", inline=True)
            embed.add_field(name="💧 Thirst", value=f"{thirst_percent}%", inline=True)

            skill_list = "\n".join([f"• {skill}: {level}" for skill, level in skills.items()])
            embed.add_field(name="📈 Skills", value=skill_list or "No skills yet", inline=False)

            from collections import Counter

            if equipped:
                equipped_names = [item[2:] for item in equipped]
                equipped_counts = Counter(equipped_names)
                equip_list = "\n".join(
                    f"• {name} x{count}" if count > 1 else f"• {name}"
                    for name, count in equipped_counts.items()
                )
                embed.add_field(name="🛠️ Equipped", value=equip_list, inline=False)

            if inventory:
                visible_inventory = [item for item in inventory if not item.startswith("E:")]
                inv_counts = Counter(visible_inventory)
                item_list = "\n".join(
                    f"• {name} x{count}" if count > 1 else f"• {name}"
                    for name, count in inv_counts.items()
                )
                embed.add_field(name="🎒 Inventory", value=item_list or "Empty", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except Exception as e:
            import traceback
            traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"🟥 Error in /check:\n{traceback_str}")
            try:
                await interaction.response.send_message("❌ An error occurred while checking your character.", ephemeral=False)
            except:
                pass
                
    @app_commands.command(name="kill", description="(Admin) Kill a character and remove them from the game.")
    @app_commands.describe(user="The user whose character will be deleted.")
    @app_commands.checks.has_permissions(administrator=True)
    async def kill(self, interaction: discord.Interaction, user: discord.User):
        user_id = str(user.id)
        characters = load_characters()
        char = characters[user_id]

        if user_id not in characters:
            await interaction.response.send_message(f"{user.display_name} has no character.", ephemeral=True)
            return

        name = char["name"]
        
        del characters[user_id]
        save_characters(characters)

        await interaction.response.send_message(f"☠️ **{name}** has been killed and removed.")


async def setup(bot):
    await bot.add_cog(Character(bot))
