import sys
sys.path.append('.')
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
import main # To register everything

env = Environment()
registry.dispatch("load_theory", env, args_str="NT")

commands = [
    "cv u v",
    "def_r 2 u ≠ v ¬ u = v",
    "ct 1 S 0",
    "cf goal 0 ≠ 1",
    "mission goal",
    "fold ≠ (1)",
    "rw 1 (1)",
    "cv x",
    "cf f1 ¬∃x S x = 0",
    "apply f1 0_pred",
    "fold ∃ (1) f1 f1_unfolded",
    "neg- f1_unfolded f2",
    "intro f2 0",
    "swap_eq (1) f2"
]

active_env = env

# Simulate main loop logic for commands
for line in commands:
    print(f"\n> {line}")
    parts = line.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    
    returned_env = registry.dispatch(cmd, active_env, args_str=args)
    if returned_env is not None and isinstance(returned_env, Environment):
        active_env = returned_env
        print("Switched environment!")

print("\nGoal status:", active_env.goal_formula_name)
