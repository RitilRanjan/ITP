import pytest
from backend.Environment import Environment
from backend.AST import Variable, DummyVariable, Relation, RelationType, Quantifier, Connective, PropositionalVariable
from backend.Parser import parse_fol_formula, parse_prop_formula
from backend.AutoProver import auto_prove, collect_leaf_sequents, make_sequent_formula, decode_propositional_to_fol
from main import get_default_env

def test_auto_prove_axioms():
    env = get_default_env()
    
    # 1. Logical Axiom E1: x = x
    f1 = parse_fol_formula("x = x", env)
    env.formulae["f1"] = f1
    assert auto_prove("f1", env)
    assert "f1" in env.theorems
    
    # 2. ZFC Extension Axiom
    # ( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ x = y
    env.add_variable(Variable("z"))
    f2 = parse_fol_formula("( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ x = y", env)
    env.formulae["f2"] = f2
    assert auto_prove("f2", env)
    assert "f2" in env.theorems

def test_auto_prove_tautologies():
    env = get_default_env()
    
    # Excluded Middle: p ∨ ¬ p (as prop formula)
    env.add_propositional_variable(PropositionalVariable("p"))
    f1 = parse_prop_formula("p ∨ ¬ p", env)
    env.formulae["f1"] = f1
    assert auto_prove("f1", env)
    
    # Peirce's Law: ((p ⇒ q) ⇒ p) ⇒ p
    f2 = parse_prop_formula("( ( p ⇒ q ) ⇒ p ) ⇒ p", env)
    env.formulae["f2"] = f2
    assert auto_prove("f2", env)

def test_auto_prove_qr1_recursive():
    env = get_default_env()
    env.add_variable(Variable("z"))
    env.add_variable(Variable("w"))
    
    # Conclusion: (z = z) ⇒ ∀ x (z = z)
    # Premise: (z = z) ⇒ (z = z), which is a propositional tautology (PC2)
    f1 = parse_fol_formula("( z = z ) ⇒ ∀ x ( z = z )", env)
    env.formulae["f1"] = f1
    
    # Proving f1 should recursively trigger proving the premise (z = z) => (z = z)
    assert auto_prove("f1", env)
    assert "f1" in env.theorems

def test_auto_prove_qr2_recursive():
    env = get_default_env()
    env.add_variable(Variable("z"))
    env.add_variable(Variable("w"))
    
    # Conclusion: (∃ x (z = z)) ⇒ (z = z)
    # Premise: (z = z) ⇒ (z = z)
    f1 = parse_fol_formula("( ∃ x ( z = z ) ) ⇒ ( z = z )", env)
    env.formulae["f1"] = f1
    
    assert auto_prove("f1", env)
    assert "f1" in env.theorems

def test_auto_prove_pc2_decomposition():
    env = get_default_env()
    env.add_variable(Variable("z"))
    env.add_variable(Variable("w"))
    
    # Formula: (z = z ∧ w = w) ⇒ z = z
    # Decomposes via PC2 into leaf sequents. Since the leaf sequents are proved,
    # the whole formula is proved via PC2.
    f1 = parse_fol_formula("( z = z ∧ w = w ) ⇒ z = z", env)
    env.formulae["f1"] = f1
    
    assert auto_prove("f1", env)
    assert "f1" in env.theorems

def test_recursion_safety():
    env = get_default_env()
    env.add_variable(Variable("z"))
    env.add_variable(Variable("w"))
    
    # Non-tautological atomic formula: z = w
    # Cannot be proved, and should exit gracefully with False instead of looping.
    f1 = parse_fol_formula("z = w", env)
    env.formulae["f1"] = f1
    
    assert not auto_prove("f1", env)
