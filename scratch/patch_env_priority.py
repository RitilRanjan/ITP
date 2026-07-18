import re
with open('backend/Environment.py', 'r') as f:
    c = f.read()

c = c.replace('def_type: DefinitionType = DefinitionType.USER_DEFINED', 'def_type: DefinitionType = DefinitionType.USER_DEFINED\n    priority: int = 0')

with open('backend/Environment.py', 'w') as f:
    f.write(c)
