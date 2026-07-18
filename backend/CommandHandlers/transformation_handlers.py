from typing import Callable, Optional, Tuple, Any
from backend.AST import Variable, Quantifier, Connective, Node,  Constant, PropositionalVariable
from backend.Environment import Environment
from backend.Parser import lex, reconstruct_string, parse_fol_formula, parse_prop_formula, parse_term
from backend.SubstitutionManager import clone_ast, substitute_free, remove_double_neg, add_double_neg, replace_structurally, swap_ast_nodes
from backend.DefinitionExpander import *
from backend.ProofLogger import proof_logger



from backend.CommandHandlers.utils import parse_universal_args, parse_occurrences, validate_new_name, get_target_resolutions, handle_variable_capture_interactive, resolve_term
from backend.CommandHandlers.CommandRegistry import registry

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
                from backend.CommandHandlers.utils import get_user_input
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
            if isinstance(node, Quantifier) and node.name == "∃": return node, "∃", "∃"
            if isinstance(node, Quantifier) and node.name == "∃!": return node, "∃!", "∃!"

            if isinstance(node, Epsilon): return node, "epsilon", "ε"
            if isinstance(node, Iota): return node, "iota", "ι"
            
            if hasattr(node, 'arguments'):
                for arg in node.arguments:
                    res = find_first_expandable(arg, env)
                    if res: return res
            elif isinstance(node, Quantifier):
                res = find_first_expandable(node.formula, env)
                if res: return res
            elif isinstance(node, (Iota, Epsilon)):
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
        if f1_name == env.goal_formula_name:
            env.goal_formula_name = f2_name
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
    if symbol in ("ε", "ι"):
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
    if input_name == env.goal_formula_name:
        env.goal_formula_name = output_name
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
        from backend.AST import LongFormula
        if not isinstance(th_node, LongFormula) or th_node.definition_name != "=":
            print(f"Error: Theorem '{theorem_name}' is not an equality.")
            return
        t3, t4 = th_node.term_placeholders["?t1"], th_node.term_placeholders["?t2"]
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
        if input_name == env.goal_formula_name:
            env.goal_formula_name = output_name
        print(f"Goal updated to '{output_name}': {reconstruct_string(new_node)}")
    elif is_term:
        env.terms[output_name] = new_node
        print(f"Saved modified term as '{output_name}': {reconstruct_string(new_node)}")
    else:
        env.formulae[output_name] = new_node
        if input_name == env.goal_formula_name:
            env.goal_formula_name = output_name
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
        if target_name == env.goal_formula_name:
            env.goal_formula_name = save_name
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
        if target_name == env.goal_formula_name:
            env.goal_formula_name = save_name
        print(f"Goal updated to '{save_name}': {reconstruct_string(new_node)}")

