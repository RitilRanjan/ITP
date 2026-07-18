import os

handlers = """
def _handle_swap_base(env: Environment, args_str: str, target_symbol: str, is_relation: bool, cmd_name: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    
    occs, idx = parse_occurrences(cmd_args, 0)
    if occs is not None:
        if 0 in occs: occs = None
        remaining = cmd_args[idx:]
    else:
        remaining = cmd_args
        
    target_name = None
    out_name = None
    equiv_name = None
    
    is_formula_target = False
    is_term_target = False
    
    if len(remaining) == 0:
        if env.goal_formula_name is not None:
            target_name = env.goal_formula_name
            out_name = env.goal_formula_name
            is_formula_target = True
        else:
            print("Error: No target specified and no active goal to default to.")
            return
    else:
        target_name = remaining[0]
        if target_name in env.local_formulae or target_name in env.formulae:
            is_formula_target = True
        elif target_name in env.local_terms or target_name in env.terms:
            is_term_target = True
        else:
            print(f"Error: Target '{target_name}' not found.")
            return
            
        if len(remaining) == 1:
            out_name = target_name
        elif len(remaining) == 2:
            out_name = remaining[1]
        elif len(remaining) >= 3:
            out_name = remaining[1]
            equiv_name = remaining[2]

    if out_name != target_name:
        ns = "formula" if is_formula_target else "term"
        if not validate_new_name(env, out_name, ns):
            return
            
    if equiv_name is not None:
        if not validate_new_name(env, equiv_name, "formula"):
            return

    target_node = env.formulae[target_name] if is_formula_target else env.terms[target_name]
    
    try:
        new_target = swap_ast_nodes(target_node, target_symbol, is_relation, occurrence_idx=occs)
    except Exception as e:
        print(f"Error swapping: {e}")
        return

    if is_formula_target:
        env.formulae[out_name] = new_target
        if out_name not in env.local_formulae:
            env.local_formulae[out_name] = new_target
        print(f"Formula '{out_name}' = '{reconstruct_string(new_target)}'")
        
        if target_name in env.theorems:
            env.theorems.add(out_name)
            print(f"Proven '{out_name}' since '{target_name}' is a theorem!")
            proof_logger.log_rule([(target_name, env.formulae[target_name])], out_name, new_target, cmd_name)
        elif out_name == env.goal_formula_name:
            print(f"Goal updated to '{out_name}': {reconstruct_string(new_target)}")
            env.target_goal = new_target
            
        if equiv_name:
            eq = Connective(name="⇔", arity=2, arguments=[clone_ast(target_node), clone_ast(new_target)])
            env.formulae[equiv_name] = eq
            if equiv_name not in env.local_formulae:
                env.local_formulae[equiv_name] = eq
            print(f"Created equivalence formula '{equiv_name}' = '{reconstruct_string(eq)}'")
            if target_name in env.theorems:
                env.theorems.add(equiv_name)
                print(f"Proven '{equiv_name}' because '{target_name}' is a theorem!")
                proof_logger.log_rule([(target_name, env.formulae[target_name])], equiv_name, eq, f"{cmd_name}_equiv")
                
    elif is_term_target:
        env.terms[out_name] = new_target
        if out_name not in env.local_terms:
            env.local_terms[out_name] = new_target
        print(f"Term '{out_name}' = '{reconstruct_string(new_target)}'")
        
        if equiv_name:
            eq = Relation(name="=", arity=2, rel_type=RelationType.EQUALITY, arguments=[clone_ast(target_node), clone_ast(new_target)])
            env.formulae[equiv_name] = eq
            if equiv_name not in env.local_formulae:
                env.local_formulae[equiv_name] = eq
            print(f"Created equivalence formula '{equiv_name}' = '{reconstruct_string(eq)}'")
            if target_name in env.theorems:
                env.theorems.add(equiv_name)
                print(f"Proven '{equiv_name}' because '{target_name}' is a theorem!")
                proof_logger.log_rule([(target_name, env.terms[target_name])], equiv_name, eq, f"{cmd_name}_equiv")

@registry.register("swap_eq", category="Transformations", help_text="Swap LHS and RHS of '=' in target term/formula")
def handle_swap_eq(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    _handle_swap_base(env, args_str, "=", True, "swap_eq")

@registry.register("swap_bi", category="Transformations", help_text="Swap LHS and RHS of '⇔' in target formula")
def handle_swap_bi(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    _handle_swap_base(env, args_str, "⇔", False, "swap_bi")

"""

with open("CommandHandlers/transformation_handlers.py", "a") as f:
    f.write(handlers)

print("Appended handle_swap_eq and handle_swap_bi")
