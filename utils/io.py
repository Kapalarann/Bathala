# utils/io.py

import json
import os

CHARACTER_DATA_PATH = "data/characters.json"

def load_characters():
    if not os.path.exists(CHARACTER_DATA_PATH):
        return {}
    with open(CHARACTER_DATA_PATH, "r") as f:
        return json.load(f)

def save_characters(data):
    with open(CHARACTER_DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
