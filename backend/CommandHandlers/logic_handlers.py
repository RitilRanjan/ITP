from typing import Callable, Any

from backend.AST import Variable, Quantifier, Connective, Node
from backend.Environment import Environment
from backend.Parser import lex, reconstruct_string
from backend.SubstitutionManager import clone_ast, substitute_free, check_free, check_bound
from backend.Registry import AXIOMS, RULES, THEORY_AXIOMS, LOGICAL_AXIOMS
from backend.ProofLogger import proof_logger
from backend.CommandHandlers.CommandRegistry import registry
from backend.CommandHandlers.utils import validate_new_name, parse_universal_args, resolve_term, enforce_no_shadowing

@registry.register("left", category="Mission Tactics", help_text="Reduce goal/premise Ψ∨Φ to Ψ", aliases=["right"])
def handle_left_right(env: Environment, args_str: str, cmd: str) -> None:
    if env.goal_formula_name is None:
        print(f"Error: '{cmd}' can only be used inside a child environment (i.e. when there is an active mission goal).")
        return
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) == 0:
        if env.goal_formula_name is None:
            print(f"Error: '{cmd}' requires an active goal formula.")
            return
        new_goal_name = env.goal_formula_name
    elif len(cmd_args) == 1:
        new_goal_name = cmd_args[0]
    else:
        print(f"Error: Usage: {cmd} [<new_goal_name>]")
        return
    
    current_goal_name = env.goal_formula_name
    if current_goal_name not in env.formulae:
        print(f"Error: Current goal formula '{current_goal_name}' not found in environment.")
        return
    current_goal_node = env.formulae[current_goal_name]
    
    if not (isinstance(current_goal_node, Connective) and current_goal_node.name == "∨" and current_goal_node.arity == 2):
        print(f"Error: The current goal '{current_goal_name}' is not of the form Ψ ∨ Φ. "
              f"'left'/'right' can only be used on disjunctive goals.")
        return
    
    selected_node = current_goal_node.arguments[0] if cmd == "left" else current_goal_node.arguments[1]
    
    if new_goal_name in env.formulae and new_goal_name != current_goal_name:
        existing_node = env.formulae[new_goal_name]
        if not existing_node.is_structurally_equal(selected_node):
            print(f"Error: Name '{new_goal_name}' already exists in the environment with a different definition.")
            return
    else:
        if not enforce_no_shadowing(env, current_goal_name, new_goal_name, "formula"):
            return
        env.formulae[new_goal_name] = clone_ast(selected_node)
    
    env.goal_formula_name = new_goal_name
    side = "∨-intro-left" if cmd == "left" else "∨-intro-right"
    other_node = current_goal_node.arguments[1] if cmd == "left" else current_goal_node.arguments[0]
    env.proof_annotation = {
        "method": side,
        "disjunct_name": new_goal_name,
        "disjunct_node": clone_ast(selected_node),
        "other_node": clone_ast(other_node),
        "disjunction_name": current_goal_name,
        "disjunction_node": clone_ast(current_goal_node),
    }
    print(f"Goal updated to '{new_goal_name}': {reconstruct_string(env.formulae[new_goal_name])}")

