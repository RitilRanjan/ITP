with open("Environment.py", "r") as f:
    env_code = f.read()

target = "self.theory: str = theory"
repl = "self.theory: str = theory if parent is None else parent.theory"

env_code = env_code.replace(target, repl)

with open("Environment.py", "w") as f:
    f.write(env_code)

print("Patched Environment.py")
