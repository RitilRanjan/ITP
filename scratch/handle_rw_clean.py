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
                        
        def_ast = env.long_terms[name].definition_ast if name in env.long_terms else env.long_formulae[name].definition_ast
        
        while True:
            try:
                f_clone = replace_long_definition(f_clone, name, def_ast, occs, get_fresh_var, get_fresh_term)
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

def _handle_swap_base