import pytest
from AST import Variable, PropositionalVariable, Function, FunctionType, Relation, RelationType, Connective, Quantifier
from Environment import Environment
from Frontend import parse_fol_formula
from ZFC_Rules import (
    axiom_extension, axiom_regularity, axiom_union, axiom_pairing,
    axiom_power_set, axiom_infinity, axiom_choice, axiom_specification, axiom_replacement
)

def get_test_env():
    env = Environment()
    for var_name in ["x", "y", "z", "w", "u", "v", "A", "B", "C", "D", "X", "E", "Y", "a", "b", "c", "d"]:
        env.add_variable(Variable(var_name))
    dummy = Variable("x")
    env.add_formula(Relation("=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation("∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_axiom_extension():
    env = get_test_env()
    
    # Standard open form
    f1 = parse_fol_formula("( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ x = y", env)
    assert axiom_extension(f1) is True
    
    # Renamed open form
    f2 = parse_fol_formula("( ∀ w ( w ∈ a ⇔ w ∈ b ) ) ⇒ a = b", env)
    assert axiom_extension(f2) is True
    
    # Fully closed form
    f3 = parse_fol_formula("∀ a ∀ b ( ( ∀ w ( w ∈ a ⇔ w ∈ b ) ) ⇒ a = b )", env)
    assert axiom_extension(f3) is True
    
    # Incorrect structure
    f4 = parse_fol_formula("( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ y = x", env)  # should match because x=y is isomorphic to y=x (renaming)
    assert axiom_extension(f4) is True
    
    f5 = parse_fol_formula("( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ x = z", env)  # invalid
    assert axiom_extension(f5) is False

def test_axiom_pairing():
    env = get_test_env()
    
    f1 = parse_fol_formula("∃ z ∀ w ( w ∈ z ⇔ w = x ∨ w = y )", env)
    assert axiom_pairing(f1) is True
    
    f2 = parse_fol_formula("∀ a ∀ b ∃ c ∀ d ( d ∈ c ⇔ d = b ∨ d = a )", env)
    assert axiom_pairing(f2) is True

def test_axiom_union_and_power():
    env = get_test_env()
    
    f1 = parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )", env)
    assert axiom_union(f1) is True
    
    f2 = parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ ∀ w ( w ∈ z ⇒ w ∈ x ) )", env)
    assert axiom_power_set(f2) is True

def test_axiom_regularity():
    env = get_test_env()
    
    f1 = parse_fol_formula("∃ y ( y ∈ x ) ⇒ ∃ y ( y ∈ x ∧ ¬ ∃ z ( z ∈ y ∧ z ∈ x ) )", env)
    assert axiom_regularity(f1) is True

def test_axiom_infinity_and_choice():
    env = get_test_env()
    
    f1 = parse_fol_formula("∃ X ( ∃ E ( E ∈ X ∧ ∀ z ( ¬ ( z ∈ E ) ) ) ∧ ∀ y ( y ∈ X ⇒ ∃ Y ( Y ∈ X ∧ ∀ z ( z ∈ Y ⇔ z ∈ y ∨ z = y ) ) ) )", env)
    assert axiom_infinity(f1) is True
    
    f2 = parse_fol_formula(
        "∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ) ) ∧ ∀ y ∀ z ( y ∈ X ∧ z ∈ X ∧ ¬ ( y = z ) ⇒ ¬ ∃ w ( w ∈ y ∧ w ∈ z ) ) ⇒ ∃ C ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ∧ z ∈ C ∧ ∀ w ( w ∈ y ∧ w ∈ C ⇒ w = z ) ) )",
        env
    )
    assert axiom_choice(f2) is True

def test_axiom_specification():
    env = get_test_env()
    
    # phi is z = w (w is a free variable in phi, y is not free)
    f1 = parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ z ∈ x ∧ z = w )", env)
    assert axiom_specification(f1) is True
    
    # phi contains y free, which is invalid
    f2 = parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ z ∈ x ∧ z = y )", env)
    assert axiom_specification(f2) is False

def test_axiom_replacement():
    env = get_test_env()
    
    # phi is u = v
    # phi_uw is u = w
    # uniqueness: ∀u ∀v ∀w (u = v ∧ u = w ⇒ v = w)
    # consequent: ∃B ∀v (v ∈ B ⇔ ∃u (u ∈ A ∧ u = v))
    f1 = parse_fol_formula(
        "∀ u ∀ v ∀ w ( u = v ∧ u = w ⇒ v = w ) ⇒ ∃ B ∀ v ( v ∈ B ⇔ ∃ u ( u ∈ A ∧ u = v ) )",
        env
    )
    assert axiom_replacement(f1) is True
    
    # Mismatched relation in antecedent
    f2 = parse_fol_formula(
        "∀ u ∀ v ∀ w ( u = v ∧ u = z ⇒ v = w ) ⇒ ∃ B ∀ v ( v ∈ B ⇔ ∃ u ( u ∈ A ∧ u = v ) )",
        env
    )
    assert axiom_replacement(f2) is False
