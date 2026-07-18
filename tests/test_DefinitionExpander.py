import pytest
from backend.AST import Variable, DummyVariable, Function, FunctionType, Relation, RelationType, Quantifier, Connective
from backend.Environment import Environment
from backend.Parser import parse_term, parse_fol_formula, reconstruct_string
from backend.SubstitutionManager import clone_ast, substitute_term
from backend.DefinitionExpander import (
    expand_user_defined_function_in_term,
    expand_user_defined_function_in_formula,
    expand_user_defined_relation_in_formula,
    expand_existential_in_formula,
    expand_unique_existential_in_formula,
    expand_iota_in_formula,
    substitute_dummy_in_formula
)

def get_test_env():
    env = Environment()
    env.add_variable(Variable("x"))
    env.add_variable(Variable("y"))
    env.add_variable(Variable("z"))
    env.add_variable(Variable("w"))
    
    dummy = Variable("x")
    env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_expand_user_defined_function():
    env = get_test_env()
    # Define F 1 = S _1
    definition = parse_term("S x", env)
    dummy_var = DummyVariable("_1")
    env.add_dummy_variable(dummy_var)
    definition = substitute_term(definition, "x", dummy_var)
    env.user_functions["F"] = (1, definition)
    
    decl_node = Function(
        name="F", arity=1, func_type=FunctionType.USER_DEFINED,
        arguments=[DummyVariable("_1")]
    )
    env.terms["F"] = decl_node
    
    # 1. Expand in term
    t1 = parse_term("F(x)", env)
    expanded_t = expand_user_defined_function_in_term(env, t1, "F", 1)
    assert reconstruct_string(expanded_t) == "S(x)"
    
    # 2. Expand in formula
    f1 = parse_fol_formula("F(y) = z", env)
    expanded_f = expand_user_defined_function_in_formula(env, f1, "F", 1)
    assert reconstruct_string(expanded_f) == "S(y) = z"

def test_expand_user_defined_relation():
    env = get_test_env()
    # Define R 2 = _1 = _2
    f_def = parse_fol_formula("x = y", env)
    d1 = DummyVariable("_1")
    d2 = DummyVariable("_2")
    env.add_dummy_variable(d1)
    env.add_dummy_variable(d2)
    from backend.SubstitutionManager import substitute_free
    f_def = substitute_free(f_def, "x", d1)
    f_def = substitute_free(f_def, "y", d2)
    env.user_relations["R"] = (2, f_def)
    
    decl_node = Relation(
        name="R", arity=2, rel_type=RelationType.USER_DEFINED,
        arguments=[DummyVariable("_1"), DummyVariable("_2")]
    )
    env.formulae["R"] = decl_node
    
    f1 = parse_fol_formula("x R y", env)
    expanded = expand_user_defined_relation_in_formula(env, f1, "R", 1)
    assert reconstruct_string(expanded) == "x = y"

def test_expand_existential():
    env = get_test_env()
    f1 = parse_fol_formula("∃ x ( x = y )", env)
    expanded = expand_existential_in_formula(f1, 1)
    assert reconstruct_string(expanded) == "¬∀ x¬ ( x = y )"

def test_expand_unique_existential():
    env = get_test_env()
    f1 = parse_fol_formula("∃! x ( x = y )", env)
    expanded = expand_unique_existential_in_formula(f1, 1, "z")
    assert reconstruct_string(expanded) == "∃ x∀z(  ( z= y )⇔z= x )"
    
    # Check checks on y
    with pytest.raises(ValueError):
        # y must not be the same as bound variable x
        expand_unique_existential_in_formula(f1, 1, "x")
        
    with pytest.raises(ValueError):
        # y must not be free in the body (y is free in x=y)
        expand_unique_existential_in_formula(f1, 1, "y")

def test_expand_iota_function():
    env = get_test_env()
    
    # Theorem: ∃! x ( x = y )
    th = parse_fol_formula("∃! x ( x = y )", env)
    env.theorems["th1"] = th
    
    # Define iota function F1 from th1 (bound var is x, free is y, arity 1)
    definition = clone_ast(th.formula) # (x = y)
    d1 = DummyVariable("_1")
    env.add_dummy_variable(d1)
    from backend.SubstitutionManager import substitute_free
    definition = substitute_free(definition, "y", d1)
    
    env.user_functions["F1"] = (1, definition)
    env.terms["F1"] = Function(
        name="F1", arity=1, func_type=FunctionType.IOTA_DEFINED,
        arguments=[DummyVariable("_1")]
    )
    
    f1 = parse_fol_formula("F1(z) = w", env)
    expanded = expand_iota_in_formula(env, f1, "F1", 1, "u", "v")
    assert reconstruct_string(expanded) == "∃u( ∀v(  ( v=(z) )⇔u=v ) )∧u= w"
    
    # Semantic violations
    # 1. u and v must be distinct
    with pytest.raises(ValueError):
        expand_iota_in_formula(env, f1, "F1", 1, "u", "u")
        
    # 2. u must not be free in Φ (which contains w)
    with pytest.raises(ValueError):
        expand_iota_in_formula(env, f1, "F1", 1, "w", "v")
        
    # 3. v must not be free in Ψ_instantiated (z is free)
    with pytest.raises(ValueError):
        expand_iota_in_formula(env, f1, "F1", 1, "u", "z")
        
    # 4. u/v captured by enclosing quantifiers in Φ
    env.add_variable(Variable("u"))
    env.add_variable(Variable("v"))
    f2 = parse_fol_formula("∀ u ( F1(z) = u )", env)
    with pytest.raises(ValueError):
        expand_iota_in_formula(env, f2, "F1", 1, "u", "v")
