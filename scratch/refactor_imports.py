import os
import re

modules_to_move = [
    "AST", "Autocomplete", "AutoProver", "BackwardSearch", 
    "DeductiveSystem", "DefinitionExpander", "Environment", 
    "GraphSearch", "NT_Rules", "ProofGenerator", "ProofLogger", 
    "PropAbstraction", "RecycleBinManager", "Registry", 
    "SequentEvaluator", "StorageManager", "SubstitutionManager", 
    "TruthEvaluator", "ZFC_Rules", "CommandHandlers"
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content

    # Replace modules exactly
    for mod in modules_to_move:
        # Match 'from MOD import'
        new_content = re.sub(rf'^(\s*)from\s+{mod}\b', rf'\1from backend.{mod}', new_content, flags=re.MULTILINE)
        # Match 'import MOD'
        new_content = re.sub(rf'^(\s*)import\s+{mod}\b', rf'\1import backend.{mod}', new_content, flags=re.MULTILINE)

    # Handle Frontend -> backend.Parser specifically
    new_content = re.sub(r'^(\s*)from\s+Frontend\b', r'\1from backend.Parser', new_content, flags=re.MULTILINE)
    new_content = re.sub(r'^(\s*)import\s+Frontend\b', r'\1import backend.Parser', new_content, flags=re.MULTILINE)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated imports in {filepath}")

for root_dir, dirs, files in os.walk('.'):
    if '.git' in root_dir or '__pycache__' in root_dir:
        continue
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root_dir, file))
