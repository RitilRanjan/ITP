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


