import pytest
from AST import Variable, Relation, RelationType
from Environment import Environment
from Frontend import parse_fol_formula, reconstruct_string
from PropAbstraction import abstract_to_propositional, abstract_to_propositional_with_mapping

def get_test_env():
    env = Environment()
    for var_name in ["x", "y", "z", "w", "u", "v"]:
        env.add_variable(Variable(var_name))
    dummy = Variable("x")
    env.add_formula(Relation("=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation("∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_simple_abstraction():
    env = get_test_env()
    
    # Simple relation
    f1 = parse_fol_formula("x = y", env)
    abs1 = abstract_to_propositional(f1)
    assert reconstruct_string(abs1) == "p0"
    
    # Identical relations
    f2 = parse_fol_formula("x = y ∧ x = y", env)
    abs2 = abstract_to_propositional(f2)
    assert reconstruct_string(abs2) == "p0 ∧ p0"
    
    # Mismatched relations
    f3 = parse_fol_formula("x = y ∧ z = w", env)
    abs3 = abstract_to_propositional(f3)
    assert reconstruct_string(abs3) == "p0 ∧ p1"

def test_formatting_preservation():
    env = get_test_env()
    
    # Brackets and whitespace around matched formulas
    f1 = parse_fol_formula("( x = y ) ∧ x = y", env)
    abs1 = abstract_to_propositional(f1)
    assert reconstruct_string(abs1) == "( p0 ) ∧ p0"

def test_quantifier_abstraction():
    env = get_test_env()
    
    # Outermost quantifiers are abstracted
    f1 = parse_fol_formula("∀ x ( x = y )", env)
    abs1 = abstract_to_propositional(f1)
    assert reconstruct_string(abs1) == "p0"
    
    # Connective of quantifiers
    f2 = parse_fol_formula("∀ x ( x = y ) ∧ ∃ z ( z = x )", env)
    abs2 = abstract_to_propositional(f2)
    assert reconstruct_string(abs2) == "p0 ∧ p1"
    
    # Quantifier containing connectives is treated as a single atomic unit
    f3 = parse_fol_formula("∀ x ( x = y ∧ z = w )", env)
    abs3 = abstract_to_propositional(f3)
    assert reconstruct_string(abs3) == "p0"
    
    # Identical quantifier bodies (up to formatting) should map to the same variable
    # Note: Variable names must match exactly since matching does not perform alpha-renaming, just ignores formatting.
    f4 = parse_fol_formula("∀ x ( x = y ) ∧ ( ∀ x ( x = y ) )", env)
    abs4 = abstract_to_propositional(f4)
    assert reconstruct_string(abs4) == "p0 ∧ ( p0 )"

def test_complex_connectives():
    env = get_test_env()
    
    # Nested logical connectives
    f1 = parse_fol_formula("¬ ( x = y ∧ z ∈ w ) ⇒ ( u = v ∨ x = y )", env)
    abs1 = abstract_to_propositional(f1)
    assert reconstruct_string(abs1) == "¬ ( p0 ∧ p1 ) ⇒ ( p2 ∨ p0 )"

def test_abstraction_with_mapping():
    env = get_test_env()
    
    f1 = parse_fol_formula("x = y ∧ z ∈ w ∧ x = y", env)
    abs_f, mappings = abstract_to_propositional_with_mapping(f1)
    
    assert reconstruct_string(abs_f) == "p0 ∧ p1 ∧ p0"
    assert len(mappings) == 2
    
    # Mappings contain the clean 1st order formulas
    assert reconstruct_string(mappings[0][0]) == "x = y"
    assert mappings[0][1].name == "p0"
    
    assert reconstruct_string(mappings[1][0]) == "z ∈ w"
    assert mappings[1][1].name == "p1"
