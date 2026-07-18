import re

with open("SubstitutionManager.py", "r") as f:
    content = f.read()

# Fix substitute_free
content = re.sub(
    r"    free_occs = \[o for o in occs if o\[\"node\"\].name == var_name and o\[\"is_free\"\] and isinstance\(o\[\"node\"\], Variable\)\]",
    r'''    from AST import Constant
    free_occs = [o for o in occs if o["node"].name == var_name and o["is_free"] and isinstance(o["node"], (Variable, Constant))]''',
    content
)

with open("SubstitutionManager.py", "w") as f:
    f.write(content)

