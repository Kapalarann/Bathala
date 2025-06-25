# cogs/group_actions.py

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

from utils.io import load_characters, save_characters
from utils.items import ITEMS
from utils.actions import ACTIONS
from utils.action_handler import ACTION_HANDLERS
from utils.base import load_base, save_base
from utils.items import roll_loot, format_loot
from utils.rolls import BASE_DICE, roll_dice_pool, calculate_successes, reroll_lowest, format_grouproll_embed

REACTION_ADD = "➕"   # ➕ Add Die
REACTION_REROLL = "🔁"  # 🔁 Reroll Lowest
REACTION_SUBMIT = "✅"  # ✅ Submit

class GroupActions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.group_sessions = {}  # {message_id: {"leader": user_id, "action": str, "members": set(user_id)}}
        self.active_group_rolls = {}

    @app_commands.command(name="group_action", description="Start a group action that others can join")
    @app_commands.describe(action="The group action you want to perform")
    async def group_action(self, interaction: discord.Interaction, action: str):
        if action not in ACTIONS:
            await interaction.response.send_message("Invalid action.", ephemeral=True)
            return

        user_id = str(interaction.user.id)

        embed = discord.Embed(
            title=f"👥 Group Action: {ACTIONS[action]['name']}",
            description="React with ✅ to join. Leader reacts with 🚀 to start.",
            color=discord.Color.purple()
        )
        embed.add_field(name="Description", value=ACTIONS[action]['description'], inline=False)
        embed.set_footer(text="Only the leader can launch the action.")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("✅")
        await message.add_reaction("🚀")

        # Register session for async reaction handler
        self.group_sessions[message.id] = {
            "leader": interaction.user.id,
            "action": action,
            "members": {interaction.user.id},  # Leader auto-joins
            "message": message
        }

        print(f"[GROUP] Created group action session for message {message.id}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        message_id = reaction.message.id

        # --- Handle Group Lobby Join/Launch ---
        if message_id in self.group_sessions:
            session = self.group_sessions[message_id]
            action_key = session["action"]
            print(f"[GROUP-LOBBY] Reaction from {user.display_name}: {reaction.emoji}")

            if reaction.emoji == "✅":
                if user.id not in session["members"]:
                    session["members"].add(user.id)
                    await reaction.message.channel.send(f"✅ {user.display_name} joined the group action!", delete_after=5)

            elif reaction.emoji == "🚀" and user.id == session["leader"]:
                await self.launch_group_action(session)
                del self.group_sessions[message_id]

            await reaction.remove(user)
            return  # ✅ Done handling lobby

        # --- Handle Group Action Roll Phase ---
        if message_id in self.active_group_rolls:
            data = self.active_group_rolls[message_id]
            user_id = user.id

            if user_id not in data["members"]:
                return  # Not a participant

            member_data = data["members"][user_id]
            rolls = data["rolls"]
            history = data["history"]
            submitted = data["submitted"]

            updated = False
            print(f"[GROUP-ROLL] {user.display_name} reacted: {reaction.emoji}")

            if reaction.emoji == REACTION_ADD and member_data["skill_points"] >= 3:
                rolls.append(random.randint(1, 6))
                member_data["skill_points"] -= 3
                updated = True

            elif reaction.emoji == REACTION_REROLL and member_data["skill_points"] >= 1:
                rolls, history = reroll_lowest(rolls, history)
                member_data["skill_points"] -= 1
                data["rolls"] = rolls
                data["history"] = history
                updated = True

            elif reaction.emoji == REACTION_SUBMIT:
                submitted.add(user_id)
                await reaction.message.channel.send(f"✅ {user.display_name} is ready!", delete_after=5)

                if submitted == set(data["members"].keys()):
                    # All users submitted!
                    total_successes = calculate_successes(data["rolls"])
                    action_data = ACTIONS[data["action"]]
                    result_embed = discord.Embed(
                        title=f"🎯 Final Group Result: {action_data['name']}",
                        description=f"🎲 Rolls: {', '.join(map(str, data['rolls']))}\n⭐ Total Successes: **{total_successes}**",
                        color=discord.Color.green()
                    )
                    await reaction.message.channel.send(embed=result_embed)
                    del self.active_group_rolls[message_id]
                    return

            if updated:
                embed = format_grouproll_embed(
                    ACTIONS[data["action"]],
                    rolls,
                    data["members"],
                    history,
                    submitted
                )
                try:
                    channel = reaction.message.channel
                    updated_msg = await channel.fetch_message(message_id)
                    await updated_msg.edit(embed=embed)
                    await updated_msg.remove_reaction(reaction.emoji, user)
                except Exception as e:
                    print(f"[ERROR] Failed to update group roll embed: {e}")

    async def launch_group_action(self, session):
        action_key = session["action"]
        action_data = ACTIONS[action_key]
        skill_required = action_data["skill"]

        characters = load_characters()
        members = {}
        submitted = set()

        # Gather skill data
        for user_id in session["members"]:
            user_id_str = str(user_id)
            char = characters.get(user_id_str)
            user_obj = await self.bot.fetch_user(user_id)

            if not char:
                await session["message"].channel.send(f"❌ <@{user_id}> has no character.")
                continue

            skill_value = char["skills"].get(skill_required, 0)
            inventory = char.get("inventory", [])
            equipped = [i[2:] for i in inventory if i.startswith("E:")]
            tool_bonus = sum(
                ITEMS.get(i, {}).get("bonus", {}).get(skill_required, 0)
                for i in equipped if i in ITEMS
            )
            total_skill = skill_value + tool_bonus
            print(f"[{user_obj.display_name}] Skill: {skill_value}, Tool: {tool_bonus}, Total: {total_skill}")

            members[user_id] = {
                "user": user_obj,
                "skill_points": total_skill
            }

        # Shared roll pool
        shared_rolls = roll_dice_pool(BASE_DICE * len(members))
        history = [shared_rolls.copy()]

        # Create embed
        embed = format_grouproll_embed(action_data, shared_rolls, members, history, submitted)
        roll_msg = await session["message"].channel.send(embed=embed)
        await roll_msg.add_reaction("➕")
        await roll_msg.add_reaction("🔁")
        await roll_msg.add_reaction("✅")

        # Store for ongoing interaction
        self.active_group_rolls = getattr(self, "active_group_rolls", {})
        self.active_group_rolls[roll_msg.id] = {
            "action": action_key,
            "members": members,
            "submitted": submitted,
            "rolls": shared_rolls,
            "history": history,
            "message": roll_msg
        }
        

async def setup(bot):
    await bot.add_cog(GroupActions(bot))
