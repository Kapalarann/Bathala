# utils/base.py

import json
import os

BASE_PATH = "data/base.json"

def load_base():
    if not os.path.exists(BASE_PATH):
        print("📂 No base file found. Creating new one.")
        return {"inventory": []}
    try:
        with open(BASE_PATH, "r") as f:
            data = json.load(f)
            if "inventory" not in data:
                print("🔧 No 'inventory' key found. Initializing empty list.")
                data["inventory"] = []
            return data
    except Exception as e:
        print(f"❌ Failed to load base.json: {e}")
        return {"inventory": []}


def save_base(data):
    try:
        with open("data/base.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("⚠️ Error saving base data:", e)
        raise
