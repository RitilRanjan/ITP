from typing import Callable, Any

from backend.AST import Connective, FormulaNode
from backend.Environment import Environment
from backend.Parser import lex, reconstruct_string, parse_fol_formula, parse_prop_formula
from backend.SubstitutionManager import clone_ast
from backend.CommandHandlers.CommandRegistry import registry
from backend.CommandHandlers.utils import validate_new_name

@registry.register("mission", category="Mission Management", help_text="Enter a child environment to prove goal formula f")
def handle_mission(env: Environment, args_str: str) -> Environment:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: mission <formula>")
        return env
    f1_name = cmd_args[0]
    if f1_name not in env.formulae:
        print(f"Error: Formula '{f1_name}' not found.")
        return env
    if f1_name in env.theorems:
        print(f"Error: Goal '{f1_name}' is already proven.")
        return env
    # Also check if any existing theorem has the exact same formula
    goal_node = env.formulae[f1_name]
    already_proven = False
    for k in env.theorems:
        v = env.formulae[k]
        if isinstance(v, FormulaNode) and v.is_structurally_equal(goal_node):
            already_proven = True
            break
    if already_proven:
        print(f"Error: Goal '{f1_name}' (or a structurally identical formula) is already proven.")
        return env
    
    new_env = Environment(parent=env, goal_formula_name=f1_name)
    print(f"Entered child environment for goal '{f1_name}'.")
    return new_env

@registry.register("contra", category="Mission Management", help_text="Proof by contradiction: f2 = ¬goal, goal f3 = ⊥ (Syntax: contra [<f1>] <f2> <f3>)")
def handle_contra(env: Environment, args_str: str) -> Environment:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) == 2:
        if env.goal_formula_name is None:
            print("Error: No active goal to target. Usage: contra [<f1>] <f2> <f3>")
            return env
        f1_name = env.goal_formula_name
        f2_name, f3_name = cmd_args[0], cmd_args[1]
    elif len(cmd_args) >= 3:
        f1_name, f2_name, f3_name = cmd_args[0], cmd_args[1], cmd_args[2]
    else:
        print("Error: Usage: contra [<f1>] <f2> <f3>")
        return env
    
    # 1. Verify f1 exists in active environment's formulae
    if f1_name not in env.formulae:
        print(f"Error: Formula '{f1_name}' not found.")
        return env
        
    # 2. Verify f1 is not already proven
    if f1_name in env.local_theorems or f1_name in env.theorems:
        print(f"Error: Goal '{f1_name}' is already proven.")
        return env
    # Also check if structurally identical theorem exists
    f1_node = env.formulae[f1_name]
    already_proven = False
    for k in env.theorems:
        v = env.formulae[k]
        if v.is_structurally_equal(f1_node):
            already_proven = True
            break
    if already_proven:
        print(f"Error: Goal '{f1_name}' (or a structurally identical formula) is already proven.")
        return env
        
    # 3. Verify name uniqueness for f2 and f3
    if f2_name == f3_name:
        print(f"Error: Name '{f2_name}' is already in use by another environment object.")
        return env
        
    # Validate f2 name
    from backend.CommandHandlers.utils import validate_new_name
    if not validate_new_name(env, f2_name, "formula"):
        return env
        
    # Validate f3 name
    if not validate_new_name(env, f3_name, "formula"):
        return env
        
    # 4. Construct AST nodes
    from backend.Parser import reconstruct_string, parse_fol_formula, parse_prop_formula
    from backend.AST import Connective
    from backend.SubstitutionManager import clone_ast
    f1_str = reconstruct_string(f1_node, color_mode="none")
    try:
        neg_f1_node = parse_fol_formula(f"¬ ( {f1_str} )", env)
    except Exception:
        neg_f1_node = parse_prop_formula(f"¬ ( {f1_str} )", env)
        
    goal_node = Connective("⊥", 0, [])
    
    # 5. Instantiation of child environment
    child_env = Environment(parent=env, goal_formula_name=f3_name, target_proven_formula_name=f1_name)
    child_env.target_goal = goal_node
    child_env.formulae[f2_name] = neg_f1_node
    child_env.add_theorem(f2_name)
    child_env.formulae[f3_name] = goal_node
    # Store closure metadata for proof logger
    child_env.proof_annotation = {
        "method": "contradiction-elim",
        "target_name": f1_name,
        "target_node": clone_ast(f1_node),
        "assumption_name": f2_name,
        "assumption_node": clone_ast(neg_f1_node),
        "contradiction_name": f3_name,
        "contradiction_node": clone_ast(goal_node),
    }
    
    print(f"Entered child environment for contradiction proof. Goal: '{f3_name}' (⊥). Assumption '{f2_name}': ¬{f1_name}.")
    return child_env
