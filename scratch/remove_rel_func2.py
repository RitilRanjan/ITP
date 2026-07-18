import re

with open('backend/SubstitutionManager.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if re.match(r'^\s*elif isinstance\(node, Function\):', line) or re.match(r'^\s*elif isinstance\(node, Relation\):', line):
        skip = True
        continue
    
    if skip:
        if re.match(r'^\s*elif ', line) or re.match(r'^\s*return ', line) or re.match(r'^\s*if ', line) or re.match(r'^\S', line):
            skip = False
        else:
            continue
            
    # Also fix inline usages
    line = line.replace('Function, FunctionType,', '')
    line = line.replace('Relation, RelationType,', '')
    line = line.replace('Function, Relation, ', '')
    line = line.replace('Function, Relation', '')
    line = line.replace('(Function, Relation, Connective)', '(Connective,)').replace('(Connective,)', 'Connective')
    line = line.replace('(Constant, Function, Relation)', 'Constant')
    
    new_lines.append(line)

with open('backend/SubstitutionManager.py', 'w') as f:
    f.writelines(new_lines)

