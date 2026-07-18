from typing import Callable, Any

from backend.AST import Variable, PropositionalVariable
from backend.Environment import Environment
from backend.Parser import lex, reconstruct_string, parse_term, parse_fol_formula, parse_prop_formula
from backend.CommandHandlers.transformation_handlers import parse_occurrences
from backend.SubstitutionManager import (
    clone_ast, substitute_term, is_substitutable_free, substitute_free,
    is_substitutable_bound, substitute_bound, substitute_all, collect_all_occurrences, substitute_proposition
)
from backend.CommandHandlers.CommandRegistry import registry
from backend.CommandHandlers.utils import validate_new_name, parse_universal_args, resolve_term

@registry.register("cv", category="Environment", help_text="Create FOL variables")
def handle_cv(env: Environment, args_str: str) -> None:
    if not args_str:
        print("Error: Missing variable name.")
        return
    names = args_str.strip().split()
    for name in names:
        if not validate_new_name(env, name, "variable"):
            continue
        try:
            env.add_variable(Variable(name=name))
            print(f"Created standard variable '{name}'")
        except Exception as e:
            import traceback; traceback.print_exc()

@registry.register("cV", category="Environment", help_text="Create propositional variables")
def handle_cV(env: Environment, args_str: str) -> None:
    if not args_str:
        print("Error: Missing propositional variable name.")
        return
    names = args_str.strip().split()
    for name in names:
        if not validate_new_name(env, name, "propositional_variable"):
            continue
        try:
            env.add_propositional_variable(PropositionalVariable(name=name))
            print(f"Created propositional variable '{name}'")
        except Exception as e:
            import traceback; traceback.print_exc()

@registry.register("ct", category="Environment", help_text="Create a term")
def handle_ct(env: Environment, args_str: str) -> None:
    args_str = args_str.strip()
    if '"' in args_str:
        parts = args_str.split('"', 2)
        if len(parts) < 3:
            print(f"Error: Missing closing quote for long term pattern.")
            return
            
        pre_quote = parts[0].strip().split()
        if len(pre_quote) == 0:
            print(f"Error: Missing identifier for long term.")
            return
        elif len(pre_quote) > 2:
            print(f"Error: Too many arguments before name for long term.")
            return
            
        identifier = pre_quote[0]
        priority = 0
        if len(pre_quote) == 2:
            try:
                priority = int(pre_quote[1])
            except ValueError:
                print(f"Error: Priority must be an integer, got '{pre_quote[1]}'")
                return
                
        long_name = parts[1]
        definition_expr = parts[2].strip()
        
        if not validate_new_name(env, identifier, "term"):
            return
        
        try:
            from backend.Environment import LongDefinition
            from backend.AST import DefinitionType
            from backend.Parser import lex
            from backend.MacroExpander import compute_macro_free_variables
            
            pattern = [t for t in lex(long_name) if not t.isspace()]
            def_tokens = [t for t in lex(definition_expr) if not t.isspace()]
            
            free_vars = compute_macro_free_variables(pattern, def_tokens, env, "term") if def_tokens else set()
            
            def_type = DefinitionType.SCHEMA if not def_tokens else DefinitionType.USER_DEFINED
            long_def = LongDefinition(name=identifier, pattern=pattern, definition_tokens=def_tokens, def_type=def_type)
            long_def.priority = priority
            env.long_terms[identifier] = long_def
            env.local_free_vars_cache[identifier] = free_vars
            print(f"Created {'schema' if not def_tokens else f'long term notation'} '{identifier}' (priority {priority}) with pattern '{long_name}'")
        except Exception as e:
            import traceback; traceback.print_exc()
        return

    sub_parts = args_str.split()
    if len(sub_parts) < 2:
        print(f"Error: Usage: ct [<priority>] <name> <definition>")
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
    
    if not validate_new_name(env, name, "term"):
        return
    try:
        ast = parse_term(expr, env)
        ast.priority = priority
        env.terms[name] = ast
        from backend.SubstitutionManager import compute_free_variables
        env.local_free_vars_cache[name] = compute_free_variables(ast, env)
        print(f"Created term '{name}' (priority {priority}) = '{reconstruct_string(ast)}'")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("cf", category="Environment", help_text="Create a 1st-order formula")
