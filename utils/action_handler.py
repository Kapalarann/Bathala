# utils/action_handler.py

from utils.items import roll_loot, format_loot, ABSTRACT_RESOURCES
from utils.io import load_characters, save_characters

def handle_scavenge(user_id, successes):
    loot = roll_loot(successes)
    loot_text = format_loot(loot)

    characters = load_characters()
    char = characters.get(user_id)
    if not char:
        return "⚠️ Character not found."

    inventory = char.setdefault("inventory", [])

    for item, amt in loot:
        item_key = item.lower()
        if item_key in ABSTRACT_RESOURCES:
            inventory.extend([item_key] * amt)
        else:
            inventory.extend([item] * amt)

    save_characters(characters)
    return loot_text



# Register handlers by action key
ACTION_HANDLERS = {
    "scavenge": handle_scavenge,
    # "cook": handle_cook, etc.
}
