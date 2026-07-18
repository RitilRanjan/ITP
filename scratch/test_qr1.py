import sys
sys.path.append('.')
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from main import get_default_env

env = get_default_env(theory="NT")

commands = [
    "cv x",
    "cf f1 x + 0 = x",
    "apply f1 add_base",
    "cf f2 ∀x x + 0 = x",
    "apply f2 QR1 f1",
    "intro f2 1"
]

active_env = env

for line in commands:
    print(f"\n> {line}")
    parts = line.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    try:
        returned_env = registry.dispatch(cmd, active_env, args_str=args)
        if returned_env:
            active_env = returned_env
    except Exception as e:
        print(f"EXCEPTION: {e}")

