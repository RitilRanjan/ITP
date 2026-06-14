import json
import pytest
from AST import Variable, DummyVariable, Function, FunctionType, Relation, RelationType
from Environment import Environment
from Frontend import parse_term, parse_fol_formula, reconstruct_string
from SubstitutionManager import clone_ast, substitute_term, substitute_free

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

def test_def_f_arity_1():
    env = get_test_env()
    
    # Term definition: S x
    t1 = parse_term("S x", env)
    env.terms["t1"] = t1
    
    # Simulate def_f 1 F x t1
    arity = 1
    f_name = "F"
    variables = ["x"]
    t1_name = "t1"
    
    assert t1_name in env.terms
    definition = clone_ast(env.terms[t1_name])
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
    
    assert reconstruct_string(definition) == "S_1"
    assert "F" in env.user_functions
    assert env.user_functions["F"][0] == 1
    assert reconstruct_string(env.user_functions["F"][1]) == "S_1"
    assert env.terms["F"].arity == 1

def test_def_f_arity_2_infix():
    env = get_test_env()
    
    # Term definition: x + y
    t2 = parse_term("x + y", env)
    env.terms["t2"] = t2
    
    # Simulate def_f 2 x G y t2
    arity = 2
    f_name = "G"
    variables = ["x", "y"]
    t2_name = "t2"
    
    definition = clone_ast(env.terms[t2_name])
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
    
    assert reconstruct_string(definition) == "_1+_2"
    assert env.user_functions["G"][0] == 2
    assert reconstruct_string(env.user_functions["G"][1]) == "_1+_2"

def test_def_r_arity_1():
    env = get_test_env()
    
    # Formula definition: x = x
    f1 = parse_fol_formula("x = x", env)
    env.formulae["f1"] = f1
    
    # Simulate def_r 1 R x f1
    arity = 1
    r_name = "R"
    variables = ["x"]
    f1_name = "f1"
    
    definition = clone_ast(env.formulae[f1_name])
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
    
    assert reconstruct_string(definition) == "_1=_1"
    assert env.user_relations["R"][0] == 1
    assert reconstruct_string(env.user_relations["R"][1]) == "_1=_1"

def test_def_r_arity_2_infix():
    env = get_test_env()
    
    # Formula definition: x ∈ y
    f2 = parse_fol_formula("x ∈ y", env)
    env.formulae["f2"] = f2
    
    # Simulate def_r 2 x Rel y f2
    arity = 2
    r_name = "Rel"
    variables = ["x", "y"]
    f2_name = "f2"
    
    definition = clone_ast(env.formulae[f2_name])
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
    
    assert reconstruct_string(definition) == "_1∈_2"
    assert env.user_relations["Rel"][0] == 2
    assert reconstruct_string(env.user_relations["Rel"][1]) == "_1∈_2"

def test_serialization():
    env = get_test_env()
    t1 = parse_term("S x", env)
    env.terms["t1"] = t1
    
    # Add custom function definition
    dummy_var = DummyVariable("_1")
    env.add_dummy_variable(dummy_var)
    df = substitute_term(clone_ast(t1), "x", dummy_var)
    env.user_functions["F"] = (1, df)
    
    json_str = env.to_json()
    data = json.loads(json_str)
    
    assert "user_functions" in data
    assert "user_relations" in data
    assert "F" in data["user_functions"]
