import ast
import glob
import os
from collections import defaultdict

def get_local_imports():
    py_files = glob.glob('*.py')
    modules = [os.path.splitext(f)[0] for f in py_files]
    
    deps = defaultdict(list)
    
    for f in py_files:
        mod_name = os.path.splitext(f)[0]
        try:
            with open(f, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        base = n.name.split('.')[0]
                        if base in modules and base != mod_name:
                            deps[mod_name].append(base)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        base = node.module.split('.')[0]
                        if base in modules and base != mod_name:
                            deps[mod_name].append(base)
                            
        except Exception as e:
            pass
            
    # Remove duplicates
    for k in deps:
        deps[k] = list(set(deps[k]))
        
    return deps

deps = get_local_imports()
for module, imports in sorted(deps.items()):
    print(f"{module} -> {', '.join(sorted(imports))}")
