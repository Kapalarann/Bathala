# utils/constants.py

from datetime import datetime

STARTING_HP = 100
STARTING_SKILL_POINTS = 5

SKILLS = [
    "Scavenging",
    "Crafting",
    "Farming",
    "Cooking",
    "Melee",
    "Ranged",
    "Medical",
    "Stealth"
]

def get_default_character():
    return {
        "name": "",
        "background": "",
        "hp": STARTING_HP,
        "injury": None,
        "skills": {skill: 0 for skill in SKILLS},
        "inventory": [],
        "unallocated_points": 5,
        "allocated": False,
        "image": None,
        "hunger": 120,
        "thirst": 72,
        "last_tick": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
    }

BACKGROUNDS = {
    "Mechanic": {
        "description": "A skilled tinkerer who can fix almost anything.",
        "skills": {
            "Crafting": 2,
            "Scavenging": 2
        },
        "equipment": ["E:Wrench", "Duct Tape", "Screwdriver"]
    },
    "Hunter": {
        "description": "Experienced in the wild. Knows how to hunt and stay hidden.",
        "skills": {
            "Ranged": 2,
            "Stealth": 1,
            "Scavenging": 1
        },
        "equipment": ["E:Hunting Bow", "Arrows x10", "Camo Jacket"]
    },
    "Medic": {
        "description": "Trained in medical aid, vital for survival.",
        "skills": {
            "Medical": 3,
            "Melee": 1
        },
        "equipment": ["E:Medical Kit", "Bandage x2", "Painkillers"]
    },
    "Cook": {
        "description": "Knows how to turn scraps into a morale-boosting meal.",
        "skills": {
            "Cooking": 3,
            "Farming": 1
        },
        "equipment": ["E:Frying Pan", "Cooking Oil", "Can of Beans"]
    },
    "Scavenger": {
        "description": "Fast, quiet, and efficient when looting.",
        "skills": {
            "Scavenging": 2,
            "Stealth": 2
        },
        "equipment": ["E:Crowbar", "Flashlight", "Rucksack"]
    },
    "Farmer": {
        "description": "Knows how to keep food growing and soil healthy.",
        "skills": {
            "Farming": 3,
            "Ranged": 1
        },
        "equipment": ["E:Hoe", "Seed Packet", "Work Gloves"]
    },
    "Soldier": {
        "description": "Trained in combat. Keeps zombies off your back.",
        "skills": {
            "Melee": 1,
            "Ranged": 2,
            "Medical": 1
        },
        "equipment": ["E:Pistol", "Ammo x10", "Combat Knife", "Bandage"]
    }
}
