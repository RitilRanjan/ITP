import pytest
from unittest.mock import patch
from AST import Variable, DummyVariable, Function, FunctionType, Relation, RelationType, Quantifier
from Environment import Environment
from Frontend import parse_fol_formula, reconstruct_string, parse_term
from SubstitutionManager import clone_ast, substitute_free
from main import validate_new_name

def get_test_env():
    env = Environment()
    env.add_variable(Variable("x"))
    env.add_variable(Variable("y"))
    env.add_variable(Variable("z"))
    
    dummy = Variable("x")
    env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_validate_new_name_prefix():
    env = get_test_env()
    
    # 1. Names starting with '_' are reserved for dummy variables only
    assert validate_new_name(env, "_dummy", "dummy_variable") is True
    assert validate_new_name(env, "_dummy", "variable") is False
    assert validate_new_name(env, "_dummy", "term") is False
    
    # 2. Names starting with '?' are reserved for meta variables only
    assert validate_new_name(env, "?meta", "meta_variable") is True
    assert validate_new_name(env, "?meta", "formula") is False
    assert validate_new_name(env, "?meta", "variable") is False

def test_validate_new_name_clashes():
    env = get_test_env()
    
    # Variable 'x' exists. Adding variable 'x' should succeed (overwriting allowed).
    assert validate_new_name(env, "x", "variable") is True
    
    # Adding term 'x' should fail (clash).
    assert validate_new_name(env, "x", "term") is False
    
    # Adding formula 'x' should fail (clash).
    assert validate_new_name(env, "x", "formula") is False
    
    # Add a term 't1'
    env.terms["t1"] = parse_term("S x", env)
    
    # Adding term 't1' should succeed (overwriting).
    assert validate_new_name(env, "t1", "term") is True
    # Adding formula 't1' should fail.
    assert validate_new_name(env, "t1", "formula") is False

def test_iota_arity_0():
    env = get_test_env()
    
    # ∃! x ( x = x )
    f = parse_fol_formula("∃! x ( x = x )", env)
    env.theorems["th0"] = f
    
    # Simulate iota F0 th0
    theorem_node = env.theorems["th0"]
    assert isinstance(theorem_node, Quantifier) and theorem_node.name == "∃!"
    
    bound_var_name = theorem_node.variable.name
    from SubstitutionManager import get_free
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    assert len(free_vars) == 0
    ordered_vars = []
    
    f_name = "F0"
    assert validate_new_name(env, f_name, "term") is True
    
    arity = len(ordered_vars)
    definition = clone_ast(theorem_node.formula)
    
    env.user_functions[f_name] = (arity, definition)
    decl_node = Function(
        name=f_name,
        arity=arity,
        func_type=FunctionType.IOTA_DEFINED,
        arguments=[]
    )
    env.terms[f_name] = decl_node
    
    assert "F0" in env.user_functions
    assert env.user_functions["F0"][0] == 0
    assert reconstruct_string(env.user_functions["F0"][1]) == " ( x = x )"
    assert env.terms["F0"].func_type == FunctionType.IOTA_DEFINED
    assert env.terms["F0"].arity == 0

def test_iota_arity_1():
    env = get_test_env()
    
    # ∃! x ( x = y )
    f = parse_fol_formula("∃! x ( x = y )", env)
    env.theorems["th1"] = f
    
    # Simulate iota F1 th1
    theorem_node = env.theorems["th1"]
    assert isinstance(theorem_node, Quantifier) and theorem_node.name == "∃!"
    
    bound_var_name = theorem_node.variable.name
    from SubstitutionManager import get_free
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    assert len(free_vars) == 1
    ordered_vars = list(free_vars)
    assert ordered_vars == ["y"]
    
    f_name = "F1"
    assert validate_new_name(env, f_name, "term") is True
    
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
    
    assert "F1" in env.user_functions
    assert env.user_functions["F1"][0] == 1
    assert reconstruct_string(env.user_functions["F1"][1]) == " ( x =_1)"
    assert env.terms["F1"].func_type == FunctionType.IOTA_DEFINED
    assert env.terms["F1"].arity == 1

def test_iota_arity_2_prompt():
    env = get_test_env()
    
    # ∃! x ( x + y = z )
    f = parse_fol_formula("∃! x ( x + y = z )", env)
    env.theorems["th2"] = f
    
    theorem_node = env.theorems["th2"]
    bound_var_name = theorem_node.variable.name
    from SubstitutionManager import get_free
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    assert free_vars == {"y", "z"}
    
    # Mock input for sequence prompt: "y z"
    with patch('builtins.input', return_value="y z"):
        user_seq = input("Mock prompt").strip()
        seq_vars = user_seq.split()
        assert set(seq_vars) == free_vars
        ordered_vars = seq_vars
        
    f_name = "F2"
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
    
    assert env.user_functions["F2"][0] == 2
    assert reconstruct_string(env.user_functions["F2"][1]) == " ( x +_1=_2)"
    
    # Let's test with alternative sequence prompt: "z y"
    with patch('builtins.input', return_value="z y"):
        user_seq = input("Mock prompt").strip()
        seq_vars = user_seq.split()
        ordered_vars_alt = seq_vars
        
    f_name_alt = "F2_alt"
    definition_alt = clone_ast(theorem_node.formula)
    for i, var_name in enumerate(ordered_vars_alt):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition_alt = substitute_free(definition_alt, var_name, dummy_var)
        
    env.user_functions[f_name_alt] = (arity, definition_alt)
    
    assert env.user_functions["F2_alt"][0] == 2
    assert reconstruct_string(env.user_functions["F2_alt"][1]) == " ( x +_2=_1)"
