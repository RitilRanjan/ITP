import sys
sys.path.append('.')
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from backend.SubstitutionManager import collect_all_occurrences
import main # To register everything

env = Environment()
registry.dispatch("load_theory", env, args_str="NT")

commands = [
    "cv u v",
    "def_r 2 u ≠ v ¬ u = v",
    "ct 1 S 0",
    "cf goal 0 ≠ 1",
    "mission goal",
    "fold ≠ (1)"
]

active_env = env
for line in commands:
    parts = line.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    returned_env = registry.dispatch(cmd, active_env, args_str=args)
    if returned_env:
        active_env = returned_env

goal = active_env.formulae["goal"]
print("Goal AST:")
occs = collect_all_occurrences(goal)
for o in occs:
    print(f"Node: {type(o['node']).__name__}, Name: {o['node'].name}, IsFree: {o['is_free']}")