@registry.register("and", category="Mission Tactics", help_text="Split Ψ∧Φ into two goals/premises")
def handle_and(env: Environment, args_str: str) -> Environment:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) == 0:
        print("Error: Usage: and [<target>] [<out_left>] <out_right>")
        return env

    arg0 = cmd_args[0]
    
    is_valid_target = False
    if arg0 in env.formulae:
        t_node = env.formulae[arg0]
        is_local = arg0 in env.local_formulae
        is_correct = isinstance(t_node, Connective) and t_node.name == "∧" and t_node.arity == 2
        if is_local and is_correct:
            is_valid_target = True
            
    if is_valid_target:
        # target is arg0
        target_name = arg0
        if len(cmd_args) == 1:
            print("Error: Usage: and <target> [<out_left>] <out_right>")
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
            print("Error: 'and' without a target can only be used inside a mission environment (active goal required).")
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

    if not (isinstance(target_node, Connective) and target_node.name == "∧" and target_node.arity == 2):
        print(f"Error: The target '{target_name}' is not of the form Ψ ∧ Φ.")
        return env

    psi_node = target_node.arguments[0]
    phi_node = target_node.arguments[1]

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
        env.and_right_formula_name = out_right_name
        env.proof_annotation = {
            "method": "∧-intro",
            "left_name": out_left_name,
            "left_node": clone_ast(psi_node),
            "right_name": out_right_name,
            "right_node": clone_ast(phi_node),
            "conjunction_name": target_name,
            "conjunction_node": clone_ast(target_node),
        }
        print(f"Conjunction goal '{target_name}' split into:")
        if out_left_name == target_name:
            print(f"  Ψ (in-place): {reconstruct_string(psi_node)}")
        else:
            print(f"  Ψ ('{out_left_name}'): {reconstruct_string(psi_node)}")
        print(f"  Φ ('{out_right_name}'): {reconstruct_string(phi_node)}")
        print(f"Now working on Φ ('{out_right_name}') in a nested environment first.")

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
                out_left_name, psi_node, "PC2", "∧-elim-left"
            )
            proof_logger.log_rule(
                [(target_name, clone_ast(target_node))],
                out_right_name, phi_node, "PC2", "∧-elim-right"
            )
        else:
            if out_left_name == target_name:
                print(f"'{out_left_name}' redefined to: {reconstruct_string(psi_node)}")
            else:
                print(f"'{out_left_name}' created as:   {reconstruct_string(psi_node)}")
            print(f"'{out_right_name}' created as:   {reconstruct_string(phi_node)}")
            
        return env

