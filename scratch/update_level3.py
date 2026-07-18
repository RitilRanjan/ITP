import json

with open("games/Set Theory/level3.json", "r") as f:
    data = json.load(f)

if "start_env" in data:
    del data["start_env"]

data["start_env_commands"] = [
    "cv A B C",
    "cf subset \"?t1 ⊆ ?t2\" ∀?v3 (?v3 ∈ ?t1 ⇒ ?v3 ∈ ?t2)",
    "cf goal (A⊆B ∧ B⊆C) ⇒ A⊆C"
]

with open("games/Set Theory/level3.json", "w") as f:
    json.dump(data, f, indent=2)
