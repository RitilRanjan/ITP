import json

with open("games/natural number game/level6.json", "r") as f:
    data = json.load(f)

if "start_env" in data:
    del data["start_env"]

data["start_env_commands"] = [
    "cv x y",
    "cf add_id_left ∀x (0 + x = x)"
]

with open("games/natural number game/level6.json", "w") as f:
    json.dump(data, f, indent=2)
