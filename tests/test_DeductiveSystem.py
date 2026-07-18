import pytest
from backend.AST import Variable, Relation, RelationType, Function, FunctionType
from backend.Environment import Environment
from backend.Parser import parse_fol_formula
from backend.DeductiveSystem import (
    axiom_E1, axiom_E2, axiom_E3, axiom_Q1, axiom_Q2,
    rule_QR1, rule_QR2, rule_PC1, rule_PC2
)

def get_test_env():
    env = Environment()
    for name in ["x", "y", "z", "w", "u", "v"]:
        env.add_variable(Variable(name))
    
    dummy = Variable("x")
    env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_axiom_E1():
    env = get_test_env()
    
    f1 = parse_fol_formula("x = x", env)
    assert axiom_E1(f1) is True
    
    f2 = parse_fol_formula("S x = S x", env)
    assert axiom_E1(f2) is True
    
    f3 = parse_fol_formula("x = y", env)
    assert axiom_E1(f3) is False

def test_axiom_E2():
    env = get_test_env()
    
    f1 = parse_fol_formula("x = y ⇒ S x = S y", env)
    assert axiom_E2(f1) is True
    
    f2 = parse_fol_formula("( x = y ∧ u = v ) ⇒ x + u = y + v", env)
    assert axiom_E2(f2) is True
    
    f3 = parse_fol_formula("( x = y ∧ u = v ) ⇒ x + u = v + y", env)
    assert axiom_E2(f3) is False

def test_axiom_E3():
    env = get_test_env()
    
    f1 = parse_fol_formula("( x = y ∧ z = z ) ⇒ ( x ∈ z ⇒ y ∈ z )", env)
    assert axiom_E3(f1) is True
    
    f2 = parse_fol_formula("x = y ∧ u = v ⇒ ( x = u ⇒ y = v )", env)
    assert axiom_E3(f2) is True

def test_axiom_Q1():
    env = get_test_env()
    
    f1 = parse_fol_formula("∀ x ( x = y ) ⇒ z = y", env)
    assert axiom_Q1(f1) is True
    
    f2 = parse_fol_formula("∀ x ( x = y ) ⇒ y = y", env)
    assert axiom_Q1(f2) is True
    
    f3 = parse_fol_formula("∀ x ( ∀ y ( x = y ) ) ⇒ ∀ y ( z = y )", env)
    assert axiom_Q1(f3) is True
    
    # Substituting y inside ∀y scope (causes bound variable capture)
    f4 = parse_fol_formula("∀ x ( ∀ y ( x = y ) ) ⇒ ∀ y ( y = y )", env)
    assert axiom_Q1(f4) is False

def test_axiom_Q2():
    env = get_test_env()
    
    f1 = parse_fol_formula("z = y ⇒ ∃ x ( x = y )", env)
    assert axiom_Q2(f1) is True
    
    f2 = parse_fol_formula("y = y ⇒ ∃ x ( x = y )", env)
    assert axiom_Q2(f2) is True
    
    f3 = parse_fol_formula("∀ y ( y = y ) ⇒ ∃ x ( ∀ y ( x = y ) )", env)
    assert axiom_Q2(f3) is False

def test_rule_QR1():
    env = get_test_env()
    
    premise = parse_fol_formula("z = y ⇒ x = y", env)
    conclusion = parse_fol_formula("z = y ⇒ ∀ x ( x = y )", env)
    assert rule_QR1([premise], conclusion) is True
    
    # x is free in antecedent "x = y" of conclusion, invalid
    premise2 = parse_fol_formula("x = y ⇒ x = y", env)
    conclusion2 = parse_fol_formula("x = y ⇒ ∀ x ( x = y )", env)
    assert rule_QR1([premise2], conclusion2) is False

def test_rule_QR2():
    env = get_test_env()
    
    premise = parse_fol_formula("x = y ⇒ z = y", env)
    conclusion = parse_fol_formula("∃ x ( x = y ) ⇒ z = y", env)
    assert rule_QR2([premise], conclusion) is True

def test_rule_PC1_and_PC2():
    env = get_test_env()
    
    # Modus Ponens: A ⇒ B, A |- B
    p1 = parse_fol_formula("x = y ⇒ u = v", env)
    p2 = parse_fol_formula("x = y", env)
    c = parse_fol_formula("u = v", env)
    
    assert rule_PC1([p1, p2], c) is True
    assert rule_PC2([p1, p2], c) is True
    
    # Modus Tollens
    p3 = parse_fol_formula("x = y ⇒ u = v", env)
    p4 = parse_fol_formula("¬ ( u = v )", env)
    c2 = parse_fol_formula("¬ ( x = y )", env)
    
    assert rule_PC1([p3, p4], c2) is True
    assert rule_PC2([p3, p4], c2) is True
    
    # Invalid consequence
    c3 = parse_fol_formula("u = v", env)
    assert rule_PC1([p3], c3) is False
    assert rule_PC2([p3], c3) is False

def test_environment_remove_theorem():
    env = get_test_env()
    f = parse_fol_formula("x = x", env)
    env.theorems["f1"] = f
    assert "f1" in env.theorems
    env.remove_theorem("f1")
    assert "f1" not in env.theorems

def test_main_repl_logic_simulation():
    from backend.Registry import AXIOMS, RULES
    env = get_test_env()
    
    f1 = parse_fol_formula("x = x", env)
    env.formulae["f1"] = f1
    
    assert AXIOMS["E1"](env.formulae["f1"]) is True
    env.theorems["f1"] = f1
    assert "f1" in env.theorems
    
    env.remove_theorem("f1")
    assert "f1" not in env.theorems
    assert "f1" in env.formulae

