# utils/items.py

import random

def normalize_item_name(item: str) -> str:
    return item[2:].lower() if item.startswith("E:") else item.lower()


ABSTRACT_RESOURCES = {
    "materials": "🧱 Materials",
    "food": "🍖 Food",
    "water": "💧 Water",
    "medicine": "💊 Medicine",
    "fuel": "🔥 Fuel",
    "ammo": "💥 Ammo",
}


ITEMS = {
    "Hunting Bow": {
        "type": "weapon",
        "bonus": {"Ranged": 2}
    },
    "Medical Kit": {
        "type": "tool",
        "bonus": {"Medical": 2}
    },
    "Frying Pan": {
        "type": "tool",
        "bonus": {"Cooking": 1}
    },
    "Crowbar": {
        "type": "tool",
        "bonus": {"Scavenging": 1}
    },
    "Hoe": {
        "type": "tool",
        "bonus": {"Farming": 1}
    },
    "Pistol": {
        "type": "weapon",
        "bonus": {"Ranged": 2}
    },
    "Combat Knife": {
        "type": "weapon",
        "bonus": {"Melee": 2}
    }
    # You can add more items with "durability", "uses", etc.
}

LOOT_TABLE = {
    "common": {
        "weight": 60,
        "items": [
            {"name": "Materials", "amount": (1, 4)},
            {"name": "Food", "amount": (1, 3)},
            {"name": "Water", "amount": (1, 3)},
            {"name": "Medicine"},
        ]
    },
    "uncommon": {
        "weight": 30,
        "items": [
            {"name": "Materials", "amount": (4, 8)},
            {"name": "Food", "amount": (4, 6)},
            {"name": "Water", "amount": (4, 6)},
            {"name": "Medicine", "amount": (2, 3)},
            {"name": "Fuel", "amount": (1, 2)},
            {"name": "Ammo", "amount": (3, 6)},
            {"name": "Hoe"},
            {"name": "Frying Pan"},
            {"name": "Crowbar"},
            {"name": "Knife"}
        ]
    },
    "rare": {
        "weight": 10,
        "items": [
            {"name": "Hunting Bow"},
            {"name": "Combat Knife"},
            {"name": "Medical Kit"},
        ]
    }
}

def choose_rarity():
    rarities = list(LOOT_TABLE.keys())
    weights = [LOOT_TABLE[r]["weight"] for r in rarities]
    return random.choices(rarities, weights=weights, k=1)[0]
    
def roll_loot(successes: int):
    loot_results = []

    for _ in range(successes):
        rarity = choose_rarity()
        item_entry = random.choice(LOOT_TABLE[rarity]["items"])
        name = item_entry["name"]

        if "amount" in item_entry:
            min_amt, max_amt = item_entry["amount"]
            amount = random.randint(min_amt, max_amt)
            loot_results.append((name, amount))
        else:
            loot_results.append((name, 1))  # One of a non-stackable item

    return loot_results

def format_loot(loot):
    summary = {}
    for item, amt in loot:
        summary[item] = summary.get(item, 0) + amt
    return "\n".join([f"• {item} x{amt}" for item, amt in summary.items()])
