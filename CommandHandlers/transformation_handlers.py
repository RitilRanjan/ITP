from typing import Callable, Optional, Tuple, Any
from AST import Variable, Quantifier, Connective, Node, SetBuilder, Relation, Function, FunctionType
from Environment import Environment
from Frontend import lex, reconstruct_string
from SubstitutionManager import clone_ast, substitute_free, remove_double_neg, add_double_neg, replace_structurally
from DefinitionExpander import *
from ProofLogger import proof_logger



from CommandHandlers.utils import parse_universal_args, parse_occurrences, validate_new_name, get_target_resolutions, handle_variable_capture_interactive, resolve_term
from CommandHandlers.CommandRegistry import registry

@registry.register("fold", category="Transformations", help_text="Unroll definitions (∃, ∃!, {, func/rel) or all")
def handle_fold(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: fold <symbol> [<occurrences>] <f1> [<f2>] [<f3>]")
        return
    
    symbol = cmd_args[0]
    
    def get_fresh_variable_interactive(env, cat_name, node_so_far):
        print(f"Expansion of '{cat_name}' requires a new variable.")
        print(f"Expanded form so far: {reconstruct_string(node_so_far)}")
        while True:
            try:
                from CommandHandlers.utils import get_user_input
                var_name = get_user_input(f"Enter replacement variable for '{cat_name}': ", command_queue, inputs_collected)
                if not var_name:
                    return None
                if var_name not in env.variables:
                    if not validate_new_name(env, var_name, "variable"):
                        continue
                    env.add_variable(Variable(var_name))
                    print(f"Registered fresh variable '{var_name}'")
                return var_name
            except EOFError:
                print("EOF encountered. Aborting fold.")
                raise

    if symbol == "all":
        parsed = parse_universal_args(env, "fold all", cmd_args[1:], 0, validate_new_name, supports_equiv=True, namespace="formula")
        if not parsed: return
        _, _, f1_name, f2_name, f3_name = parsed
    
        f_clone = clone_ast(env.formulae[f1_name])
    
        def find_first_expandable(node: Node, env) -> Optional[Tuple[Node, str, str]]:
            if isinstance(node, Relation) and node.name in env.user_relations: return node, "user_relation", node.name
            if isinstance(node, Function) and node.name in env.user_functions: return node, "user_function", node.name
            
            # For 'fold all', we only want to unfold macros (user_relations and user_functions)
            # Expanding primitives like ∃, ∃!, ε, ι requires fresh variables and shouldn't be done automatically.
            
            if hasattr(node, 'arguments'):
                for arg in node.arguments:
                    res = find_first_expandable(arg, env)
                    if res: return res
            elif isinstance(node, Quantifier):
                res = find_first_expandable(node.formula, env)
                if res: return res
            elif isinstance(node, SetBuilder):
                res = find_first_expandable(node.formula, env)
                if res: return res
            return None
    
        changed = True
        while changed:
            changed = False
            while True:
                res = find_first_expandable(f_clone, env)
                if not res: break
                target_node, cat, sym_name = res
                try:
                    if cat == "∃": f_clone = expand_existential_in_formula(f_clone, 1)
                    elif cat == "∃!":
                        y_fresh = get_fresh_variable_interactive(env, "∃!", f_clone)
                        if not y_fresh: return
                        f_clone = expand_unique_existential_in_formula(f_clone, 1, y_fresh)
                    elif cat == "{":
                        u_fresh = get_fresh_variable_interactive(env, "{", f_clone)
                        if not u_fresh: return
                        f_clone = expand_set_builder_in_formula(env, f_clone, 1, u_fresh)
                    elif cat == "user_relation": f_clone = expand_user_defined_relation_in_formula(env, f_clone, sym_name, 1)
                    elif cat == "user_function": f_clone = expand_user_defined_function_in_formula(env, f_clone, sym_name, 1)
                    elif cat == "epsilon":
                        u_fresh = get_fresh_variable_interactive(env, "epsilon", f_clone)
                        if not u_fresh: return
                        f_clone = expand_epsilon_in_formula(env, f_clone, 1, u_fresh)
                    elif cat == "iota":
                        u_fresh = get_fresh_variable_interactive(env, "iota (first variable)", f_clone)
                        if not u_fresh: return
                        v_fresh = get_fresh_variable_interactive(env, "iota (second variable)", f_clone)
                        if not v_fresh: return
                        f_clone = expand_iota_in_formula(env, f_clone, 1, u_fresh, v_fresh)
                    changed = True
                    break
                except ValueError as e:
                    print(f"Error during expansion: {e}")
                    return
                except VariableCaptureError as e:
                    f_clone = handle_variable_capture_interactive(env, e, f_clone, sym_name, command_queue, inputs_collected)
    
        env.formulae[f2_name] = f_clone
        print(f"Expanded all symbols in '{f1_name}' to '{reconstruct_string(f_clone)}'")
        if f1_name in env.theorems:
            env.add_theorem(f2_name)
            print(f"Registered theorem '{f2_name}'")
            proof_logger.log([(f1_name, env.formulae[f1_name])], f2_name, f_clone, "definition: fold-all")
        if f3_name is not None:
            if validate_new_name(env, f3_name, "formula"):
                f1_clone = clone_ast(env.formulae[f1_name])
                f2_clone = clone_ast(f_clone)
                f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                env.formulae[f3_name] = f3_node
                env.add_theorem(f3_name)
                print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                proof_logger.log([(f1_name, f1_clone)], f3_name, f3_node, "definition: fold-all-equiv")
        return
        
    is_term = False
    if symbol in env.user_functions:
        is_term = True
    elif symbol in ("ε", "ι"):
        is_term = False
            
    parsed = parse_universal_args(env, "fold", cmd_args, 1, validate_new_name, supports_equiv=True, namespace="formula")
    if not parsed:
        return
        
    _, occurrence_idx, input_name, output_name, f3_name = parsed

    if is_term and input_name not in env.terms:
        # Actually wait, fold operates on a target which is usually a formula containing the term!
        # wait, expanding a user defined function is done IN A FORMULA.
        # Yes, expand_user_defined_function_in_formula! It's always a formula!
        if input_name not in env.formulae:
            print(f"Error: Formula '{input_name}' not found.")
            return
    elif not is_term and input_name not in env.formulae:
        print(f"Error: Formula '{input_name}' not found.")
        return
        
    if input_name != output_name and not validate_new_name(env, output_name, "formula"):
        return
        
    target_ast = clone_ast(env.formulae[input_name])
    
    try:
        while True:
            try:
                if symbol == "∃":
                    expanded = expand_existential_in_formula(target_ast, occurrence_idx)
                elif symbol == "∀":
                    expanded = expand_universal_in_formula(target_ast, occurrence_idx)
                elif symbol == "∃!":
                    y = get_fresh_variable_interactive(env, "∃!", target_ast)
                    if not y: return
                    expanded = expand_unique_existential_in_formula(target_ast, occurrence_idx, y)
                elif symbol == "{":
                    u = get_fresh_variable_interactive(env, "{", target_ast)
                    if not u: return
                    expanded = expand_set_builder_in_formula(env, target_ast, occurrence_idx, u)
                elif symbol == "ε":
                    u = get_fresh_variable_interactive(env, "epsilon", target_ast)
                    if not u: return
                    expanded = expand_epsilon_in_formula(env, target_ast, occurrence_idx, u)
                elif symbol == "ι":
                    u = get_fresh_variable_interactive(env, "iota (first variable)", target_ast)
                    if not u: return
                    v = get_fresh_variable_interactive(env, "iota (second variable)", target_ast)
                    if not v: return
                    expanded = expand_iota_in_formula(env, target_ast, occurrence_idx, u, v)
                else:
                    if is_term:
                        expanded = expand_user_defined_function_in_formula(env, target_ast, symbol, occurrence_idx)
                    else:
                        if symbol in env.user_relations:
                            expanded = expand_user_defined_relation_in_formula(env, target_ast, symbol, occurrence_idx)
                        else:
                            print(f"Error: Unrecognized symbol '{symbol}' to fold.")
                            return
                break # Success!
            except VariableCaptureError as e:
                target_ast = handle_variable_capture_interactive(env, e, target_ast, symbol, command_queue, inputs_collected)
                # Retry expansion after capture resolution
                
    except Exception as e:
        print(f"Error expanding '{symbol}': {e}")
        return
        
    env.formulae[output_name] = expanded
    print(f"Expanded '{symbol}' to '{reconstruct_string(expanded)}'")
    
    if input_name in env.theorems:
        env.add_theorem(output_name)
        print(f"Registered theorem '{output_name}'")
        proof_logger.log([(input_name, env.formulae[input_name])], output_name, expanded, f"definition: {symbol}-expansion")
    elif output_name in env.theorems and input_name != output_name:
        env.add_theorem(input_name)
        print(f"Registered theorem '{input_name}'")
        proof_logger.log([(output_name, expanded)], input_name, env.formulae[input_name], f"definition: {symbol}-folding")

    if f3_name is not None:
        if validate_new_name(env, f3_name, "formula"):
            f1_clone = clone_ast(env.formulae[input_name])
            f2_clone = clone_ast(expanded)
            f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
            env.formulae[f3_name] = f3_node
            env.add_theorem(f3_name)
            print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
            proof_logger.log([(input_name, f1_clone)], f3_name, f3_node, f"definition: {symbol}-expansion-equiv")
@registry.register("simp_l_eq", category="Equational Rewriting", help_text="Replace LHS with RHS of theorem", aliases=["simp_r_eq", "simp_l_bi", "simp_r_bi"])
def handle_simp(env: Environment, args_str: str, cmd: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print(f"Error: Usage: {cmd} <theorem> [<occurrences>] <target> [<out>] [<equiv>]")
        return
        
    theorem_name = cmd_args[0]
    if theorem_name not in env.theorems:
        print(f"Error: '{theorem_name}' is not a proven theorem.")
        return
        
    occs, next_idx = parse_occurrences(cmd_args, 1)
    occurrence_idx = occs
    remaining = cmd_args[next_idx:]
    
    th_node = env.theorems[theorem_name]
    if cmd in ["simp_l_eq", "simp_r_eq"]:
        if not isinstance(th_node, Relation) or th_node.name != "=" or len(th_node.arguments) != 2:
            print(f"Error: Theorem '{theorem_name}' is not an equality.")
            return
        t3, t4 = th_node.arguments
        replace_from = t3 if cmd == "simp_l_eq" else t4
        replace_to = t4 if cmd == "simp_l_eq" else t3
    else:
        if not isinstance(th_node, Connective) or th_node.name != "⇔" or len(th_node.arguments) != 2:
            print(f"Error: Theorem '{theorem_name}' is not a bi-implication.")
            return
        f3, f4 = th_node.arguments
        replace_from = f3 if cmd == "simp_l_bi" else f4
        replace_to = f4 if cmd == "simp_l_bi" else f3

    is_term = False
    if len(remaining) > 0:
        f1 = remaining[0]
        if f1 in env.terms and f1 not in env.formulae:
            is_term = True
            
    parsed = parse_universal_args(env, cmd, cmd_args, 1, validate_new_name, supports_equiv=not is_term, namespace="formula")
    if not parsed: return
    _, occurrence_idx, input_name, output_name, f3_name = parsed

    target_node = env.terms[input_name] if is_term else env.formulae[input_name]
    
    try:
        new_node = replace_structurally(target_node, replace_from, replace_to, occurrence_idx)
    except Exception as e:
        print(f"Error during substitution: {e}")
        return
        
    if target_node.is_structurally_equal(new_node):
        print("Notice: No matching occurrences were found to substitute.")
        return
        
    if input_name == env.goal_formula_name:
        env.formulae[output_name] = new_node
        env.goal_formula_name = output_name
        print(f"Goal updated to '{output_name}': {reconstruct_string(new_node)}")
    elif is_term:
        env.terms[output_name] = new_node
        print(f"Saved modified term as '{output_name}': {reconstruct_string(new_node)}")
    else:
        env.formulae[output_name] = new_node
        print(f"Saved modified formula as '{output_name}': {reconstruct_string(new_node)}")
        if input_name in env.theorems:
            env.add_theorem(output_name)
            print(f"Registered theorem '{output_name}'")
            simp_axiom = "E2/E3" if cmd in ["simp_l_eq", "simp_r_eq"] else "PC2"
            simp_note = "eq-subst" if cmd in ["simp_l_eq", "simp_r_eq"] else "bi-subst"
            proof_logger.log_rule(
                [(theorem_name, th_node), (input_name, target_node)],
                output_name, new_node, simp_axiom, f"{simp_note} via {theorem_name}"
            )
            
        if f3_name is not None:
            f2_clone = clone_ast(target_node)
            f3_clone = clone_ast(new_node)
            equiv_node = Connective(name="⇔", arity=2, arguments=[f2_clone, f3_clone])
            env.formulae[f3_name] = equiv_node
            env.add_theorem(f3_name)
            print(f"Registered theorem '{f3_name}' = '{reconstruct_string(equiv_node)}'")
            proof_logger.log_rule(
                [(theorem_name, th_node), (input_name, target_node)],
                f3_name, equiv_node, "PC2", "equiv-subst"
            )

@registry.register("neg-", category="Transformations", help_text="Remove ¬¬Ψ→Ψ", aliases=["neg+"])
def handle_neg(env: Environment, args_str: str, cmd: str) -> None:
    transform_fn = remove_double_neg if cmd == "neg-" else add_double_neg
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    
    parsed = parse_universal_args(env, cmd, cmd_args, 0, validate_new_name, supports_equiv=True)
    if not parsed: return
    _, occurrence_idx, target_name, new_name, equiv_name = parsed
    
    target_node = env.formulae[target_name]
    try:
        new_node = transform_fn(target_node, occurrence_idx)
    except Exception as e:
        print(f"Error during transformation: {e}")
        return
        
    if target_node.is_structurally_equal(new_node):
        op = "double negation" if cmd == "neg-" else "negation introduction"
        print(f"Notice: No applicable site for {op} was found.")
        return
        
    save_name = new_name if new_name else target_name
    target_type = "formula" if target_name != env.goal_formula_name else "goal"
    
    if target_type == "formula":
        env.formulae[save_name] = new_node
        print(f"Saved formula '{save_name}': {reconstruct_string(new_node)}")
        if target_name in env.theorems:
            env.add_theorem(save_name)
            print(f"Registered theorem '{save_name}'")
            neg_note = "neg-elim (¬¬Ψ→Ψ)" if cmd == "neg-" else "neg-intro (Ψ→¬¬Ψ)"
            proof_logger.log_rule(
                [(target_name, target_node)],
                save_name, new_node, "PC2", neg_note
            )
        if equiv_name is not None:
            f_orig = clone_ast(target_node)
            f_new = clone_ast(new_node)
            equiv_node = Connective(name="⇔", arity=2, arguments=[f_orig, f_new])
            env.formulae[equiv_name] = equiv_node
            env.add_theorem(equiv_name)
            print(f"Registered theorem '{equiv_name}' = '{reconstruct_string(equiv_node)}'")
            proof_logger.log_rule(
                [(target_name, target_node)],
                equiv_name, equiv_node, "PC2", "neg-equiv"
            )
    elif target_type == "goal":
        env.formulae[save_name] = new_node
        env.goal_formula_name = save_name
        print(f"Goal updated to '{save_name}': {reconstruct_string(new_node)}")

@registry.register("intro2", category="Mission Tactics", help_text="Instantiate a universally quantified schema goal")
def handle_intro2(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    from AST import Relation, Function, RelationType, FunctionType, FormulaNode, TermNode, Bracket, Whitespace, DummyVariable, PropositionalVariable, MetaVariable, Connective, Quantifier, SetBuilder
    from SubstitutionManager import collect_all_occurrences, substitute_all
    
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "intro2", cmd_args, 2, validate_new_name, supports_equiv=True, namespace=None)
    if not parsed: return
    
    fixed_args, occurrence_idx, target_name, out_name, equiv_name = parsed
    schema_name = fixed_args[0]
    f1_name = fixed_args[1]
    
    if target_name not in env.formulae and target_name not in env.terms:
        print(f"Error: Target '{target_name}' not found.")
        return
        
    target_node = env.formulae[target_name] if target_name in env.formulae else env.terms[target_name]
    is_target_formula = isinstance(target_node, FormulaNode)
    
    # Identify schema
    schema_node = None
    if schema_name in env.formulae and isinstance(env.formulae[schema_name], Relation) and env.formulae[schema_name].rel_type == RelationType.SCHEMA:
        schema_node = env.formulae[schema_name]
    elif schema_name in env.terms and isinstance(env.terms[schema_name], Function) and env.terms[schema_name].func_type == FunctionType.SCHEMA:
        schema_node = env.terms[schema_name]
        
    if not schema_node:
        print(f"Error: Schema '{schema_name}' not found.")
        return
        
    # Identify f1
    if schema_name in env.formulae:
        if f1_name not in env.formulae:
            print(f"Error: Replacement '{f1_name}' must be a formula for relation schemas.")
            return
        f1_node = env.formulae[f1_name]
    else:
        f1_node = resolve_term(env, f1_name)
        if f1_node is None:
            print(f"Error: Replacement '{f1_name}' must be a term for term schemas.")
            return
        
    # Collect free variables of f1
    f1_occs = collect_all_occurrences(f1_node)
    f1_free_vars = list({o["node"].name for o in f1_occs if o["is_free"] and isinstance(o["node"], Variable)})
    
    arity = schema_node.arity
    if len(f1_free_vars) < arity:
        print(f"Error: Replacement '{f1_name}' has fewer free variables ({len(f1_free_vars)}) than the arity of schema '{schema_name}' ({arity}).")
        return
        
    # Ask for mapping
    arg_map = []
    print(f"Replacement '{f1_name}' has free variables: {', '.join(f1_free_vars)}")
    for i in range(arity):
        while True:
            try:
                from CommandHandlers.utils import get_user_input
                v_name = get_user_input(f"Map argument {i+1} of schema '{schema_name}' to which free variable of '{f1_name}'? ", command_queue, inputs_collected)
                if not v_name:
                    print("Error: Input cannot be empty.")
                    continue
                if v_name not in f1_free_vars:
                    print(f"Error: '{v_name}' is not a free variable of '{f1_name}'.")
                    continue
                arg_map.append(v_name)
                break
            except EOFError:
                print("\nEOF encountered. Aborting intro2.")
                return
                
    # Now replace occurrences
    def replace_schema_recursive(node, occurrence_idx, current_count, enclosing_quants):
        from SubstitutionManager import get_term_vars
        
        if current_count is None:
            current_count = [0]
            
        if isinstance(node, (Relation, Function)) and node.name == schema_name and node.arity == arity:
            # Check if this is the correct type of schema
            if (isinstance(node, Relation) and isinstance(schema_node, Relation)) or \
               (isinstance(node, Function) and isinstance(schema_node, Function)):
                current_count[0] += 1
                from SubstitutionManager import matches_occurrence
                if matches_occurrence(occurrence_idx, current_count[0]):
                    cloned_f1 = clone_ast(f1_node)
                    # Simulate simultaneous substitution by using fresh dummy variables
                    fresh_vars = []
                    for i in range(arity):
                        fresh = Variable(name=f"__fresh_{i}__")
                        fresh_vars.append(fresh)
                        v_target = Variable(arg_map[i])
                        from SubstitutionManager import substitute_all
                        cloned_f1 = substitute_all(cloned_f1, v_target, fresh)
                        
                    for i in range(arity):
                        fresh = fresh_vars[i]
                        t_arg = node.arguments[i]
                        
                        from SubstitutionManager import is_substitutable_free
                        # Wait, we need to check capture against the ORIGINAL f1
                        v_target = Variable(arg_map[i])
                        if not is_substitutable_free(v_target, t_arg, f1_node):
                            raise Exception(f"Variable capture detected when substituting argument {i+1} into '{f1_name}'.")
                        cloned_f1 = substitute_all(cloned_f1, fresh, clone_ast(t_arg))
                        
                    # 2. Check if the remaining free variables of f1 get captured by enclosing_quants
                    unmapped_vars = set(f1_free_vars) - set(arg_map)
                    enclosing_bound = {q.variable.name for q in enclosing_quants}
                    capture_intersection = unmapped_vars.intersection(enclosing_bound)
                    if capture_intersection:
                        raise Exception(f"Variable capture detected: free variables {capture_intersection} of '{f1_name}' get captured by enclosing quantifiers in '{target_name}'.")
                        
                    cloned_f1.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
                    cloned_f1.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
                    return cloned_f1
                    
        # Recursion
        if isinstance(node, Variable):
            c = Variable(name=node.name)
        elif isinstance(node, DummyVariable):
            c = DummyVariable(name=node.name)
        elif isinstance(node, PropositionalVariable):
            c = PropositionalVariable(name=node.name)
        elif isinstance(node, MetaVariable):
            c = MetaVariable(name=node.name)
        elif isinstance(node, Bracket):
            c = Bracket(name=node.name)
        elif isinstance(node, Whitespace):
            c = Whitespace(name=node.name)
        elif isinstance(node, Function):
            c = Function(
                name=node.name,
                arity=node.arity,
                func_type=node.func_type,
                arguments=[replace_schema_recursive(arg, occurrence_idx, current_count, enclosing_quants) for arg in node.arguments]
            )
        elif isinstance(node, Relation):
            c = Relation(
                name=node.name,
                arity=node.arity,
                rel_type=node.rel_type,
                arguments=[replace_schema_recursive(arg, occurrence_idx, current_count, enclosing_quants) for arg in node.arguments]
            )
        elif isinstance(node, Connective):
            c = Connective(
                name=node.name,
                arity=node.arity,
                arguments=[replace_schema_recursive(arg, occurrence_idx, current_count, enclosing_quants) for arg in node.arguments]
            )
        elif isinstance(node, Quantifier):
            c = Quantifier(
                name=node.name,
                variable=clone_ast(node.variable),
                formula=replace_schema_recursive(node.formula, occurrence_idx, current_count, enclosing_quants + [node])
            )
        elif isinstance(node, SetBuilder):
            c = SetBuilder(
                variable=clone_ast(node.variable),
                base_set=clone_ast(node.base_set),
                formula=replace_schema_recursive(node.formula, occurrence_idx, current_count, enclosing_quants + [node]) # node is a binder
            )
        else:
            raise ValueError(f"Unknown AST node type: {type(node)}")
            
        c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
        c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
        return c

    try:
        new_target = replace_schema_recursive(target_node, occurrence_idx, None, [])
    except Exception as e:
        print(f"Error: {e}")
        return
        
    out_name = out_name if out_name else target_name
    
    if is_target_formula:
        env.formulae[out_name] = new_target
        print(f"Created formula '{out_name}' = '{reconstruct_string(new_target)}'")
        if equiv_name:
            # Implication
            from AST import Connective
            impl = Connective(name="⇒", arity=2, arguments=[clone_ast(target_node), clone_ast(new_target)])
            env.formulae[equiv_name] = impl
            print(f"Created equivalence formula '{equiv_name}' = '{reconstruct_string(impl)}'")
            if target_name in env.theorems:
                env.theorems.add(equiv_name)
                print(f"Proven '{equiv_name}' because '{target_name}' is a theorem!")
                proof_logger.log_rule([(target_name, env.formulae[target_name])], equiv_name, impl, "intro2")
    else:
        env.terms[out_name] = new_target
        print(f"Created term '{out_name}' = '{reconstruct_string(new_target)}'")
        if equiv_name:
            # Equality
            from AST import Relation
            eq = Relation(name="=", arity=2, rel_type=RelationType.EQUALITY, arguments=[clone_ast(target_node), clone_ast(new_target)])
            env.formulae[equiv_name] = eq
            print(f"Created equivalence formula '{equiv_name}' = '{reconstruct_string(eq)}'")
            if target_name in env.theorems:
                env.theorems.add(equiv_name)
                print(f"Proven '{equiv_name}' because '{target_name}' is a theorem!")
                proof_logger.log_rule([(target_name, env.formulae[target_name])], equiv_name, eq, "intro2")
    
@registry.register("rw", category="Transformations", help_text="Rewrite a term/formula definition within another")
def handle_rw(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: rw <name> [occ] [<target>] [<out>] [<equiv>]")
        return
        
    name = cmd_args[0]
    
    if name not in env.terms and name not in env.formulae:
        print(f"Error: '{name}' is not a defined term or formula.")
        return
        
    occs, idx = parse_occurrences(cmd_args, 1)
    if occs is not None:
        if 0 in occs: occs = None
        remaining = cmd_args[idx:]
    else:
        remaining = cmd_args[1:]
        
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
        if not is_formula_target:
            print("Error: Equivalence generation is only supported for formulas.")
            return
        if not validate_new_name(env, equiv_name, "formula"):
            return

    if is_formula_target:
        original_ast = env.local_formulae.get(target_name, env.formulae.get(target_name))
    else:
        original_ast = env.local_terms.get(target_name, env.terms.get(target_name))
        
    if name in env.terms:
        def_ast = env.terms[name]
        from AST import Variable
        search_node = Variable(name)
        is_prop = False
    else:
        def_ast = env.formulae[name]
        from AST import PropositionalVariable
        search_node = PropositionalVariable(name)
        is_prop = True

    f_clone = clone_ast(original_ast)

    while True:
        occs_list = collect_all_occurrences(f_clone)
        if is_prop:
            targets = [o for o in occs_list if o["node"].name == search_node.name and isinstance(o["node"], PropositionalVariable)]
        else:
            targets = [o for o in occs_list if o["node"].name == search_node.name and o["is_free"] and isinstance(o["node"], Variable)]
            
        if occs is not None:
            targets = [targets[i - 1] for i in occs if 1 <= i <= len(targets)]
            
        capturing_vars = set()
        from SubstitutionManager import get_free
        free_in_def = get_free(def_ast)
        for o in targets:
            enclosing_vars = {q.variable.name for q in o["enclosing_quantifiers"]}
            capture = free_in_def.intersection(enclosing_vars)
            capturing_vars.update(capture)
            
        if capturing_vars:
            try:
                from DefinitionExpander import VariableCaptureError
                raise VariableCaptureError("Variable capture detected.", list(capturing_vars), clone_ast(def_ast))
            except VariableCaptureError as e:
                handle_variable_capture_interactive(env, e, f_clone, name, command_queue, inputs_collected)
                continue
        break
        
    if is_prop:
        from SubstitutionManager import substitute_proposition
        if not is_formula_target:
            print("Error: Cannot substitute a propositional formula into a term.")
            return
        substitute_proposition(f_clone, search_node, clone_ast(def_ast), occs)
    else:
        if is_formula_target:
            from SubstitutionManager import substitute_free
            substitute_free(f_clone, search_node, clone_ast(def_ast), occs)
        else:
            from SubstitutionManager import substitute_term
            substitute_term(f_clone, search_node, clone_ast(def_ast), occs)
            
    if original_ast.is_structurally_equal(f_clone):
        print("Notice: No matching occurrences were found to substitute.")
        return
        
    if is_formula_target:
        env.formulae[out_name] = f_clone
        print(f"Expanded '{name}' to '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems:
            env.add_theorem(out_name)
            print(f"Registered theorem '{out_name}'")
            proof_logger.log([(target_name, original_ast)], out_name, f_clone, f"rw: replace {name}")
            
        if equiv_name is not None:
            f1_clone = clone_ast(original_ast)
            f2_clone = clone_ast(f_clone)
            f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
            env.formulae[equiv_name] = f3_node
            env.add_theorem(equiv_name)
            print(f"Registered theorem '{equiv_name}' = '{reconstruct_string(f3_node)}'")
            proof_logger.log([(target_name, f1_clone)], equiv_name, f3_node, f"rw: {name}-equiv")
    else:
        env.terms[out_name] = f_clone
        print(f"Expanded term '{name}' to '{reconstruct_string(f_clone)}'")
