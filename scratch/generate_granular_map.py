import os
import ast
from collections import defaultdict

def extract_granular_deps(directory):
    # Map: module -> { 'classes': set(), 'functions': set() }
    modules = {}
    
    # Map: (src_module, src_entity) -> set((tgt_module, tgt_entity))
    deps = defaultdict(set)
    
    # First pass: discover all defined classes and functions
    for filename in os.listdir(directory):
        if not filename.endswith('.py') or filename.startswith('.'):
            continue
            
        module_name = filename[:-3]
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except Exception:
            continue
            
        modules[module_name] = {'classes': set(), 'functions': set()}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                modules[module_name]['classes'].add(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('__'):
                modules[module_name]['functions'].add(node.name)
                
    # Quick lookup: entity_name -> module_name
    entity_lookup = {}
    for mod, data in modules.items():
        for c in data['classes']:
            entity_lookup[c] = mod
        for f in data['functions']:
            entity_lookup[f] = mod
            
    # Second pass: find dependencies
    for filename in os.listdir(directory):
        if not filename.endswith('.py') or filename.startswith('.'):
            continue
            
        src_module = filename[:-3]
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except Exception:
            continue
            
        # We only track class-to-class inheritance and function-to-function calls
        current_context = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                current_context = node.name
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in entity_lookup:
                        tgt_module = entity_lookup[base.id]
                        if tgt_module != src_module or base.id != current_context:
                            deps[(src_module, current_context)].add((tgt_module, base.id))
                            
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('__'):
                current_context = node.name
                # Find calls inside this function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            callee = child.func.id
                            if callee in entity_lookup:
                                tgt_module = entity_lookup[callee]
                                if tgt_module != src_module or callee != current_context:
                                    deps[(src_module, current_context)].add((tgt_module, callee))
                                    
    # Generate Mermaid
    output = []
    output.append("# Granular Dependency Map")
    output.append("This graph shows dependencies between individual classes and functions across the codebase.\\n")
    output.append("```mermaid")
    output.append("graph TD")
    
    # Subgraphs
    for mod, data in modules.items():
        if not data['classes'] and not data['functions']:
            continue
        output.append(f"  subgraph {mod}")
        for c in data['classes']:
            output.append(f"    {mod}_{c}[{c}]:::classNode")
        for f in data['functions']:
            output.append(f"    {mod}_{f}({f}):::funcNode")
        output.append("  end")
        
    # Edges
    for (s_mod, s_ent), targets in deps.items():
        for (t_mod, t_ent) in targets:
            output.append(f"  {s_mod}_{s_ent} --> {t_mod}_{t_ent}")
            
    # Styling
    output.append("  classDef classNode fill:#f9f,stroke:#333,stroke-width:2px;")
    output.append("  classDef funcNode fill:#bbf,stroke:#333,stroke-width:1px;")
    
    output.append("```")
    
    with open('/Users/ritilranjan/ITP/scratch/map.md', 'w') as f:
        f.write("\n".join(output))
        
if __name__ == "__main__":
    extract_granular_deps('/Users/ritilranjan/ITP')