@registry.register("imply", category="Mission Tactics", help_text="Split Ψ⇒Φ or reduce goal to consequent")
def handle_imply(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) == 0:
        print("Error: Usage: imply [<target>] [<out_consequent>] <out_antecedent>")
        return

    arg0 = cmd_args[0]
    
    is_valid_target = False
    if arg0 in env.formulae:
        t_node = env.formulae[arg0]
        is_local = arg0 in env.local_formulae
        is_correct = isinstance(t_node, Connective) and t_node.name == "⇒" and t_node.arity == 2
        if is_local and is_correct:
            is_valid_target = True
            
    if is_valid_target:
        # target is arg0
        target_name = arg0
        if len(cmd_args) == 1:
            print("Error: Usage: imply <target> [<out_consequent>] <out_antecedent>")
            return
        elif len(cmd_args) == 2:
            out_consequent_name = target_name
            out_antecedent_name = cmd_args[1]
        else:
            out_consequent_name = cmd_args[1]
            out_antecedent_name = cmd_args[2]
        is_goal_target = False
    else:
        # target is goal
        if env.goal_formula_name is None:
            print("Error: 'imply' without a target can only be used inside a mission environment (active goal required).")
            return
        target_name = env.goal_formula_name
        if len(cmd_args) == 1:
            out_consequent_name = target_name
            out_antecedent_name = arg0
        else:
            out_consequent_name = arg0
            out_antecedent_name = cmd_args[1]
        is_goal_target = True

    if target_name not in env.formulae:
        print(f"Error: Target formula '{target_name}' not found.")
        return

    target_node = env.formulae[target_name]

    if not (isinstance(target_node, Connective) and target_node.name == "⇒" and target_node.arity == 2):
        print(f"Error: The target '{target_name}' is not of the form Ψ ⇒ Φ.")
        return

    psi_node = target_node.arguments[0] # Antecedent
    phi_node = target_node.arguments[1] # Consequent

    # Validate out_consequent_name
    if out_consequent_name in env.formulae and out_consequent_name != target_name:
        if not env.formulae[out_consequent_name].is_structurally_equal(phi_node):
            print(f"Error: Name '{out_consequent_name}' already exists in the environment with a different definition.")
            return
    else:
        if not enforce_no_shadowing(env, target_name, out_consequent_name, "formula"):
            return

    # Validate out_antecedent_name
    f2_error = False
    f2_action = None
    if out_antecedent_name in env.formulae and out_antecedent_name != target_name:
        if not env.formulae[out_antecedent_name].is_structurally_equal(psi_node):
            print(f"Error: Name '{out_antecedent_name}' already exists in the environment with a different definition.")
            return
        elif out_antecedent_name in env.theorems:
            f2_action = 'already_proven'
        else:
            f2_action = 'theorem_only'
    else:
        if not enforce_no_shadowing(env, target_name, out_antecedent_name, "formula"):
            return
        f2_action = 'new'

    if out_consequent_name == out_antecedent_name:
        print(f"Error: <out_consequent> and <out_antecedent> cannot have the same name ('{out_consequent_name}').")
        return

    if is_goal_target:
        # Goal Reduction (old 'imply')
        # The consequent replaces the goal
        env.formulae[out_consequent_name] = clone_ast(phi_node)

        # The antecedent becomes a proven assumption
        if f2_action == 'new':
            env.formulae[out_antecedent_name] = clone_ast(psi_node)
                
            env.add_theorem(out_antecedent_name)
            print(f"Created assumption '{out_antecedent_name}' = '{reconstruct_string(psi_node)}' as a proven theorem in this environment.")
        elif f2_action == 'theorem_only':
            env.add_theorem(out_antecedent_name)
            print(f"Registered existing formula '{out_antecedent_name}' as a proven assumption (Ψ) in this environment. "
                  f"It remains unproven in the parent environment.")
        else:
            print(f"'{out_antecedent_name}' = Ψ is already a proven theorem in scope. Using it as assumption.")

        env.goal_formula_name = out_consequent_name
        env.proof_annotation = {
            "method": "⇒-intro",
            "assumption_name": out_antecedent_name,
            "assumption_node": clone_ast(psi_node),
            "consequent_name": out_consequent_name,
            "consequent_node": clone_ast(phi_node),
        }
        
        if out_consequent_name == target_name:
            print(f"Goal updated in-place: {reconstruct_string(phi_node)}")
        else:
            print(f"Goal updated to '{out_consequent_name}' (Φ): {reconstruct_string(phi_node)}")
        print(f"Assumption '{out_antecedent_name}' (Ψ): {reconstruct_string(psi_node)} is available as proven theorem.")
    else:
        # Premise Destructuring (new functionality)
        env.formulae[out_consequent_name] = clone_ast(phi_node)
        if out_consequent_name == target_name:
            print(f"'{out_consequent_name}' redefined to: {reconstruct_string(phi_node)}")
        else:
            print(f"'{out_consequent_name}' created as:   {reconstruct_string(phi_node)}")

        if f2_action == 'new' or f2_action == 'theorem_only':
            env.formulae[out_antecedent_name] = clone_ast(psi_node)
            if out_antecedent_name == target_name:
                print(f"'{out_antecedent_name}' redefined to: {reconstruct_string(psi_node)}")
            else:
                print(f"'{out_antecedent_name}' created as:   {reconstruct_string(psi_node)}")


