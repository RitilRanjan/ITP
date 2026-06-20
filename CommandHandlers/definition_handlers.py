from typing import Callable, Any

from AST import DummyVariable, Function, FunctionType, Relation, RelationType, Quantifier
from Environment import Environment
from Frontend import lex, reconstruct_string, parse_term, parse_fol_formula
from SubstitutionManager import clone_ast, substitute_term, substitute_free, get_free
from CommandHandlers.CommandRegistry import registry
from CommandHandlers.utils import validate_new_name

@registry.register("def_f", category="Definitions", help_text="Define a new function")
def handle_def_f(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 3:
        print("Error: Usage: def_f n F1 v1 v2 ... vn t1 (infix: def_f 2 v1 F1 v2 t1)")
        return
    try:
        arity = int(cmd_args[0])
    except ValueError:
        print("Error: Arity must be an integer.")
        return

    if arity == 2:
        if len(cmd_args) < 5:
            print("Error: Usage for arity 2: def_f 2 v1 F1 v2 t1")
            return
        v1_name, f_name, v2_name = cmd_args[1], cmd_args[2], cmd_args[3]
        variables = [v1_name, v2_name]
        tail_tokens = cmd_args[4:]
    else:
        if len(cmd_args) < arity + 3:
            print(f"Error: Usage for arity {arity}: def_f {arity} F1 v1 v2 ... v{arity} t1")
            return
        f_name = cmd_args[1]
        variables = cmd_args[2 : arity + 2]
        tail_tokens = cmd_args[arity + 2 :]

    if not validate_new_name(env, f_name, "term"):
        return

    valid_vars = True
    for v in variables:
        if v not in env.variables:
            print(f"Error: Variable '{v}' not found in environment.")
            valid_vars = False
            break
    if not valid_vars:
        return

    if len(tail_tokens) == 1 and tail_tokens[0] in env.terms:
        definition = clone_ast(env.terms[tail_tokens[0]])
    else:
        t1_expr = " ".join(tail_tokens)
        try:
            definition = parse_term(t1_expr, env)
        except Exception as e:
            print(f"Error parsing term: {e}")
            return

    for i, var_name in enumerate(variables):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_term(definition, var_name, dummy_var)

    env.user_functions[f_name] = (arity, definition)
    decl_node = Function(
        name=f_name,
        arity=arity,
        func_type=FunctionType.USER_DEFINED,
        arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
    )
    env.terms[f_name] = decl_node
    print(f"Defined function '{f_name}' of arity {arity} = '{reconstruct_string(definition)}'")

@registry.register("def_r", category="Definitions", help_text="Define a new relation")
def handle_def_r(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 3:
        print("Error: Usage: def_r n R1 v1 v2 ... vn f1 (infix: def_r 2 v1 R1 v2 f1)")
        return
    try:
        arity = int(cmd_args[0])
    except ValueError:
        print("Error: Arity must be an integer.")
        return

    if arity == 2:
        if len(cmd_args) < 5:
            print("Error: Usage for arity 2: def_r 2 v1 R1 v2 f1")
            return
        v1_name, r_name, v2_name = cmd_args[1], cmd_args[2], cmd_args[3]
        variables = [v1_name, v2_name]
        tail_tokens = cmd_args[4:]
    else:
        if len(cmd_args) < arity + 3:
            print(f"Error: Usage for arity {arity}: def_r {arity} R1 v1 v2 ... v{arity} f1")
            return
        r_name = cmd_args[1]
        variables = cmd_args[2 : arity + 2]
        tail_tokens = cmd_args[arity + 2 :]

    if not validate_new_name(env, r_name, "formula"):
        return

    valid_vars = True
    for v in variables:
        if v not in env.variables:
            print(f"Error: Variable '{v}' not found in environment.")
            valid_vars = False
            break
    if not valid_vars:
        return

    if len(tail_tokens) == 1 and tail_tokens[0] in env.formulae:
        definition = clone_ast(env.formulae[tail_tokens[0]])
    else:
        f1_expr = " ".join(tail_tokens)
        try:
            definition = parse_fol_formula(f1_expr, env)
        except Exception as e:
            print(f"Error parsing formula: {e}")
            return

    for i, var_name in enumerate(variables):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_free(definition, var_name, dummy_var)

    env.user_relations[r_name] = (arity, definition)
    decl_node = Relation(
        name=r_name,
        arity=arity,
        rel_type=RelationType.USER_DEFINED,
        arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
    )
    env.formulae[r_name] = decl_node
    print(f"Defined relation '{r_name}' of arity {arity} = '{reconstruct_string(definition)}'")

@registry.register("iota", category="Definitions", help_text="Define an iota function from ∃! theorem")
def handle_iota(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 2:
        print("Error: Usage: iota F1 f1")
        return
    f_name = cmd_args[0]
    tail_tokens = cmd_args[1:]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.theorems:
        theorem_node = env.theorems[tail_tokens[0]]
    else:
        f1_expr = " ".join(tail_tokens)
        try:
            target_formula = parse_fol_formula(f1_expr, env)
        except Exception as e:
            print(f"Error parsing formula: {e}")
            return
        
        theorem_node = None
        for th_name in env.theorems:
            th = env.formulae[th_name]
            if target_formula.is_structurally_equal(th):
                theorem_node = th
                break
        if theorem_node is None:
            print(f"Error: No proven theorem matches '{f1_expr}'.")
            return
    
    if not (isinstance(theorem_node, Quantifier) and theorem_node.name == "∃!"):
        if len(tail_tokens) == 1 and tail_tokens[0] in env.theorems:
            print(f"Error: Theorem '{tail_tokens[0]}' is not of the form ∃! x Ψ(x).")
        else:
            print(f"Error: Matched theorem is not of the form ∃! x Ψ(x).")
        return
        
    bound_var_name = theorem_node.variable.name
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    if len(free_vars) == 0:
        ordered_vars = []
    elif len(free_vars) == 1:
        ordered_vars = list(free_vars)
    else:
        print(f"Multiple free variables found: {', '.join(sorted(free_vars))}")
        while True:
            try:
                from CommandHandlers.utils import get_user_input
                user_seq = get_user_input("Enter sequence of variables separated by spaces: ", command_queue, inputs_collected)
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                ordered_vars = None
                break
            seq_vars = user_seq.split()
            if set(seq_vars) != free_vars or len(seq_vars) != len(free_vars):
                print(f"Error: Must enter exactly the variables {', '.join(sorted(free_vars))} without duplicates.")
                continue
            ordered_vars = seq_vars
            break
        if ordered_vars is None:
            return
    
    if not validate_new_name(env, f_name, "term"):
        return
        
    arity = len(ordered_vars)
    definition = clone_ast(theorem_node.formula)
    for i, var_name in enumerate(ordered_vars):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_free(definition, var_name, dummy_var)
        
    env.user_functions[f_name] = (arity, definition)
    decl_node = Function(
        name=f_name,
        arity=arity,
        func_type=FunctionType.IOTA_DEFINED,
        arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
    )
    env.terms[f_name] = decl_node
    print(f"Defined iota function '{f_name}' of arity {arity} = '{reconstruct_string(definition)}'")

@registry.register("epsilon", category="Definitions", help_text="Define an epsilon function from ∃ theorem")
def handle_epsilon(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 2:
        print("Error: Usage: epsilon F1 f1")
        return
    f_name = cmd_args[0]
    tail_tokens = cmd_args[1:]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.theorems:
        theorem_node = env.theorems[tail_tokens[0]]
    else:
        f1_expr = " ".join(tail_tokens)
        try:
            target_formula = parse_fol_formula(f1_expr, env)
        except Exception as e:
            print(f"Error parsing formula: {e}")
            return
        
        theorem_node = None
        for th_name in env.theorems:
            th = env.formulae[th_name]
            if target_formula.is_structurally_equal(th):
                theorem_node = th
                break
        if theorem_node is None:
            print(f"Error: No proven theorem matches '{f1_expr}'.")
            return
    
    if not (isinstance(theorem_node, Quantifier) and theorem_node.name == "∃"):
        if len(tail_tokens) == 1 and tail_tokens[0] in env.theorems:
            print(f"Error: Theorem '{tail_tokens[0]}' is not of the form ∃ x Ψ(x).")
        else:
            print(f"Error: Matched theorem is not of the form ∃ x Ψ(x).")
        return
        
    bound_var_name = theorem_node.variable.name
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    if len(free_vars) == 0:
        ordered_vars = []
    elif len(free_vars) == 1:
        ordered_vars = list(free_vars)
    else:
        print(f"Multiple free variables found: {', '.join(sorted(free_vars))}")
        while True:
            try:
                from CommandHandlers.utils import get_user_input
                user_seq = get_user_input("Enter sequence of variables separated by spaces: ", command_queue, inputs_collected)
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                ordered_vars = None
                break
            seq_vars = user_seq.split()
            if set(seq_vars) != free_vars or len(seq_vars) != len(free_vars):
                print(f"Error: Must enter exactly the variables {', '.join(sorted(free_vars))} without duplicates.")
                continue
            ordered_vars = seq_vars
            break
        if ordered_vars is None:
            return
    
    if not validate_new_name(env, f_name, "term"):
        return
        
    arity = len(ordered_vars)
    definition = clone_ast(theorem_node.formula)
    for i, var_name in enumerate(ordered_vars):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_free(definition, var_name, dummy_var)
        
    env.user_functions[f_name] = (arity, definition)
    decl_node = Function(
        name=f_name,
        arity=arity,
        func_type=FunctionType.EPSILON_DEFINED,
        arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
    )
    env.terms[f_name] = decl_node
    print(f"Defined epsilon function '{f_name}' of arity {arity} = '{reconstruct_string(definition)}'")