@registry.register("intro2", category="Mission Tactics", help_text="Instantiate a universally quantified schema goal")
def handle_intro2(env, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    from backend.AST import FormulaNode, TermNode, LongTerm, LongFormula, DefinitionType
    from backend.SubstitutionManager import matches_occurrence, extract_flat_nodes, map_flat_nodes_to_pattern
    from backend.CommandHandlers.utils import parse_universal_args, validate_new_name
    from backend.Parser import lex, reconstruct_string
    
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
    is_formula_target = isinstance(target_node, FormulaNode)
    
    if schema_name not in env.long_formulae and schema_name not in env.long_terms:
        print(f"Error: Schema '{schema_name}' not found.")
        return
        
    schema_def = env.long_formulae[schema_name] if schema_name in env.long_formulae else env.long_terms[schema_name]
    if schema_def.def_type != DefinitionType.SCHEMA:
        print(f"Error: '{schema_name}' is not a schema.")
        return
        
    if f1_name not in env.long_formulae and f1_name not in env.long_terms:
        print(f"Error: Replacement '{f1_name}' not found.")
        return
        
    f1_def = env.long_formulae[f1_name] if f1_name in env.long_formulae else env.long_terms[f1_name]
    
    from backend.SubstitutionManager import clone_ast
    
    def replace_schema_recursive(node, current_count):
        if current_count is None:
            current_count = [0]
            
        if isinstance(node, (LongTerm, LongFormula)) and node.definition_name == schema_name:
            current_count[0] += 1
            if matches_occurrence(occurrence_idx, current_count[0]):
                flat_nodes = extract_flat_nodes(schema_def.pattern, node.term_placeholders, node.var_placeholders, node.formula_placeholders, node.repetition_counts)
                flat_clones = [clone_ast(n) for n in flat_nodes]
                
                try:
                    tp, vp, fp, rc = map_flat_nodes_to_pattern(flat_clones, f1_def.pattern)
                except ValueError as e:
                    raise Exception(f"Failed to match schema placeholders: {e}")
                    
                if f1_name in env.long_formulae:
                    new_node = LongFormula(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type, pattern=f1_def.pattern)
                else:
                    new_node = LongTerm(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type, pattern=f1_def.pattern)
                    
                new_node.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
                new_node.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
                return new_node
                
        # Recursion for LongTerm/LongFormula
        if isinstance(node, (LongTerm, LongFormula)):
            tp = {k: (replace_schema_recursive(v, current_count) if not isinstance(v, list) else [replace_schema_recursive(x, current_count) for x in v]) for k, v in node.term_placeholders.items()}
            vp = {k: (replace_schema_recursive(v, current_count) if not isinstance(v, list) else [replace_schema_recursive(x, current_count) for x in v]) for k, v in node.var_placeholders.items()}
            fp = {k: (replace_schema_recursive(v, current_count) if not isinstance(v, list) else [replace_schema_recursive(x, current_count) for x in v]) for k, v in node.formula_placeholders.items()}
            
            if isinstance(node, LongFormula):
                c = LongFormula(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type, pattern=node.pattern)
            else:
                c = LongTerm(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type, pattern=node.pattern)
            c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
            c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
            return c
            
        from backend.AST import Variable, DummyVariable, PropositionalVariable, MetaVariable, Bracket, Whitespace, Connective, Quantifier, Constant, Iota, Epsilon
        if isinstance(node, Variable): c = Variable(name=node.name)
        elif isinstance(node, DummyVariable): c = DummyVariable(name=node.name)
        elif isinstance(node, PropositionalVariable): c = PropositionalVariable(name=node.name)
        elif isinstance(node, MetaVariable): c = MetaVariable(name=node.name)
        elif isinstance(node, Bracket): c = Bracket(name=node.name)
        elif isinstance(node, Whitespace): c = Whitespace(name=node.name)
        elif isinstance(node, Constant): c = Constant(name=node.name)
        elif isinstance(node, Connective):
            c = Connective(name=node.name, arity=node.arity, arguments=[replace_schema_recursive(arg, current_count) for arg in node.arguments])
        elif isinstance(node, Quantifier):
            c = Quantifier(name=node.name, variable=clone_ast(node.variable), formula=replace_schema_recursive(node.formula, current_count))
        elif isinstance(node, Iota):
            c = Iota(variable=clone_ast(node.variable), formula=replace_schema_recursive(node.formula, current_count))
        elif isinstance(node, Epsilon):
            c = Epsilon(variable=clone_ast(node.variable), formula=replace_schema_recursive(node.formula, current_count))
        else:
            c = clone_ast(node)
            
        if not isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable, Bracket, Whitespace, Constant)):
            c.prefix_formatting = [clone_ast(f) for f in getattr(node, 'prefix_formatting', [])]
            c.postfix_formatting = [clone_ast(f) for f in getattr(node, 'postfix_formatting', [])]
        return c

    original_ast = target_node
    try:
        f_clone = replace_schema_recursive(target_node, [0])
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"Error during intro2 replacement: {e}")
        return

    if original_ast.is_structurally_equal(f_clone):
        print("Notice: No matching occurrences were found to substitute.")
        return
        
    from backend.CommandHandlers.transformation_handlers import proof_logger
    if is_formula_target:
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Expanded '{schema_name}' to '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems:
            env.add_theorem(out_name)
            print(f"Registered theorem '{out_name}'")
            proof_logger.log([(target_name, original_ast)], out_name, f_clone, f"intro2: {schema_name}")
            
        if equiv_name is not None:
            from backend.AST import Connective
            f3_node = Connective(name="⇔", arity=2, arguments=[clone_ast(original_ast), clone_ast(f_clone)])
            env.formulae[equiv_name] = f3_node
            env.add_theorem(equiv_name)
            print(f"Registered theorem '{equiv_name}' = '{reconstruct_string(f3_node)}'")
            proof_logger.log([(target_name, clone_ast(original_ast))], equiv_name, f3_node, f"intro2: {schema_name}-equiv")
    else:
        env.terms[out_name] = f_clone
        print(f"Expanded term '{schema_name}' to '{reconstruct_string(f_clone)}'")




