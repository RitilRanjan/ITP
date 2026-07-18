import re

with open('backend/CommandHandlers/env_handlers.py', 'r') as f:
    c = f.read()

def patch_handler(handler_name, expected_type, help_text):
    old_def = f'''@registry.register("{handler_name}", category="Environment", help_text="{help_text}")
def handle_{handler_name}(env: Environment, args_str: str) -> None:'''
    
    new_logic = f'''@registry.register("{handler_name}", category="Environment", help_text="{help_text}")
def handle_{handler_name}(env: Environment, args_str: str) -> None:
    args_str = args_str.strip()
    if '"' in args_str:
        parts = args_str.split('"', 2)
        if len(parts) < 3:
            print(f"Error: Missing closing quote for long {expected_type} pattern.")
            return
            
        pre_quote = parts[0].strip().split()
        if len(pre_quote) == 0:
            print(f"Error: Missing identifier for long {expected_type}.")
            return
        elif len(pre_quote) > 2:
            print(f"Error: Too many arguments before name for long {expected_type}.")
            return
            
        identifier = pre_quote[0]
        priority = 0
        if len(pre_quote) == 2:
            try:
                priority = int(pre_quote[1])
            except ValueError:
                print(f"Error: Priority must be an integer, got '{{pre_quote[1]}}'")
                return
                
        long_name = parts[1]
        definition_expr = parts[2].strip()
        
        if not validate_new_name(env, identifier, "{expected_type}"):
            return
        
        try:
            from backend.Environment import LongDefinition
            from backend.AST import DefinitionType
            from backend.Parser import lex
            from backend.MacroExpander import compute_macro_free_variables
            
            pattern = [t for t in lex(long_name) if not t.isspace()]
            def_tokens = [t for t in lex(definition_expr) if not t.isspace()]
            
            free_vars = compute_macro_free_variables(pattern, def_tokens, env, "{expected_type}") if def_tokens else set()
            
            def_type = DefinitionType.SCHEMA if not def_tokens else DefinitionType.USER_DEFINED
            long_def = LongDefinition(name=identifier, pattern=pattern, definition_tokens=def_tokens, def_type=def_type)
            long_def.priority = priority
            if "{expected_type}" == "term":
                env.long_terms[identifier] = long_def
            else:
                env.long_formulae[identifier] = long_def
            env.local_free_vars_cache[identifier] = free_vars
            print(f"Created {{'schema' if not def_tokens else f'long {expected_type} notation'}} '{{identifier}}' (priority {{priority}}) with pattern '{{long_name}}'")
        except Exception as e:
            import traceback; traceback.print_exc()
        return

    sub_parts = args_str.split()
    if len(sub_parts) < 2:
        print(f"Error: Usage: {handler_name} [<priority>] <name> <definition>")
        return
        
    priority = 0
    name_idx = 0
    if len(sub_parts) > 2:
        try:
            priority = int(sub_parts[0])
            name_idx = 1
        except ValueError:
            pass # First arg wasn't an integer, so priority defaults to 0
            
    name = sub_parts[name_idx]
    expr = " ".join(sub_parts[name_idx+1:])
    
    if not validate_new_name(env, name, "{expected_type}"):
        return
    try:
        if "{expected_type}" == "term":
            ast = parse_term(expr, env)
            ast.priority = priority
            env.terms[name] = ast
        else:
            ast = parse_fol_formula(expr, env)
            ast.priority = priority
            env.formulae[name] = ast
        from backend.SubstitutionManager import compute_free_variables
        env.local_free_vars_cache[name] = compute_free_variables(ast, env)
        print(f"Created {expected_type} '{{name}}' (priority {{priority}}) = '{{reconstruct_string(ast)}}'")
    except Exception as e:
        import traceback; traceback.print_exc()'''

    return re.sub(old_def + r'.*?(?=\n@registry|\Z)', new_logic + '\n', c, flags=re.DOTALL)

c = patch_handler("ct", "term", "Create a term")
c = patch_handler("cf", "formula", "Create a 1st-order formula")

with open('backend/CommandHandlers/env_handlers.py', 'w') as f:
    f.write(c)