def handle_cf(env: Environment, args_str: str) -> None:
    args_str = args_str.strip()
    if '"' in args_str:
        parts = args_str.split('"', 2)
        if len(parts) < 3:
            print(f"Error: Missing closing quote for long formula pattern.")
            return
            
        pre_quote = parts[0].strip().split()
        if len(pre_quote) == 0:
            print(f"Error: Missing identifier for long formula.")
            return
        elif len(pre_quote) > 2:
            print(f"Error: Too many arguments before name for long formula.")
            return
            
        identifier = pre_quote[0]
        priority = 0
        if len(pre_quote) == 2:
            try:
                priority = int(pre_quote[1])
            except ValueError:
                print(f"Error: Priority must be an integer, got '{pre_quote[1]}'")
                return
                
        long_name = parts[1]
        definition_expr = parts[2].strip()
        
        if not validate_new_name(env, identifier, "formula"):
            return
        
        try:
            from backend.Environment import LongDefinition
            from backend.AST import DefinitionType
            from backend.Parser import lex
            from backend.MacroExpander import compute_macro_free_variables
            
            pattern = [t for t in lex(long_name) if not t.isspace()]
            def_tokens = [t for t in lex(definition_expr) if not t.isspace()]
            
            free_vars = compute_macro_free_variables(pattern, def_tokens, env, "fol") if def_tokens else set()
            
            def_type = DefinitionType.SCHEMA if not def_tokens else DefinitionType.USER_DEFINED
            long_def = LongDefinition(name=identifier, pattern=pattern, definition_tokens=def_tokens, def_type=def_type)
            long_def.priority = priority
            env.long_formulae[identifier] = long_def
            env.local_free_vars_cache[identifier] = free_vars
            print(f"Created {'schema' if not def_tokens else f'long formula notation'} '{identifier}' (priority {priority}) with pattern '{long_name}'")
        except Exception as e:
            import traceback; traceback.print_exc()
        return

    sub_parts = args_str.split()
    if len(sub_parts) < 2:
        print(f"Error: Usage: cf [<priority>] <name> <definition>")
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
    
    if not validate_new_name(env, name, "formula"):
        return
    try:
        ast = parse_fol_formula(expr, env)
        ast.priority = priority
        env.formulae[name] = ast
        from backend.SubstitutionManager import compute_free_variables
        env.local_free_vars_cache[name] = compute_free_variables(ast, env)
        print(f"Created formula '{name}' (priority {priority}) = '{reconstruct_string(ast)}'")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("cp", category="Environment", help_text="Create a propositional formula")
def handle_cp(env: Environment, args_str: str) -> None:
    sub_parts = args_str.split(maxsplit=1)
    if len(sub_parts) < 2:
        print("Error: Usage: cp <name> <definition>")
        return
    name = sub_parts[0]
    expr = sub_parts[1]
    if not validate_new_name(env, name, "formula"):
        return
    try:
        ast = parse_prop_formula(expr, env)
        env.formulae[name] = ast
        from backend.SubstitutionManager import compute_free_variables
        env.local_free_vars_cache[name] = compute_free_variables(ast, env)
        print(f"Created propositional formula '{name}' = '{reconstruct_string(ast)}'")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("st", category="Transformations", help_text="Substitute term t1 for var v in term")
