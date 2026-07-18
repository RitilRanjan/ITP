import os

def patch_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    target = """        else:
            raise ValueError(f"Unknown AST node type: {type(node)}")"""
            
    repl = """        elif isinstance(node, Constant):
            c = Constant(name=node.name)
        elif isinstance(node, PropositionalVariable):
            c = PropositionalVariable(name=node.name)
        else:
            raise ValueError(f"Unknown AST node type: {type(node)}")"""

    content = content.replace(target, repl)

    target2 = """    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")"""

    repl2 = """    elif isinstance(node, Constant):
        c = Constant(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")"""

    content = content.replace(target2, repl2)
    
    with open(filepath, "w") as f:
        f.write(content)

patch_file("SubstitutionManager.py")
patch_file("CommandHandlers/transformation_handlers.py")
print("Patched AST cloning in SubstitutionManager.py and transformation_handlers.py")
