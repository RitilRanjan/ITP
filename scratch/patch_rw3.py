import re

with open("CommandHandlers/transformation_handlers.py", "r") as f:
    content = f.read()

content = content.replace("if f1_name == env.goal_formula_name:", "if target_name == env.goal_formula_name:")

with open("CommandHandlers/transformation_handlers.py", "w") as f:
    f.write(content)

