import re

with open("SubstitutionManager.py", "r") as f:
    content = f.read()

# In collect_all_occurrences, add Constant and PropositionalVariable
content = re.sub(
    r"    if isinstance\(node, \(Variable, DummyVariable\)\):\n        is_free = True",
    r'''    if isinstance(node, (Variable, DummyVariable, Constant, PropositionalVariable, MetaVariable)):
        is_free = True''',
    content
)

# In collect_term_vars_list, add Constant
content = re.sub(
    r"    if isinstance\(node, \(Variable, DummyVariable\)\):",
    r'''    if isinstance(node, (Variable, DummyVariable, Constant)):''',
    content
)

with open("SubstitutionManager.py", "w") as f:
    f.write(content)

