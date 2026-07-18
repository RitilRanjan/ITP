import re

# 1. Add handle_iff to CommandHandlers/logic_handlers.py
with open("CommandHandlers/logic_handlers.py", "r") as f:
    content = f.read()

iff_code = """
@registry.register("iff", category="Mission Tactics", help_text="Split Ψ⇔Φ into two implications")
def handle_iff(env: Environment, args_str: str) -> Environment:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) == 0:
        print("Error: Usage: iff [<target>] [<out_left>] <out_right>")
        return env

    arg0 = cmd_args[0]
    
    is_valid_target = False
    if arg0 in env.formulae:
        t_node = env.formulae[arg0]
        is_local = arg0 in env.local_formulae
        is_correct = isinstance(t_node, Connective) and t_node.name == "⇔" and t_node.arity == 2
        if is_local and is_correct:
            is_valid_target = True
            
    if is_valid_target:
        # target is arg0
        target_name = arg0
        if len(cmd_args) == 1:
            print("Error: Usage: iff <target> [<out_left>] <out_right>")
            return env
        elif len(cmd_args) == 2:
            out_left_name = target_name
            out_right_name = cmd_args[1]
        else:
            out_left_name = cmd_args[1]
            out_right_name = cmd_args[2]
        is_goal_target = False
    else:
        # target is goal
        if env.goal_formula_name is None:
            print("Error: 'iff' without a target can only be used inside a mission environment (active goal required).")
            return env
        target_name = env.goal_formula_name
        if len(cmd_args) == 1:
            out_left_name = target_name
            out_right_name = arg0
        else:
            out_left_name = arg0
            out_right_name = cmd_args[1]
        is_goal_target = True

    if target_name not in env.formulae:
        print(f"Error: Target formula '{target_name}' not found.")
        return env

    target_node = env.formulae[target_name]

    if not (isinstance(target_node, Connective) and target_node.name == "⇔" and target_node.arity == 2):
        print(f"Error: The target '{target_name}' is not of the form Ψ ⇔ Φ.")
        return env

    psi_node = Connective(name="⇒", arity=2, arguments=[clone_ast(target_node.arguments[0]), clone_ast(target_node.arguments[1])])
    phi_node = Connective(name="⇒", arity=2, arguments=[clone_ast(target_node.arguments[1]), clone_ast(target_node.arguments[0])])

    # Name validation
    if out_left_name in env.formulae and out_left_name != target_name:
        if not env.formulae[out_left_name].is_structurally_equal(psi_node):
            print(f"Error: Name '{out_left_name}' already exists in the environment with a different definition.")
            return env
    else:
        if not enforce_no_shadowing(env, target_name, out_left_name, "formula"):
            return env

    if out_right_name in env.formulae and out_right_name != target_name:
        if not env.formulae[out_right_name].is_structurally_equal(phi_node):
            print(f"Error: Name '{out_right_name}' already exists in the environment with a different definition.")
            return env
    else:
        if not enforce_no_shadowing(env, target_name, out_right_name, "formula"):
            return env

    if out_left_name == out_right_name:
        print(f"Error: <out_left> and <out_right> cannot have the same name ('{out_left_name}').")
        return env

    if is_goal_target:
        # Goal Splitting
        env.formulae[out_left_name] = clone_ast(psi_node)
        env.formulae[out_right_name] = clone_ast(phi_node)

        env.goal_formula_name = out_left_name
        env.iff_right_formula_name = out_right_name
        env.proof_annotation = {
            "method": "⇔-intro",
            "left_name": out_left_name,
            "left_node": clone_ast(psi_node),
            "right_name": out_right_name,
            "right_node": clone_ast(phi_node),
            "equivalence_name": target_name,
            "equivalence_node": clone_ast(target_node),
        }
        print(f"Equivalence goal '{target_name}' split into:")
        if out_left_name == target_name:
            print(f"  Ψ⇒Φ (in-place): {reconstruct_string(psi_node)}")
        else:
            print(f"  Ψ⇒Φ ('{out_left_name}'): {reconstruct_string(psi_node)}")
        print(f"  Φ⇒Ψ ('{out_right_name}'): {reconstruct_string(phi_node)}")
        print(f"Now working on Φ⇒Ψ ('{out_right_name}') in a nested environment first.")

        grandchild = Environment(parent=env, goal_formula_name=out_right_name)
        print(f"Entered nested environment for goal '{out_right_name}'.")
        return grandchild
    else:
        # Premise Splitting
        is_proven = target_name in env.theorems

        if is_proven:
            env.add_theorem(out_left_name)
            env.add_theorem(out_right_name)

        env.formulae[out_left_name] = clone_ast(psi_node)
        env.formulae[out_right_name] = clone_ast(phi_node)

        if is_proven:
            env.add_theorem(out_left_name)
            env.add_theorem(out_right_name)
            
            if out_left_name == target_name:
                print(f"'{out_left_name}' redefined to: {reconstruct_string(psi_node)}  [proven]")
            else:
                print(f"'{out_left_name}' created as:   {reconstruct_string(psi_node)}  [proven]")
            print(f"'{out_right_name}' created as:   {reconstruct_string(phi_node)}  [proven]")

            proof_logger.log_rule(
                [(target_name, clone_ast(target_node))],
                out_left_name, psi_node, "PC1", "⇔-elim-left"
            )
            proof_logger.log_rule(
                [(target_name, clone_ast(target_node))],
                out_right_name, phi_node, "PC1", "⇔-elim-right"
            )
        else:
            if out_left_name == target_name:
                print(f"'{out_left_name}' redefined to: {reconstruct_string(psi_node)}")
            else:
                print(f"'{out_left_name}' created as:   {reconstruct_string(psi_node)}")
            print(f"'{out_right_name}' created as:   {reconstruct_string(phi_node)}")
            
        return env
"""

