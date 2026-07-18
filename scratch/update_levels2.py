import os
import json

games_dir = "/Users/ritilranjan/ITP/games"

for root, _, files in os.walk(games_dir):
    for file in files:
        if file.endswith(".json"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            changed = False
            if "allowed_commands" in data:
                cmds = data["allowed_commands"]
                if "ct" in cmds or "cf" in cmds:
                    if "rw" not in cmds:
                        cmds.append("rw")
                        changed = True
            
            # also, we must make sure fold isn't completely removed if they need it for other things, but rw is definitely needed.
            # actually wait, let's also remove def_f and def_r from allowed commands if they are STILL there.
            if "allowed_commands" in data:
                new_cmds = [cmd for cmd in data["allowed_commands"] if cmd not in ("def_f", "def_r")]
                if len(new_cmds) != len(data["allowed_commands"]):
                    data["allowed_commands"] = new_cmds
                    changed = True

            if changed:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write('\n')
                print(f"Added rw / fixed allowed commands in {filepath}")
