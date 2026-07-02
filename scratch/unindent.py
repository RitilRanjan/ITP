with open("StorageManager.py", "r") as f:
    lines = f.readlines()

for i in range(31, 140):
    if lines[i].startswith("        "):
        lines[i] = lines[i][4:]

with open("StorageManager.py", "w") as f:
    f.writelines(lines)
