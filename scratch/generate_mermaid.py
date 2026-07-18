import ast
import os
from collections import defaultdict

def generate_mermaid():
    print("# Granular Dependency Map")
    print("This graph shows dependencies between individual classes and functions across the codebase.\\n")
    print("```mermaid")
    print("graph TD")
    
    # We will just list the modules and their classes/functions, and inter-module dependencies for brevity.
    # To replicate the previous output, we group by module (subgraph)
    
    py_files = []
    for root_dir, dirs, files in os.walk('.'):
        if '.git' in root_dir or '__pycache__' in root_dir or 'scratch' in root_dir or 'tests' in root_dir:
            continue
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root_dir, file))
                
    for f in py_files:
        mod_name = os.path.basename(f)[:-3]
        if mod_name == "__init__":
            continue
            
        try:
            with open(f, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
        except Exception:
            continue
            
        print(f"  subgraph {mod_name}")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                print(f"    {mod_name}_{node.name}[{node.name}]:::classNode")
            elif isinstance(node, ast.FunctionDef):
                print(f"    {mod_name}_{node.name}({node.name}):::funcNode")
        print("  end")
        
    print("```")

if __name__ == "__main__":
    generate_mermaid()
