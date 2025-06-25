from datetime import datetime
from utils.io import load_characters, save_characters  # adjust if needed

characters = load_characters()
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

for char in characters.values():
    char["last_tick"] = now

save_characters(characters)
print("✅ All characters updated with current last_tick.")
