import re

with open("CommandHandlers/utils.py", "r") as f:
    code = f.read()

target = """    if target_name == out_name:
        if target_name not in local_dict:
            print(f"Error: Cannot modify '{target_name}' in-place because it is not defined in the current local environment. Provide an explicit <out> name.")
            return None"""

repl = """    if target_name == out_name:
        if target_name not in local_dict:
            if target_name == env.goal_formula_name and namespace == "formula":
                # Allow in-place modification of the goal formula, we will just copy it to local_dict
                pass
            else:
                print(f"Error: Cannot modify '{target_name}' in-place because it is not defined in the current local environment. Provide an explicit <out> name.")
                return None"""

code = code.replace(target, repl)

with open("CommandHandlers/utils.py", "w") as f:
    f.write(code)

print("Patched utils.py")
