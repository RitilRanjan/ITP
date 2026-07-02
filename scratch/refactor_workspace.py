import re

with open("app.py", "r") as f:
    lines = f.readlines()

out = []
workspace_lines = []
in_workspace = False

for line in lines:
    if line.strip() == "# PROVER INTERFACE":
        in_workspace = True
        
    if in_workspace and line.startswith("with tab_games:"):
        in_workspace = False
        out.append("        render_workspace(is_game_mode=False)\n\n")
        
    if in_workspace:
        # dedent by 8 spaces because it was under `with tab_programs:` -> `else:`
        if line.startswith("        "):
            workspace_lines.append(line[8:])
        elif line.strip() == "":
            workspace_lines.append("\n")
        else:
            workspace_lines.append(line)
    else:
        out.append(line)

# insert the function definition before `# --- MAIN UI ---`
insert_idx = 0
for i, line in enumerate(out):
    if line.startswith("# --- MAIN UI ---"):
        insert_idx = i
        break

func_def = ["def render_workspace(is_game_mode=False):\n"] + [("    " + l if l.strip() else l) for l in workspace_lines]

final_out = out[:insert_idx] + func_def + ["\n"] + out[insert_idx:]

with open("app.py", "w") as f:
    f.writelines(final_out)

print("Refactoring done.")
