import sys
sys.path.append('.')
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from main import get_default_env
from backend.Parser import reconstruct_string

env = get_default_env(theory="NT")

commands = [
    "cv u v",
    "def_r 2 u ≠ v ¬ u = v",
    "ct 1 S 0",
    "ct 2 S 1",
    "cf goal 1 + 1 = 2",
    "mission goal",
    "rw 2 (1)",
    "rw 1 (2)",
    "cf f1 1 + S 0 = S( 1 + 0 )",
    "apply f1 add_induction",
    "simp_l_eq f1 (1)",
    "cf f2 1 + 0 = 1",
    "apply f2 add_base",
    "simp_l_eq f2 (1)",
    "cf f3 S 1 = S 1",
    "apply f3 E1"
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
    
    if active_env.goal_formula_name:
        goal_form = active_env.formulae[active_env.goal_formula_name]
        print(f"Goal: {reconstruct_string(goal_form)}")

print("\nFinal Goal status:", active_env.goal_formula_name)