@registry.register("rw", category="Transformations", help_text="Rewrite a term/formula definition within another")
def handle_rw(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    args_str = args_str.strip()
    is_long = False
    
    if args_str.startswith('"'):
        end_quote = args_str.find('"', 1)
        if end_quote == -1:
            print("Error: Missing closing quote for name.")
            return
        name = args_str[1:end_quote]
        remaining_str = args_str[end_quote+1:].strip()
        cmd_args = [t for t in lex(remaining_str) if not t.isspace()]
        is_long = True
    else:
        cmd_args = [t for t in lex(args_str) if not t.isspace()]
        if len(cmd_args) < 1:
            print("Error: Usage: rw <name> [occ] [<target>] [<out>] [<equiv>]")
            return
        name = cmd_args[0]
        cmd_args = cmd_args[1:]
        
    if is_long:
        if name not in env.long_terms and name not in env.long_formulae:
            print(f"Error: Long notation '{name}' not found.")
            return
    else:
        if name not in env.terms and name not in env.formulae:
            print(f"Error: '{name}' is not a defined term or formula.")
            return
            
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
        if not is_formula_target:
            print("Error: Equivalence generation is only supported for formulas.")
            return
        if not validate_new_name(env, equiv_name, "formula"):
            return

    if is_formula_target:
        original_ast = env.local_formulae.get(target_name, env.formulae.get(target_name))
    else:
        original_ast = env.local_terms.get(target_name, env.terms.get(target_name))
        
    f_clone = clone_ast(original_ast)

    if is_long:
        from backend.DefinitionReplacer import replace_long_definition, VariableCaptureError
        from backend.AST import Variable
        from backend.Parser import parse_term
        from backend.CommandHandlers.utils import get_user_input
        
        def get_fresh_var(ph):
            while True:
                v = get_user_input(f"Enter variable for placeholder '{ph}': ", command_queue, inputs_collected)
                if v and validate_new_name(env, v, "variable"):
                    env.add_variable(Variable(v))
                    return Variable(v)
        
        def get_fresh_term(ph):
            while True:
                t = get_user_input(f"Enter term for placeholder '{ph}': ", command_queue, inputs_collected)
                if t:
                    try:
                        return parse_term(t, env)
                    except Exception as e:
                        print(f"Error parsing term: {e}")
                        
        long_def = env.long_terms[name] if name in env.long_terms else env.long_formulae[name]
        if not long_def.definition_tokens:
            print(f"Error: Long notation '{name}' is a schema and has no definition to expand.")
            return
            
        definition_expr = " ".join(long_def.definition_tokens)
        def_ast = parse_term(definition_expr, env) if name in env.long_terms else parse_fol_formula(definition_expr, env)
        
        while True:
            try:
                f_clone = replace_long_definition(f_clone, name, def_ast, occs, get_fresh_var, get_fresh_term, env)
                break
            except VariableCaptureError as e:
                f_clone = handle_variable_capture_interactive(env, e, f_clone, name, command_queue, inputs_collected)
    else:
        if name in env.terms:
            def_ast = env.terms[name]
            from backend.AST import Constant, Variable
            if name in env.variables or name in env.local_variables:
                search_node = Variable(name)
            else:
                search_node = Constant(name)
            is_prop = False
        else:
            def_ast = env.formulae[name]
            from backend.AST import PropositionalVariable
            search_node = PropositionalVariable(name)
            is_prop = True
            
        while True:
            from backend.SubstitutionManager import collect_all_occurrences
            occs_list = collect_all_occurrences(f_clone)
            if is_prop:
                targets = [o for o in occs_list if o["node"].name == search_node.name and isinstance(o["node"], PropositionalVariable)]
            else:
                from backend.AST import Constant
                targets = [o for o in occs_list if o["node"].name == search_node.name and o["is_free"] and isinstance(o["node"], (Variable, Constant))]
                
            if occs is not None:
                targets = [targets[i - 1] for i in occs if 1 <= i <= len(targets)]
                
            capturing_vars = set()
            from backend.SubstitutionManager import get_free
            free_in_def = get_free(def_ast)
            for o in targets:
                enclosing_vars = {q.variable.name for q in o["enclosing_quantifiers"]}
                capture = free_in_def.intersection(enclosing_vars)
                capturing_vars.update(capture)
                
            if capturing_vars:
                try:
                    from backend.DefinitionExpander import VariableCaptureError
                    raise VariableCaptureError("Variable capture detected.", list(capturing_vars), clone_ast(def_ast))
                except VariableCaptureError as e:
                    handle_variable_capture_interactive(env, e, f_clone, name, command_queue, inputs_collected)
                    continue
            break
            
        if is_prop:
            from backend.SubstitutionManager import substitute_proposition
            if not is_formula_target:
                print("Error: Cannot substitute a propositional formula into a term.")
                return
            substitute_proposition(f_clone, search_node, clone_ast(def_ast), occs)
        else:
            if is_formula_target:
                from backend.SubstitutionManager import substitute_free
                substitute_free(f_clone, search_node, clone_ast(def_ast), occs)
            else:
                from backend.SubstitutionManager import substitute_term
                substitute_term(f_clone, search_node, clone_ast(def_ast), occs)
                
    if original_ast.is_structurally_equal(f_clone):
        print("Notice: No matching occurrences were found to substitute.")
        return
        
    if is_formula_target:
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Expanded '{name}' to '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems:
            env.add_theorem(out_name)
            print(f"Registered theorem '{out_name}'")
            proof_logger.log([(target_name, original_ast)], out_name, f_clone, f"rw: replace {name}")
            
        if equiv_name is not None:
            f1_clone = clone_ast(original_ast)
            f2_clone = clone_ast(f_clone)
            from backend.AST import Connective
            f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
            env.formulae[equiv_name] = f3_node
            env.add_theorem(equiv_name)
            print(f"Registered theorem '{equiv_name}' = '{reconstruct_string(f3_node)}'")
            proof_logger.log([(target_name, f1_clone)], equiv_name, f3_node, f"rw: {name}-equiv")
    else:
        env.terms[out_name] = f_clone
        print(f"Expanded term '{name}' to '{reconstruct_string(f_clone)}'")



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
            env.add_theorem(out_name)
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
                env.add_theorem(equiv_name)
                print(f"Proven '{equiv_name}' because '{target_name}' is a theorem!")
                proof_logger.log_rule([(target_name, env.formulae[target_name])], equiv_name, eq, f"{cmd_name}_equiv")
                
    elif is_term_target:
        env.terms[out_name] = new_target
        if out_name not in env.local_terms:
            env.local_terms[out_name] = new_target
        print(f"Term '{out_name}' = '{reconstruct_string(new_target)}'")
        
        if equiv_name:
            eq = LongFormula(definition_name="=", term_placeholders={"t1": clone_ast(target_node), "t2": clone_ast(new_target)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})
            env.formulae[equiv_name] = eq
            if equiv_name not in env.local_formulae:
                env.local_formulae[equiv_name] = eq
            print(f"Created equivalence formula '{equiv_name}' = '{reconstruct_string(eq)}'")
            if target_name in env.theorems:
                env.add_theorem(equiv_name)
                print(f"Proven '{equiv_name}' because '{target_name}' is a theorem!")
                proof_logger.log_rule([(target_name, env.terms[target_name])], equiv_name, eq, f"{cmd_name}_equiv")

@registry.register("swap_eq", category="Transformations", help_text="Swap LHS and RHS of '=' in target term/formula")
def handle_swap_eq(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    _handle_swap_base(env, args_str, "=", True, "swap_eq")

@registry.register("swap_bi", category="Transformations", help_text="Swap LHS and RHS of '⇔' in target formula")
def handle_swap_bi(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    _handle_swap_base(env, args_str, "⇔", False, "swap_bi")

