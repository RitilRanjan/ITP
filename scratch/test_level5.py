import sys
sys.path.append('.')
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from main import get_default_env
from backend.RecycleBinManager import RecycleBinManager, snapshot_env_state
from backend.AST import is_structurally_equal
from backend.SubstitutionManager import clone_ast

env = get_default_env(theory="NT")
rb = RecycleBinManager(swap_dir="swap_files_cli")

commands = [
    "cv x",
    "cf f1 0 + 0 = 0",
    "apply f1 add_base",
    "cf goal ∀x ( 0 + x = x ⇒ 0 + S x = S x )",
    "mission goal",
    "intro n n_goal",
    "imply n_hyp",
    "cf f2 0 + S n = S ( 0 + n )",
    "apply f2 add_induction",
    "simp_l_eq n_hyp (1) f2 f3",
    "and f1 goal f6",
    "cf f5 ( 0 + 0 = 0 ∧ ∀x ( 0 + x = x ⇒ 0 + S x = S x ) ) ⇒ ∀x 0 + x = x",
    "apply f5 induction",
    "cf f7 ∀x 0 + x = x",
    "apply f7 PC1 f1 goal f5"
]

command_queue = commands.copy()
has_error = False

while command_queue:
    line = command_queue.pop(0)
    print(f"\n> {line}")
    parts = line.split(maxsplit=1)
    cmd = parts[0]
    args_str = parts[1] if len(parts) > 1 else ""
    
    kwargs = {
        "command_queue": command_queue,
        "inputs_collected": []
    }
    
    new_env = registry.dispatch(cmd, env, args_str, **kwargs)
    if new_env is not None:
        env = new_env
        
    # Auto-resolve
    if env.goal_formula_name is not None and env.goal_formula_name not in env.theorems:
        goal_node = env.formulae[env.goal_formula_name]
        for th_name, th_node in env.theorems.items():
            if is_structurally_equal(goal_node, th_node):
                env.add_theorem(env.goal_formula_name)
                print(f"Goal '{env.goal_formula_name}' matches theorem '{th_name}'.")
                break
                
    while env.goal_formula_name is not None and env.goal_formula_name in env.theorems:
        goal_name = env.goal_formula_name
        original_goal_name = getattr(env, "original_goal_formula_name", goal_name)
        print(f"Goal '{goal_name}' is proven!")
        
        goal_node = env.theorems[goal_name]
        parent = env.parent
        
        parent.theorems[goal_name] = clone_ast(goal_node)
        if original_goal_name != goal_name and original_goal_name in parent.formulae:
            parent.theorems[original_goal_name] = clone_ast(parent.formulae[original_goal_name])
            print(f"Original goal '{original_goal_name}' proven.")
            
        env = parent

