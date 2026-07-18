import re

with open("SubstitutionManager.py", "r") as f:
    content = f.read()

# For substitute_free
content = re.sub(
    r"    if occurrence_idx is not None:\n        if 1 <= occurrence_idx <= len\(free_occs\):\n            target = free_occs\[occurrence_idx - 1\]\[\"node\"\]\n            replacements_map = \{id\(target\): term\}",
    r'''    if occurrence_idx is not None:
        if isinstance(occurrence_idx, list):
            replacements_map = {id(free_occs[i-1]["node"]): term for i in occurrence_idx if 1 <= i <= len(free_occs)}
        elif 1 <= occurrence_idx <= len(free_occs):
            target = free_occs[occurrence_idx - 1]["node"]
            replacements_map = {id(target): term}''',
    content
)

# For substitute_term
content = re.sub(
    r"    if occurrence_idx is not None:\n        if 1 <= occurrence_idx <= len\(free_occs\):\n            target = free_occs\[occurrence_idx - 1\]\[\"node\"\]\n            replacements_map = \{id\(target\): replacement_term\}",
    r'''    if occurrence_idx is not None:
        if isinstance(occurrence_idx, list):
            replacements_map = {id(free_occs[i-1]["node"]): replacement_term for i in occurrence_idx if 1 <= i <= len(free_occs)}
        elif 1 <= occurrence_idx <= len(free_occs):
            target = free_occs[occurrence_idx - 1]["node"]
            replacements_map = {id(target): replacement_term}''',
    content
)

# For substitute_proposition
content = re.sub(
    r"    if occurrence_idx is not None:\n        if 1 <= occurrence_idx <= len\(prop_occs\):\n            target = prop_occs\[occurrence_idx - 1\]\[\"node\"\]\n            replacements_map = \{id\(target\): formula_replacement\}",
    r'''    if occurrence_idx is not None:
        if isinstance(occurrence_idx, list):
            replacements_map = {id(prop_occs[i-1]["node"]): formula_replacement for i in occurrence_idx if 1 <= i <= len(prop_occs)}
        elif 1 <= occurrence_idx <= len(prop_occs):
            target = prop_occs[occurrence_idx - 1]["node"]
            replacements_map = {id(target): formula_replacement}''',
    content
)

with open("SubstitutionManager.py", "w") as f:
    f.write(content)