if "@registry.register(\"iff\"," not in content:
    content += "\n" + iff_code + "\n"
    with open("CommandHandlers/logic_handlers.py", "w") as f:
        f.write(content)
    print("Added handle_iff to logic_handlers.py")

# 2. Update Environment.py to include iff_right_formula_name
with open("Environment.py", "r") as f:
    env_content = f.read()

if "self.iff_right_formula_name: Optional[str] = None" not in env_content:
    env_content = env_content.replace(
        "self.and_right_formula_name: Optional[str] = None",
        "self.and_right_formula_name: Optional[str] = None\n        self.iff_right_formula_name: Optional[str] = None"
    )
    with open("Environment.py", "w") as f:
        f.write(env_content)
    print("Updated Environment.py")

# 3. Update main.py to handle iff_right_formula_name closing
with open("main.py", "r") as f:
    main_content = f.read()

if "iff_right_formula_name" not in main_content:
    # Modify the guard
    guard_target = """            and_right = getattr(env, "and_right_formula_name", None)
            if and_right is not None and and_right not in env.theorems:
                break  # Φ not yet proven; cannot close the conjunction"""
    
    guard_replacement = """            and_right = getattr(env, "and_right_formula_name", None)
            iff_right = getattr(env, "iff_right_formula_name", None)
            if and_right is not None and and_right not in env.theorems:
                break  # Φ not yet proven; cannot close the conjunction
            if iff_right is not None and iff_right not in env.theorems:
                break  # Φ⇒Ψ not yet proven; cannot close the equivalence"""
    
    main_content = main_content.replace(guard_target, guard_replacement)

    # Modify the closure block
    closure_target = """            elif and_right is not None:
                # 'and' environment: both Ψ and Φ proven → register the original conjunction in parent"""
    
    closure_replacement = """            elif iff_right is not None:
                print(f"Both parts proven (Ψ⇒Φ='{goal_name}', Φ⇒Ψ='{iff_right}'). "
                      f"Equivalence goal '{original_goal_name}' is proven!")
                if original_goal_name in parent.formulae:
                    parent.theorems[original_goal_name] = clone_ast(parent.formulae[original_goal_name])
                else:
                    parent.theorems[original_goal_name] = clone_ast(env.formulae[original_goal_name])
                iff_node = parent.theorems[original_goal_name]
                if pa and pa.get("method") == "⇔-intro":
                    proof_logger.log(
                        [
                            (pa["left_name"], env.theorems.get(pa["left_name"], pa["left_node"])),
                            (pa["right_name"], env.theorems.get(pa["right_name"], pa["right_node"])),
                        ],
                        original_goal_name, iff_node,
                        "rule: PC1 (⇔-intro)"
                    )
                else:
                    proof_logger.log_summary(original_goal_name, iff_node, "⇔-intro")
            elif and_right is not None:
                # 'and' environment: both Ψ and Φ proven → register the original conjunction in parent"""
    
    main_content = main_content.replace(closure_target, closure_replacement)
    with open("main.py", "w") as f:
        f.write(main_content)
    print("Updated main.py")

