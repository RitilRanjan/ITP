import os
import json

def process_file(filepath):
    with open(filepath, 'r') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return
            
    modified = False
    if "start_env" in data:
        val = data.pop("start_env")
        modified = True
        
        if val == "level16_env.md":
            data["start_env_commands"] = [
                "cv x y",
                "cf theorem_1 ∃y ∀x x ∈ y",
                "force theorem_1"
            ]
        elif val == "level6_start_env.md" or val == "level6_start_env.txt":
            pass # Already converted earlier, just popping is enough

    if modified:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk('games'):
    for file in files:
        if file.endswith('.json'):
            process_file(os.path.join(root, file))
            
# Remove obsolete env files
to_remove = [
    "games/basics of ITP/level16_env.md",
    "games/basics of ITP/level19_env.md",
    "games/basics of ITP/level20_env.md",
    "games/natural number game/level6_start_env.txt"
]

for f in to_remove:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed {f}")