@registry.register("intro", category="Mission Tactics", help_text="Instantiates ∀/∃ premises or reduces goals")
def handle_intro(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) == 0:
        print("Error: Usage: intro [<target>] <term> [<out>] [<equiv>]")
        return

    arg0 = cmd_args[0]
    
    if arg0 in env.formulae:
        # arg0 is <target>
        target_name = arg0
        if len(cmd_args) < 2:
            print("Error: Usage: intro <target> <term> [<out>] [<equiv>]")
            return
        term_name = cmd_args[1]
        out_name = cmd_args[2] if len(cmd_args) > 2 else target_name
        equiv_name = cmd_args[3] if len(cmd_args) > 3 else None
        is_goal_target = False
    else:
        # arg0 is <term> (target is active goal)
        if env.goal_formula_name is None:
            print("Error: 'intro' without a target can only be used inside a mission environment (active goal required).")
            return
        target_name = env.goal_formula_name
        term_name = arg0
        out_name = cmd_args[1] if len(cmd_args) > 1 else target_name
        equiv_name = cmd_args[2] if len(cmd_args) > 2 else None
        is_goal_target = True

    if target_name not in env.formulae:
        print(f"Error: Target formula '{target_name}' not found.")
        return

    target_node = env.formulae[target_name]
    
    if not isinstance(target_node, Quantifier):
        print(f"Error: Target formula '{target_name}' is not quantified. 'intro' only works on ∀x Ψ(x) or ∃x Ψ(x).")
        return
        
    bound_var_name = target_node.variable.name
    body_node = target_node.formula
    is_universal = (target_node.name == "∀")

    if is_universal and not is_goal_target:
        # ∀-elimination on a premise: term_name must be an existing term
        instantiation_node = resolve_term(env, term_name)
        if instantiation_node is None:
            print(f"Error: Term '{term_name}' not found in the environment.")
            return
        is_fresh_var = False
        log_method = "∀-elim"
        
    elif not is_universal and is_goal_target:
        # ∃-introduction on a goal: term_name must be an existing term
        instantiation_node = resolve_term(env, term_name)
        if instantiation_node is None:
            print(f"Error: Term '{term_name}' not found in the environment.")
            return
        is_fresh_var = False
        log_method = "∃-intro"
        
    elif is_universal and is_goal_target:
        # ∀-introduction on a goal: term_name must be a FRESH variable
        if not validate_new_name(env, term_name, "variable"):
            return
        env.local_variables[term_name] = Variable(name=term_name)
        instantiation_node = Variable(name=term_name)
        is_fresh_var = True
        log_method = "∀-intro"
        
    elif not is_universal and not is_goal_target:
        # ∃-elimination on a premise: term_name must be a FRESH variable
        if not validate_new_name(env, term_name, "variable"):
            return
        env.local_variables[term_name] = Variable(name=term_name)
        instantiation_node = Variable(name=term_name)
        is_fresh_var = True
        log_method = "∃-elim"
        
    # Perform the substitution
    body_clone = clone_ast(body_node)
    from backend.SubstitutionManager import find_hidden_variable
    hidden_by = find_hidden_variable(body_clone, env, bound_var_name)
    if hidden_by:
        print(f"Error: Variable '{bound_var_name}' is hidden inside the unexpanded definition of '{hidden_by}'. You must expand '{hidden_by}' using the 'rw' command before executing this command.")
        return
        
    new_body_node = substitute_free(body_clone, bound_var_name, instantiation_node)
    
    # Check if out_name is available
    if out_name in env.formulae and out_name != target_name:
        if not env.formulae[out_name].is_structurally_equal(new_body_node):
            print(f"Error: Name '{out_name}' already exists in the environment with a different definition.")
            return
    else:
        if not enforce_no_shadowing(env, target_name, out_name, "formula"):
            return
            
    # Assign the new formula to out_name
    env.formulae[out_name] = new_body_node
        
    # Process updates depending on target type
    if is_goal_target:
        # Goal updates
        env.goal_formula_name = out_name
        env.proof_annotation = {
            "method": log_method,
            "body_name": out_name,
            "body_node": clone_ast(new_body_node),
            "bound_var": bound_var_name,
            "fresh_var": term_name if is_fresh_var else None,
            "witness_name": term_name if not is_fresh_var else None,
            "universal_goal_name": target_name if is_universal else None,
            "universal_goal_node": clone_ast(target_node) if is_universal else None,
            "existential_goal_name": target_name if not is_universal else None,
            "existential_goal_node": clone_ast(target_node) if not is_universal else None,
            "witness_node": clone_ast(instantiation_node) if not is_fresh_var else None,
        }
        
        if is_fresh_var:
            print(f"Introduced fresh variable '{term_name}' (replaces bound '{bound_var_name}').")
            print(f"Goal updated to '{out_name}': {reconstruct_string(new_body_node)}")
            print(f"Prove the body for arbitrary '{term_name}' to close universal goal '{target_name}'.")
        else:
            print(f"Goal updated to '{out_name}': {reconstruct_string(new_body_node)}")
            print(f"Prove the body with term '{term_name}' (replaces bound '{bound_var_name}') to close existential goal '{target_name}'.")
            
        if equiv_name:
            print(f"Warning: '<equiv>' theorem generation is not supported for tactic introductions. Ignoring '{equiv_name}'.")
            
    else:
        # Premise updates
        is_proven = target_name in env.theorems
        
        if is_proven:
            env.add_theorem(out_name)
            if out_name == target_name:
                print(f"'{out_name}' redefined to body: {reconstruct_string(new_body_node)}  [proven]")
            else:
                print(f"'{out_name}' created as:         {reconstruct_string(new_body_node)}  [proven]")
                
            if is_universal:
                proof_logger.log(
                    [(target_name, clone_ast(target_node))],
                    out_name, new_body_node,
                    f"axiom: Q1 ({log_method}, witness: {term_name})"
                )
            else:
                proof_logger.log(
                    [(target_name, clone_ast(target_node))],
                    out_name, new_body_node,
                    f"rule: {log_method} (fresh variable: {term_name})"
                )
        else:
            if out_name == target_name:
                print(f"'{out_name}' redefined to body: {reconstruct_string(new_body_node)}")
            else:
                print(f"'{out_name}' created as:         {reconstruct_string(new_body_node)}")
            
        # Equivalence / Implication theorem generation
        if equiv_name:
            if equiv_name in env.formulae:
                print(f"Warning: Name '{equiv_name}' already exists. Cannot create implication theorem.")
            elif not is_universal:
                print(f"Warning: Cannot generate a valid implication theorem for ∃-elimination. Ignoring '{equiv_name}'.")
            elif validate_new_name(env, equiv_name, "formula"):
                # We can construct an implication theorem: target_node => new_body_node for Q1
                impl_node = Connective("⇒", 2, [clone_ast(target_node), clone_ast(new_body_node)])
                env.formulae[equiv_name] = impl_node
                env.add_theorem(equiv_name)
                print(f"Implication theorem '{equiv_name}' created: {reconstruct_string(impl_node)}  [proven]")
                proof_logger.log_axiom(equiv_name, impl_node, "Q1")

