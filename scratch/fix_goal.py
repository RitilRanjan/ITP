import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # In transformation_handlers.py:
    # fold all: env.formulae[f2_name] = f_clone
    content = re.sub(
        r'(env\.formulae\[([a-zA-Z0-9_]+)\] = f_clone\n)',
        r'\1        if f1_name == env.goal_formula_name:\n            env.goal_formula_name = \2\n',
        content
    )
    
    # fold: env.formulae[output_name] = expanded
    content = re.sub(
        r'(env\.formulae\[([a-zA-Z0-9_]+)\] = expanded\n)',
        r'\1    if input_name == env.goal_formula_name:\n        env.goal_formula_name = \2\n',
        content
    )
    
    # simp: env.formulae[output_name] = new_node
    content = re.sub(
        r'(env\.formulae\[([a-zA-Z0-9_]+)\] = new_node\n)',
        r'\1        if input_name == env.goal_formula_name:\n            env.goal_formula_name = \2\n',
        content
    )
    
    # rw: env.formulae[save_name] = new_node
    content = re.sub(
        r'(env\.formulae\[([a-zA-Z0-9_]+)\] = new_node\n)',
        r'\1        if target_name == env.goal_formula_name:\n            env.goal_formula_name = \2\n',
        content
    )
    
    # intro2: env.formulae[out_name] = new_target
    content = re.sub(
        r'(env\.formulae\[([a-zA-Z0-9_]+)\] = new_target\n)',
        r'\1        if target_name == env.goal_formula_name:\n            env.goal_formula_name = \2\n',
        content
    )
    
    # def expansion: env.formulae[out_name] = f_clone
    content = re.sub(
        r'(env\.formulae\[out_name\] = f_clone\n)',
        r'\1        if target_name == env.goal_formula_name:\n            env.goal_formula_name = out_name\n',
        content
    )

    with open(filepath, 'w') as f:
        f.write(content)

fix_file("/Users/ritilranjan/ITP/CommandHandlers/transformation_handlers.py")
fix_file("/Users/ritilranjan/ITP/CommandHandlers/env_handlers.py")
