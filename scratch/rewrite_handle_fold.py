import re

def update():
    with open('/Users/ritilranjan/ITP/CommandHandlers/transformation_handlers.py', 'r') as f:
        content = f.read()

    new_code = """
def handle_fold(env: Environment, args_str: str, validate_new_name: Callable, get_target_resolutions: Callable, handle_variable_capture_interactive: Callable) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 2:
        print("Error: Usage: fold <symbol> [<occurrences>] <f1> [<f2>] [<f3>]")
        return
    
    symbol = cmd_args[0]
    
    def get_fresh_variable_interactive(env, cat_name, node_so_far):
        print(f"Expansion of '{cat_name}' requires a new variable.")
        print(f"Expanded form so far: {reconstruct_string(node_so_far)}")
        while True:
            try:
                var_name = input(f"Enter replacement variable for '{cat_name}': ").strip()
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
        if len(cmd_args) < 2:
            print("Error: Usage: fold all <f1> [<f2>] [<f3>]")
            return
        f1_name = cmd_args[1]
        f2_name = cmd_args[2] if len(cmd_args) > 2 else f1_name
        f3_name = cmd_args[3] if len(cmd_args) > 3 else None
    
        if f1_name not in env.formulae:
            print(f"Error: Formula '{f1_name}' not found.")
            return
    
        if f2_name == f1_name:
            if f1_name not in env.local_formulae:
                print(f"Error: In-place expansion requires '{f1_name}' to be defined in the current active environment.")
                return
        else:
            if not validate_new_name(env, f2_name, "formula"):
                return
    
        f_clone = clone_ast(env.formulae[f1_name])
    
        def find_first_expandable(node: Node, env) -> Optional[Tuple[Node, str, str]]:
            if isinstance(node, Quantifier) and node.name == "∃": return node, "∃", "∃"
            if isinstance(node, Quantifier) and node.name == "∃!": return node, "∃!", "∃!"
            if isinstance(node, SetBuilder) and node.name == "{": return node, "{", "{"
            if isinstance(node, Relation) and node.name in env.user_relations: return node, "user_relation", node.name
            if isinstance(node, Function):
                if node.name in env.user_functions: return node, "user_function", node.name
                elif node.name in env.terms and isinstance(env.terms[node.name], Function):
                    t = env.terms[node.name]
                    if t.func_type == FunctionType.EPSILON_DEFINED: return node, "epsilon", node.name
                    elif t.func_type == FunctionType.IOTA_DEFINED: return node, "iota", node.name
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
                        f_clone = expand_epsilon_function_in_formula(env, f_clone, sym_name, 1, u_fresh)
                    elif cat == "iota":
                        u_fresh = get_fresh_variable_interactive(env, "iota (first variable)", f_clone)
                        if not u_fresh: return
                        v_fresh = get_fresh_variable_interactive(env, "iota (second variable)", f_clone)
                        if not v_fresh: return
                        f_clone = expand_iota_function_in_formula(env, f_clone, sym_name, 1, u_fresh, v_fresh)
                    changed = True
                    break
                except ValueError as e:
                    print(f"Error during expansion: {e}")
                    return
                except VariableCaptureError as e:
                    f_clone = handle_variable_capture_interactive(env, e, f_clone, sym_name)
    
        env.formulae[f2_name] = f_clone
        print(f"Expanded all symbols in '{f1_name}' to '{reconstruct_string(f_clone)}'")
        if f1_name in env.theorems:
            env.theorems[f2_name] = clone_ast(f_clone)
            print(f"Registered theorem '{f2_name}'")
            proof_logger.log([(f1_name, env.formulae[f1_name])], f2_name, f_clone, "definition: fold-all")
        if f3_name is not None:
            if validate_new_name(env, f3_name, "formula"):
                f1_clone = clone_ast(env.formulae[f1_name])
                f2_clone = clone_ast(f_clone)
                f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                env.formulae[f3_name] = f3_node
                env.theorems[f3_name] = clone_ast(f3_node)
                print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                proof_logger.log([(f1_name, f1_clone)], f3_name, f3_node, "definition: fold-all-equiv")
        return
        
    def parse_occurrences(args: list, start_idx: int):
        if start_idx >= len(args): return None, start_idx
        if not args[start_idx].isdigit(): return None, start_idx
        occs = []
        idx = start_idx
        expect_number = True
        while idx < len(args):
            token = args[idx]
            if expect_number:
                if token.isdigit():
                    occs.append(int(token))
                    expect_number = False
                    idx += 1
                else: break
            else:
                if token == ',':
                    expect_number = True
                    idx += 1
                else: break
        if expect_number and len(occs) > 0: idx -= 1
        return occs, idx

    occs, next_idx = parse_occurrences(cmd_args, 1)
    occurrence_idx = occs
    remaining = cmd_args[next_idx:]
    
    if len(remaining) == 0:
        print("Error: Missing formula arguments.")
        return
        
    is_term = False
    if symbol in env.user_functions:
        is_term = True
    elif symbol in env.terms and isinstance(env.terms[symbol], Function):
        t_type = env.terms[symbol].func_type
        if t_type in (FunctionType.EPSILON_DEFINED, FunctionType.IOTA_DEFINED):
            is_term = True
            
    input_name = None
    output_name = None
    f3_name = None

    if len(remaining) == 1:
        f1 = remaining[0]
        # Check if f1 is defined
        is_defined = (f1 in env.terms) if is_term else (f1 in env.formulae)
        if not is_defined:
            # Must be the <out> argument, so input is goal
            input_name = env.goal_formula_name
            if not input_name:
                print("Error: No active goal formula to fold in.")
                return
            output_name = f1
        else:
            # f1 is defined. Check if it's in local environment
            is_local = (f1 in env.local_terms) if is_term else (f1 in env.local_formulae)
            if is_local:
                # In-place fold
                input_name = f1
                output_name = f1
            else:
                print(f"Error: {'Term' if is_term else 'Formula'} '{f1}' is defined in an older environment and is immutable. Please provide an <out> name.")
                return
    elif len(remaining) == 2:
        input_name = remaining[0]
        output_name = remaining[1]
    elif len(remaining) == 3:
        input_name = remaining[0]
        output_name = remaining[1]
        f3_name = remaining[2]
    else:
        print("Error: Too many arguments.")
        return
        
    # Validate input exists
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
                elif symbol == "∃!":
                    y = get_fresh_variable_interactive(env, "∃!", target_ast)
                    if not y: return
                    expanded = expand_unique_existential_in_formula(target_ast, occurrence_idx, y)
                elif symbol == "{":
                    u = get_fresh_variable_interactive(env, "{", target_ast)
                    if not u: return
                    expanded = expand_set_builder_in_formula(env, target_ast, occurrence_idx, u)
                else:
                    if is_term:
                        is_eps = (symbol in env.terms and getattr(env.terms[symbol], 'func_type', None) == FunctionType.EPSILON_DEFINED)
                        is_io = (symbol in env.terms and getattr(env.terms[symbol], 'func_type', None) == FunctionType.IOTA_DEFINED)
                        if is_eps:
                            u = get_fresh_variable_interactive(env, "epsilon", target_ast)
                            if not u: return
                            expanded = expand_epsilon_function_in_formula(env, target_ast, symbol, occurrence_idx, u)
                        elif is_io:
                            u = get_fresh_variable_interactive(env, "iota (first var)", target_ast)
                            if not u: return
                            v = get_fresh_variable_interactive(env, "iota (second var)", target_ast)
                            if not v: return
                            expanded = expand_iota_function_in_formula(env, target_ast, symbol, occurrence_idx, u, v)
                        else:
                            expanded = expand_user_defined_function_in_formula(env, target_ast, symbol, occurrence_idx)
                    else:
                        if symbol in env.user_relations:
                            expanded = expand_user_defined_relation_in_formula(env, target_ast, symbol, occurrence_idx)
                        else:
                            print(f"Error: Unrecognized symbol '{symbol}' to fold.")
                            return
                break # Success!
            except VariableCaptureError as e:
                target_ast = handle_variable_capture_interactive(env, e, target_ast, symbol)
                # Retry expansion after capture resolution
                
    except Exception as e:
        print(f"Error expanding '{symbol}': {e}")
        return
        
    env.formulae[output_name] = expanded
    print(f"Expanded '{symbol}' to '{reconstruct_string(expanded)}'")
    
    if input_name in env.theorems:
        env.theorems[output_name] = clone_ast(expanded)
        print(f"Registered theorem '{output_name}'")
        proof_logger.log([(input_name, env.formulae[input_name])], output_name, expanded, f"definition: {symbol}-expansion")
    elif output_name in env.theorems and input_name != output_name:
        env.theorems[input_name] = clone_ast(env.formulae[input_name])
        print(f"Registered theorem '{input_name}'")
        proof_logger.log([(output_name, expanded)], input_name, env.formulae[input_name], f"definition: {symbol}-folding")

    if f3_name is not None:
        if validate_new_name(env, f3_name, "formula"):
            f1_clone = clone_ast(env.formulae[input_name])
            f2_clone = clone_ast(expanded)
            f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
            env.formulae[f3_name] = f3_node
            env.theorems[f3_name] = clone_ast(f3_node)
            print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
            proof_logger.log([(input_name, f1_clone)], f3_name, f3_node, f"definition: {symbol}-expansion-equiv")
"""

    start_str = "def handle_fold(env: Environment,"
    end_str = "def handle_simp(env: Environment,"
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx != -1 and end_idx != -1:
        new_content = content[:start_idx] + new_code + "\\n" + content[end_idx:]
        with open('/Users/ritilranjan/ITP/CommandHandlers/transformation_handlers.py', 'w') as f:
            f.write(new_content)
    else:
        print("Could not find start/end indices")

if __name__ == "__main__":
    update()
