# utils/hunger_thirst.py

from datetime import datetime, timedelta

from utils.io import load_characters, save_characters

MAX_HUNGER = 120
MAX_THIRST = 72

HUNGER_PER_FOOD = 24
THIRST_PER_DRINK = 24

def update_hunger_thirst(character, current_time=None):
    if current_time is None:
        current_time = datetime.utcnow()

    last_tick_str = character.get("last_tick")
    if not last_tick_str:
        character["last_tick"] = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        return character

    last_tick = datetime.strptime(last_tick_str, "%Y-%m-%dT%H:%M:%S")
    elapsed = current_time - last_tick
    elapsed_hours = int(elapsed.total_seconds() // 3600)

    if elapsed_hours <= 0:
        return character

    character["hunger"] = max(0, character.get("hunger", MAX_HUNGER) - elapsed_hours)
    character["thirst"] = max(0, character.get("thirst", MAX_THIRST) - elapsed_hours)

    # Update to the last full hour mark
    new_tick = last_tick + timedelta(hours=elapsed_hours)
    character["last_tick"] = new_tick.strftime("%Y-%m-%dT%H:%M:%S")

    return character

def eat(character, food_value):
    character["hunger"] = min(MAX_HUNGER, character.get("hunger", MAX_HUNGER) + (food_value * HUNGER_PER_FOOD))
    return character

def drink(character, water_value):
    character["thirst"] = min(MAX_THIRST, character.get("thirst", MAX_THIRST) + (water_value * THIRST_PER_DRINK))
    return character

def get_hunger_thirst_percent(character):
    hunger = character.get("hunger", MAX_HUNGER)
    thirst = character.get("thirst", MAX_THIRST)
    return {
        "hunger_percent": round(hunger / MAX_HUNGER * 100, 1),
        "thirst_percent": round(thirst / MAX_THIRST * 100, 1)
    }

