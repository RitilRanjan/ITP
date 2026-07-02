import sys

with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if "parts = command.strip().split(maxsplit=1)" in line:
        indent = line[:line.find("parts")]
        new_lines.append(indent + "command_lines = command.strip().splitlines()\n")
        new_lines.append(indent + "first_line = command_lines[0]\n")
        new_lines.append(indent + "command_queue = command_lines[1:] if len(command_lines) > 1 else []\n")
        new_lines.append(indent + "parts = first_line.strip().split(maxsplit=1)\n")
        i += 1
        continue
    if "new_env = registry.dispatch(cmd, current_env, args_str, get_default_env=get_default_env)" in line:
        new_line = line.replace("get_default_env=get_default_env)", "get_default_env=get_default_env, command_queue=command_queue)")
        new_lines.append(new_line)
        i += 1
        continue
    new_lines.append(line)
    i += 1

with open("app.py", "w") as f:
    f.writelines(new_lines)