@registry.register("apply", category="Mission Tactics", help_text="Prove goal or <target> using axiom/rule and premises")
def handle_apply(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: apply [<target>] <axiom/rule> [premises...]")
        return

    arg0 = cmd_args[0]
    
    if arg0 in AXIOMS or arg0 in RULES:
        if env.goal_formula_name is None:
            print("Error: 'apply' without a target can only be used inside a mission environment (active goal required).")
            return
        target_name = env.goal_formula_name
        rule_or_ax = arg0
        premise_names = cmd_args[1:]
    else:
        if arg0 not in env.formulae:
            print(f"Error: Target formula or axiom/rule '{arg0}' not found.")
            return
        
        if len(cmd_args) < 2:
            print("Error: Usage: apply <target> <axiom/rule> [premises...]")
            return
            
        target_name = arg0
        rule_or_ax = cmd_args[1]
        premise_names = cmd_args[2:]

    target_node = env.formulae[target_name]

    if rule_or_ax in AXIOMS:
        # Enforce formal theory
        theory_axioms = THEORY_AXIOMS.get(env.theory, set())
        if rule_or_ax not in LOGICAL_AXIOMS and rule_or_ax not in theory_axioms:
            print(f"Error: Axiom '{rule_or_ax}' is not available in the '{env.theory}' formal theory.")
            return

        if len(premise_names) != 0:
            print(f"Error: Axiom '{rule_or_ax}' takes no premises.")
            return
            
        axiom_func = AXIOMS[rule_or_ax]
        try:
            if axiom_func(target_node):
                env.add_theorem(target_name)
                if target_name == env.goal_formula_name:
                    print(f"Goal '{target_name}' satisfies axiom '{rule_or_ax}'. Mission closed.")
                else:
                    print(f"Proven theorem '{target_name}' using axiom '{rule_or_ax}'.")
                proof_logger.log_axiom(target_name, target_node, rule_or_ax)
            else:
                print(f"Error: Formula '{target_name}' does not satisfy axiom '{rule_or_ax}'.")
        except Exception as e:
            print(f"Error during axiom application: {e}")

    elif rule_or_ax in RULES:
        premise_nodes = []
        valid = True
        for p_name in premise_names:
            if p_name not in env.theorems:
                print(f"Error: Premise '{p_name}' is not a proven theorem.")
                valid = False
                break
            premise_nodes.append(env.theorems[p_name])
            
        if not valid:
            return
            
        rule_func = RULES[rule_or_ax]
        try:
            if rule_func(premise_nodes, target_node):
                env.add_theorem(target_name)
                if target_name == env.goal_formula_name:
                    print(f"Goal '{target_name}' proven using rule '{rule_or_ax}'. Mission closed.")
                else:
                    print(f"Proven theorem '{target_name}' using rule '{rule_or_ax}'.")
                    
                proof_logger.log_rule(
                    [(pn, env.theorems[pn]) for pn in premise_names],
                    target_name, target_node, rule_or_ax
                )
            else:
                print(f"Error: Formula '{target_name}' does not follow from the given premises using rule '{rule_or_ax}'.")
        except Exception as e:
            print(f"Error during rule application: {e}")
    else:
        print(f"Error: Unknown axiom or rule '{rule_or_ax}'. Supported axioms: {', '.join(AXIOMS.keys())}; rules: {', '.join(RULES.keys())}.")

@registry.register("apply2", category="Mission Tactics", help_text="Back-compute required premise from goal")
def handle_apply2(env: Environment, args_str: str) -> None:
    if env.goal_formula_name is None:
        print("Error: 'apply2' can only be used inside a mission environment (active goal required).")
        return
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) != 2:
        print("Error: Usage: apply2 <QR1|QR2> f1")
        return
    rule_name = cmd_args[0]
    f1_name = cmd_args[1]

    if rule_name not in ("QR1", "QR2"):
        print(f"Error: 'apply2' only supports QR1 and QR2 (got '{rule_name}').")
        return

    goal_name = env.goal_formula_name
    goal_node = env.formulae[goal_name]

    if not isinstance(goal_node, Connective) or goal_node.name != "⇒" or len(goal_node.arguments) != 2:
        print(f"Error: Goal '{goal_name}' is not of the form Ψ ⇒ Φ, which is required for {rule_name}.")
        return

    left, right = goal_node.arguments[0], goal_node.arguments[1]

    if rule_name == "QR1":
        if not isinstance(right, Quantifier) or right.name != "∀":
            print(f"Error: For QR1 the goal must be of the form Ψ ⇒ (∀x Φ). Got: '{reconstruct_string(goal_node)}'")
            return
        x_name = right.variable.name
        phi = right.formula
        if check_free(left, x_name, env):
            print(f"Error: Cannot apply QR1 — variable '{x_name}' occurs free in Ψ.")
            return
        if check_bound(phi, x_name):
            print(f"Error: Cannot apply QR1 — variable '{x_name}' is bound inside Φ.")
            return
        premise_node = Connective(name="⇒", arity=2, arguments=[clone_ast(left), clone_ast(phi)])
    else:  # QR2
        if not isinstance(left, Quantifier) or left.name != "∃":
            print(f"Error: For QR2 the goal must be of the form (∃x Φ) ⇒ Ψ. Got: '{reconstruct_string(goal_node)}'")
            return
        x_name = left.variable.name
        phi = left.formula
        if check_free(right, x_name, env):
            print(f"Error: Cannot apply QR2 — variable '{x_name}' occurs free in Ψ.")
            return
        if check_bound(phi, x_name):
            print(f"Error: Cannot apply QR2 — variable '{x_name}' is bound inside Φ.")
            return
        premise_node = Connective(name="⇒", arity=2, arguments=[clone_ast(phi), clone_ast(right)])

    if f1_name in env.formulae and f1_name != goal_name:
        if not env.formulae[f1_name].is_structurally_equal(premise_node):
            print(f"Error: Name '{f1_name}' is already used for a different formula.")
            return
    else:
        if not enforce_no_shadowing(env, goal_name, f1_name, "formula"):
            return
        env.formulae[f1_name] = premise_node

    env.goal_formula_name = f1_name
    env.proof_annotation = {
        "method": f"rule: {rule_name}",
        "reduced_goal_name": f1_name,
        "reduced_goal_node": clone_ast(premise_node),
        "original_goal_name": goal_name,
        "original_goal_node": clone_ast(goal_node),
        "rule": rule_name,
    }
    print(f"Goal changed to '{f1_name}': {reconstruct_string(premise_node)}")
    print(f"Prove '{f1_name}' to close the original goal via {rule_name}.")