def handle_st(env: Environment, args_str: str, cmd: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "st", cmd_args, 2, validate_new_name, supports_equiv=False, namespace="term")
    if not parsed: return
    fixed_args, occurrence_idx, target_name, out_name, _ = parsed
    
    x = fixed_args[0]
    t1_name = fixed_args[1]

    t1_clone = resolve_term(env, t1_name)
    if t1_clone is None:
        print(f"Error: Term '{t1_name}' not found in environment.")
        return

    t_clone = clone_ast(env.terms[target_name])
    from backend.SubstitutionManager import find_hidden_variable
    hidden_by = find_hidden_variable(t_clone, env, x)
    if hidden_by:
        print(f"Error: Variable '{x}' is hidden inside the unexpanded definition of '{hidden_by}'. You must expand '{hidden_by}' using the 'rw' command before executing this command.")
        return
        
    try:
        substitute_term(t_clone, x, t1_clone, occurrence_idx)
        env.terms[out_name] = t_clone
        print(f"Created term '{out_name}' = '{reconstruct_string(t_clone)}'")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("sf", category="Transformations", help_text="Substitute term t1 for free var v")
def handle_sf(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "sf", cmd_args, 2, validate_new_name, supports_equiv=False)
    if not parsed: return
    fixed_args, occurrence_idx, target_name, out_name, _ = parsed
    
    x = fixed_args[0]
    t1_name = fixed_args[1]

    t1_clone = resolve_term(env, t1_name)
    if t1_clone is None:
        print(f"Error: Term '{t1_name}' not found in environment.")
        return

    f_clone = clone_ast(env.formulae[target_name])
    from backend.SubstitutionManager import find_hidden_variable
    hidden_by = find_hidden_variable(f_clone, env, x)
    if hidden_by:
        print(f"Error: Variable '{x}' is hidden inside the unexpanded definition of '{hidden_by}'. You must expand '{hidden_by}' using the 'rw' command before executing this command.")
        return
        
    try:
        subst_valid = is_substitutable_free(x, t1_clone, f_clone, occurrence_idx)
        if not subst_valid:
            print("Warning: This substitution changes the semantic meaning (variable capture occurs).")
        substitute_free(f_clone, x, t1_clone, occurrence_idx)
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Created formula '{out_name}' = '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems and subst_valid:
            env.add_theorem(out_name)
            print(f"Registered formula '{out_name}' as a proven theorem.")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("sb", category="Transformations", help_text="Rename bound variable v to var t1")
def handle_sb(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "sb", cmd_args, 2, validate_new_name, supports_equiv=True)
    if not parsed: return
    fixed_args, occurrence_idx, target_name, out_name, equiv_name = parsed
    
    x = fixed_args[0]
    t1_name = fixed_args[1]

    t1_clone = resolve_term(env, t1_name)
    if t1_clone is None:
        print(f"Error: Term '{t1_name}' not found in environment.")
        return

    f_clone = clone_ast(env.formulae[target_name])
    from backend.SubstitutionManager import find_hidden_variable
    hidden_by = find_hidden_variable(f_clone, env, x)
    if hidden_by:
        print(f"Error: Variable '{x}' is hidden inside the unexpanded definition of '{hidden_by}'. You must expand '{hidden_by}' using the 'rw' command before executing this command.")
        return
        
    if not isinstance(t1_clone, Variable):
        print(f"Error: Bound substitution requires the replacement term '{t1_name}' to be a variable.")
        return
            
    try:
        subst_valid = is_substitutable_bound(x, t1_clone, f_clone, occurrence_idx)
        if not subst_valid:
            print("Warning: This substitution changes the semantic meaning.")
        substitute_bound(f_clone, x, t1_clone, occurrence_idx)
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Created formula '{out_name}' = '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems and subst_valid:
            env.add_theorem(out_name)
            print(f"Registered formula '{out_name}' as a proven theorem.")
            
        if equiv_name is not None:
            if subst_valid:
                from backend.AST import Connective
                equiv_node = Connective(name="⇔", arity=2, arguments=[clone_ast(env.formulae[target_name]), clone_ast(f_clone)])
                env.formulae[equiv_name] = equiv_node
                env.add_theorem(equiv_name)
                print(f"Registered equivalence theorem '{equiv_name}' = '{reconstruct_string(equiv_node)}'")
            else:
                print(f"Warning: Equivalence theorem '{equiv_name}' not generated because substitution is semantically invalid.")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("sa", category="Transformations", help_text="Substitute t1 for ALL occurrences of v")
