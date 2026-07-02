import json

with open("games/basics of ITP/level17.json", "r") as f:
    data = json.load(f)

# The last hint is at index 5. We should add explanation of ⇔ there or create a new hint.
# Wait, the user said "explain ⇔ logical connective and how to type it in the previous level's last hint."
last_hint = data["guide_hints"][-1]
last_hint += "\n\nNote: The `⇔` symbol is the logical connective for 'if and only if' (equivalence). You can type it by entering `21d4` and pressing Option+X (on Mac) or equivalent hex-code shortcuts on other systems, or simply copy-pasting it. The `<equiv>` parameter in the `fold` command automatically generates a theorem using this `⇔` connective!"
data["guide_hints"][-1] = last_hint

with open("games/basics of ITP/level17.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
