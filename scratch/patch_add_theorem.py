with open("CommandHandlers/transformation_handlers.py", "r") as f:
    code = f.read()

code = code.replace("env.theorems.add(out_name)", "env.add_theorem(out_name)")
code = code.replace("env.theorems.add(equiv_name)", "env.add_theorem(equiv_name)")

with open("CommandHandlers/transformation_handlers.py", "w") as f:
    f.write(code)

print("Patched add_theorem")
