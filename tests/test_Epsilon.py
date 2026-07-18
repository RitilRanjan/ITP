import pytest
from unittest.mock import patch
from backend.AST import Variable, DummyVariable, Function, FunctionType, Relation, RelationType, Quantifier
from backend.Environment import Environment
from backend.Parser import parse_fol_formula, reconstruct_string, parse_term
from backend.SubstitutionManager import clone_ast, substitute_free
from main import validate_new_name
from backend.DefinitionExpander import expand_epsilon_in_formula

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

def test_epsilon_arity_0():
    env = get_test_env()
    
    # ∃ x ( x = x )
    f = parse_fol_formula("∃ x ( x = x )", env)
    env.theorems["th0"] = f
    
    theorem_node = env.theorems["th0"]
    assert isinstance(theorem_node, Quantifier) and theorem_node.name == "∃"
    
    bound_var_name = theorem_node.variable.name
    from backend.SubstitutionManager import get_free
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    assert len(free_vars) == 0
    ordered_vars = []
    
    f_name = "E0"
    assert validate_new_name(env, f_name, "term") is True
    
    arity = len(ordered_vars)
    definition = clone_ast(theorem_node.formula)
    
    env.user_functions[f_name] = (arity, definition)
    decl_node = Function(
        name=f_name,
        arity=arity,
        func_type=FunctionType.EPSILON_DEFINED,
        arguments=[]
    )
    env.terms[f_name] = decl_node
    
    assert "E0" in env.user_functions
    assert env.user_functions["E0"][0] == 0
    assert reconstruct_string(env.user_functions["E0"][1]) == " ( x = x )"
    assert env.terms["E0"].func_type == FunctionType.EPSILON_DEFINED
    assert env.terms["E0"].arity == 0

def test_epsilon_arity_1():
    env = get_test_env()
    
    # ∃ x ( x = y )
    f = parse_fol_formula("∃ x ( x = y )", env)
    env.theorems["th1"] = f
    
    theorem_node = env.theorems["th1"]
    assert isinstance(theorem_node, Quantifier) and theorem_node.name == "∃"
    
    bound_var_name = theorem_node.variable.name
    from backend.SubstitutionManager import get_free
    free_vars = get_free(theorem_node.formula)
    free_vars.discard(bound_var_name)
    
    assert len(free_vars) == 1
    ordered_vars = list(free_vars)
    assert ordered_vars == ["y"]
    
    f_name = "E1"
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
        func_type=FunctionType.EPSILON_DEFINED,
        arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
    )
    env.terms[f_name] = decl_node
    
    assert "E1" in env.user_functions
    assert env.user_functions["E1"][0] == 1
    assert reconstruct_string(env.user_functions["E1"][1]) == " ( x =_1)"
    assert env.terms["E1"].func_type == FunctionType.EPSILON_DEFINED
    assert env.terms["E1"].arity == 1

def test_expand_epsilon_in_formula():
    env = get_test_env()
    
    # Define an epsilon function E1 of arity 1 from ∃ x ( x = y )
    # definition is (x = _1)
    # E1(y) is a term
    # Let's say we have formula: E1(y) = z
    
    env.add_variable(Variable("u"))
    
    # Manually register E1 as epsilon function in env
    dummy_var = DummyVariable("_1")
    env.add_dummy_variable(dummy_var)
    definition = parse_fol_formula("x = _1", env)
    
    env.user_functions["E1"] = (1, definition)
    decl_node = Function(
        name="E1",
        arity=1,
        func_type=FunctionType.EPSILON_DEFINED,
        arguments=[dummy_var]
    )
    env.terms["E1"] = decl_node
    
    formula = parse_fol_formula("E1(y) = z", env)
    
    expanded = expand_epsilon_in_formula(env, formula, "E1", 1, "u")
    
    # Expected: ∃u( u=(y) ∧u= z )
    assert reconstruct_string(expanded) == "∃u( u=(y) ∧u= z )"