def handle_sa(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "sa", cmd_args, 2, validate_new_name, supports_equiv=False)
    if not parsed: return
    fixed_args, occurrence_idx, target_name, out_name, _ = parsed
    
    x = fixed_args[0]
    t1_name = fixed_args[1]

    t1_clone = resolve_term(env, t1_name)
    if t1_clone is None:
        print(f"Error: Term '{t1_name}' not found in environment.")
        return

    f_clone = clone_ast(env.formulae[target_name])
    from backend.SubstitutionManager import find_hidden_variable
    hidden_by = find_hidden_variable(f_clone, env, x)
    if hidden_by:
        print(f"Error: Variable '{x}' is hidden inside the unexpanded definition of '{hidden_by}'. You must expand '{hidden_by}' using the 'rw' command before executing this command.")
        return
        
    try:
        subst_valid = is_substitutable_free(x, t1_clone, f_clone, occurrence_idx)
        occs_all = collect_all_occurrences(f_clone)
        has_bound = any(o["node"].name == x and not o["is_free"] for o in occs_all)
        if has_bound:
            if not isinstance(t1_clone, Variable):
                subst_valid = False
            else:
                subst_valid = subst_valid and is_substitutable_bound(x, t1_clone, f_clone, occurrence_idx)
        if not subst_valid:
            print("Warning: This substitution changes the semantic meaning.")
        substitute_all(f_clone, x, t1_clone, occurrence_idx)
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Created formula '{out_name}' = '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems and subst_valid:
            env.add_theorem(out_name)
            print(f"Registered formula '{out_name}' as a proven theorem.")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("sp", category="Transformations", help_text="Substitute prop-formula p1 for prop-var pv")
def handle_sp(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "sp", cmd_args, 2, validate_new_name, supports_equiv=False)
    if not parsed: return
    fixed_args, occurrence_idx, target_name, out_name, _ = parsed
    
    x = fixed_args[0]
    t1_name = fixed_args[1]

    if t1_name not in env.formulae:
        print(f"Error: Propositional formula '{t1_name}' not found in environment.")
        return

    f_clone = clone_ast(env.formulae[target_name])
    t1_clone = clone_ast(env.formulae[t1_name])
    
    try:
        substitute_proposition(f_clone, x, t1_clone, occurrence_idx)
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Created propositional formula '{out_name}' = '{reconstruct_string(f_clone)}'")
    except Exception as e:
        import traceback; traceback.print_exc()

@registry.register("crs", category="Environment Tools", help_text="Create a relation schema with given arity (e.g. crs Ψ 2)")
def handle_crs(env: Environment, args_str: str) -> None:
    from backend.AST import Relation, RelationType, DummyVariable
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) != 2:
        print("Error: Usage: crs <name> <arity>")
        return
    name, arity_str = cmd_args[0], cmd_args[1]
    if not arity_str.isdigit():
        print("Error: Arity must be an integer.")
        return
    arity = int(arity_str)
    if not validate_new_name(env, name, "formula"):
        return
    dummy = DummyVariable(name="dummy")
    args = [dummy for _ in range(arity)]
    env.add_formula(Relation(name=name, arity=arity, rel_type=RelationType.SCHEMA, arguments=args))
    print(f"Created relation schema '{name}' with arity {arity}")

@registry.register("cfs", category="Environment Tools", help_text="Create a function/term schema with given arity (e.g. cfs T 2)")
def handle_cfs(env: Environment, args_str: str) -> None:
    from backend.AST import Function, FunctionType, DummyVariable
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) != 2:
        print("Error: Usage: cfs <name> <arity>")
        return
    name, arity_str = cmd_args[0], cmd_args[1]
    if not arity_str.isdigit():
        print("Error: Arity must be an integer.")
        return
    arity = int(arity_str)
    if not validate_new_name(env, name, "term"):
        return
    dummy = DummyVariable(name="dummy")
    args = [dummy for _ in range(arity)]
    env.add_term(Function(name=name, arity=arity, func_type=FunctionType.SCHEMA, arguments=args))
    print(f"Created term schema '{name}' with arity {arity}")
