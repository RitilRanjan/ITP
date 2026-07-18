import re

with open("main.py", "r") as f:
    code = f.read()

target = """        # Check if the goal in the current child environment is proven
        if env.goal_formula_name is not None and env.goal_formula_name not in env.theorems:
            goal_node = env.formulae[env.goal_formula_name]
            from backend.AST import check_structural_equality
            for th_name, th_node in env.theorems.items():
                if check_structural_equality(goal_node, th_node):"""

repl = """        # Check if the goal in the current child environment is proven
        if env.goal_formula_name is not None and env.goal_formula_name not in env.theorems:
            goal_node = env.formulae[env.goal_formula_name]
            from backend.AST import is_structurally_equal
            for th_name, th_node in env.theorems.items():
                if is_structurally_equal(goal_node, th_node):"""

code = code.replace(target, repl)

with open("main.py", "w") as f:
    f.write(code)

print("Patched main.py again")
