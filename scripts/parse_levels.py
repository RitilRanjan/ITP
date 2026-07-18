import json, glob
import re

for path in sorted(glob.glob("games/basics of ITP/level*.json"), key=lambda x: int(re.search(r'level(\d+)', x).group(1))):
    with open(path) as f:
        data = json.load(f)
        hints = data.get("guide_hints", [])
        print(f"--- {path} ---")
        for hint in hints:
            print(hint)