@registry.register("apply3", category="Mission Tactics", help_text="Modus ponens backwards (goal matches RHS of f1)")
def handle_apply3(env: Environment, args_str: str) -> None:
    if env.goal_formula_name is None:
        print("Error: 'apply3' can only be used inside a mission environment (active goal required).")
        return
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) != 2:
        print("Error: Usage: apply3 f1 f2")
        return
    f1_name, f2_name = cmd_args[0], cmd_args[1]

    if f1_name not in env.theorems:
        print(f"Error: '{f1_name}' is not a proven theorem.")
        return

    impl_node = env.theorems[f1_name]
    if not isinstance(impl_node, Connective) or impl_node.name != "⇒" or len(impl_node.arguments) != 2:
        print(f"Error: Theorem '{f1_name}' is not of the form Ψ ⇒ Φ.")
        return

    psi, phi = impl_node.arguments[0], impl_node.arguments[1]
    goal_name = env.goal_formula_name
    goal_node = env.formulae[goal_name]

    if not phi.is_structurally_equal(goal_node):
        print(f"Error: The conclusion Φ of '{f1_name}' does not match the current goal '{goal_name}'.")
        return

    if f2_name in env.formulae and f2_name != goal_name:
        if not env.formulae[f2_name].is_structurally_equal(psi):
            print(f"Error: Name '{f2_name}' is already used for a different formula.")
            return
    else:
        if not enforce_no_shadowing(env, goal_name, f2_name, "formula"):
            return
        env.formulae[f2_name] = clone_ast(psi)

    env.goal_formula_name = f2_name
    env.proof_annotation = {
        "method": "modus-ponens",
        "impl_name": f1_name,
        "impl_node": clone_ast(impl_node),
        "antecedent_name": f2_name,
        "antecedent_node": clone_ast(psi),
        "consequent_name": goal_name,
        "consequent_node": clone_ast(goal_node),
    }
    print(f"Goal changed to '{f2_name}': {reconstruct_string(psi)}")
    print(f"Prove '{f2_name}' (Ψ) to close the original goal via modus ponens with '{f1_name}'.")


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


@registry.register("force", category="Direct Proof", help_text="Directly prove a formula (not allowed in games)")
def handle_force(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) != 1:
        print("Error: Usage: force <target>")
        return
        
    target_name = cmd_args[0]
    if target_name not in env.formulae:
        print(f"Error: Target formula '{target_name}' not found.")
        return
        
    node = env.formulae[target_name]
    env.add_theorem(target_name)
    proof_logger.log_axiom(target_name, node, "forced")
    
    if env.goal_formula_name and env.goal_formula_name == target_name:
        print(f"Formula '{target_name}' forced. Goal is proven! Mission accomplished.")
    else:
        print(f"Formula '{target_name}' successfully forced as a proven theorem.")
