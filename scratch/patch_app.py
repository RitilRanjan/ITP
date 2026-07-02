import sys

with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "def mock_get_user_input(prompt:" in line:
        new_lines.append(line)
        new_lines.append("    if command_queue:\n")
        new_lines.append("        ans = command_queue.pop(0)\n")
        new_lines.append("        if inputs_collected is not None:\n")
        new_lines.append("            inputs_collected.append(ans)\n")
        new_lines.append("        return ans\n")
        # skip the next 2 lines: raise ...
        continue
    if "raise NotImplementedError(\"Interactive prompts" in line:
        new_lines.append(line)
        continue
    new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
