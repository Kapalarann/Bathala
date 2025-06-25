# utils/rolls.py

import discord
import random
from utils.actions import ACTIONS

BASE_DICE = 3
SUCCESS_THRESHOLD = 4
CRIT = 6
FAIL = 1

def roll_dice_pool(num_dice):
        print(f"Rolling {num_dice} dice")
        return [random.randint(1, 6) for _ in range(num_dice)]

def calculate_successes(rolls):
    success = 0
    for die in rolls:
        if die == CRIT:
            success += 2
        elif die >= SUCCESS_THRESHOLD:
            success += 1
        elif die == FAIL:
            success -= 1
    print(f"Calculated successes: {success} from rolls: {rolls}")
    return success

def reroll_lowest(rolls, history):
    if not rolls:
        return rolls, history
    min_value = min(rolls)
    old_rolls = rolls.copy()
    for i in range(len(rolls)):
        if rolls[i] == min_value:
            rolls[i] = random.randint(1, 6)
            break
    history.append(old_rolls)
    print(f"Rerolled lowest: {old_rolls} → {rolls}")
    return rolls, history
    
def format_roll_embed(user, action, rolls, skill_name, skill_points, history):
    print("[format_roll_embed] Called with:")
    print(f"  User: {user.display_name} (ID: {user.id})")
    print(f"  Action: {action}")
    print(f"  Rolls: {rolls}")
    print(f"  Skill Name: {skill_name}")
    print(f"  Skill Points: {skill_points}")
    print(f"  History: {history}")

    success_count = calculate_successes(rolls)

    roll_str = ", ".join(str(r) for r in rolls)
    print(f"  Roll String: {roll_str}")

    embed = discord.Embed(
        title=f"📃 Action: {action['name']}",
        description=f"**Current Rolls:** {roll_str}",
        color=discord.Color.orange()
    )
    embed.add_field(name="User", value=user.display_name, inline=True)
    embed.add_field(name="Skill", value=skill_name, inline=True)
    embed.add_field(name="✅ Successes", value=success_count, inline=True)
    embed.add_field(name="🧠 Remaining Skill Points", value=skill_points, inline=True)

    if len(history) > 1:
        history_text = "\n".join([f"• {', '.join(map(str, h))}" for h in history[:-1]])
        embed.add_field(name="🕓 Previous Rolls", value=history_text, inline=False)
        print("  Added previous roll history to embed.")

    print("[format_roll_embed] Embed creation complete.")
    return embed

def format_grouproll_embed(action, rolls, members, history, submitted):
    """
    - action: dict from ACTIONS (e.g. ACTIONS["scavenge"])
    - rolls: shared list of ints (all player dice)
    - members: dict of user_id -> { "user": discord.User, "skill_points": int }
    - history: list of past rolls (list of lists)
    - submitted: set of user_ids who have submitted
    """
    print("[format_grouproll_embed] Called")
    print(f"  Action: {action['name']}")
    print(f"  Rolls: {rolls}")
    print(f"  Members: {list(members.keys())}")
    print(f"  Submitted: {submitted}")
    print(f"  History: {len(history)} entries")

    success_count = calculate_successes(rolls)
    roll_str = ", ".join(str(r) for r in rolls)

    embed = discord.Embed(
        title=f"👥 Group Action: {action['name']}",
        description=f"🎲 **Current Rolls:** {roll_str}",
        color=discord.Color.purple()
    )
    
    embed.add_field(name="✅ Group Successes", value=str(success_count), inline=True)

    submitted_names = []
    waiting_names = []

    for user_id, data in members.items():
        name = data["user"].display_name
        points = data["skill_points"]
        label = f"{name} ({points}🧠 left)"
        if user_id in submitted:
            submitted_names.append(f"✅ {label}")
        else:
            waiting_names.append(f"⏳ {label}")

    embed.add_field(name="📤 Submitted", value="\n".join(submitted_names) or "None", inline=False)
    embed.add_field(name="⌛ Waiting", value="\n".join(waiting_names) or "None", inline=False)

    if len(history) > 1:
        history_text = "\n".join([f"• {', '.join(map(str, h))}" for h in history[:-1]])
        embed.add_field(name="🕓 Previous Rolls", value=history_text, inline=False)

    print("[format_grouproll_embed] Embed creation complete.")
    return embed
