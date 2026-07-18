import re

with open('backend/SubstitutionManager.py', 'r') as f:
    content = f.read()

# Remove imports
content = re.sub(r'Function, FunctionType,\s*', '', content)
content = re.sub(r'Relation, RelationType,\s*', '', content)
content = re.sub(r'Function,\s*', '', content)
content = re.sub(r'Relation,\s*', '', content)

# Remove `Function` and `Relation` from isinstance checks like `(Function, Relation, Connective)`
content = re.sub(r'\(Function, Relation, Connective\)', '(Connective,)', content)
content = re.sub(r'\(Constant, Function, Relation\)', '(Constant,)', content)
content = re.sub(r'\(Function, Relation\)', '()', content)
content = re.sub(r'isinstance\(node, \(\)\)', 'False', content)

# Remove entire `elif isinstance(node, Function): ...` blocks
# It's tricky to do with regex, let's write a small state machine or just do manual replace.
