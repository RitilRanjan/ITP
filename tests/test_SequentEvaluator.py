import pytest
from backend.AST import PropositionalVariable, Connective
from backend.Environment import Environment
from backend.Parser import parse_prop_formula
from backend.SequentEvaluator import prove_sequent, is_tautology_sequent

def get_test_env():
    env = Environment()
    env.add_propositional_variable(PropositionalVariable("p"))
    env.add_propositional_variable(PropositionalVariable("q"))
    env.add_propositional_variable(PropositionalVariable("r"))
    return env

def test_is_tautology_sequent_simple():
    env = get_test_env()
    
    # Law of Excluded Middle: p ∨ ¬ p
    f1 = parse_prop_formula("p ∨ ¬ p", env)
    assert is_tautology_sequent(f1) is True
    
    # Not a tautology: p ∧ q
    f2 = parse_prop_formula("p ∧ q", env)
    assert is_tautology_sequent(f2) is False
    
    # Implication: p ⇒ p
    f3 = parse_prop_formula("p ⇒ p", env)
    assert is_tautology_sequent(f3) is True

def test_is_tautology_sequent_complex():
    env = get_test_env()
    
    # Peirce's Law: ((p ⇒ q) ⇒ p) ⇒ p
    f1 = parse_prop_formula("((p ⇒ q) ⇒ p) ⇒ p", env)
    assert is_tautology_sequent(f1) is True
    
    # Contraposition: (p ⇒ q) ⇔ (¬ q ⇒ ¬ p)
    f2 = parse_prop_formula("(p ⇒ q) ⇔ (¬ q ⇒ ¬ p)", env)
    assert is_tautology_sequent(f2) is True
    
    # De Morgan's Law: ¬ (p ∧ q) ⇔ ¬ p ∨ ¬ q
    f3 = parse_prop_formula("¬ (p ∧ q) ⇔ ¬ p ∨ ¬ q", env)
    assert is_tautology_sequent(f3) is True
    
    # Transitivity of implication: (p ⇒ q) ∧ (q ⇒ r) ⇒ (p ⇒ r)
    f4 = parse_prop_formula("(p ⇒ q) ∧ (q ⇒ r) ⇒ (p ⇒ r)", env)
    assert is_tautology_sequent(f4) is True
    
    # Not a tautology (converse of implication): (p ⇒ q) ⇒ (q ⇒ p)
    f5 = parse_prop_formula("(p ⇒ q) ⇒ (q ⇒ p)", env)
    assert is_tautology_sequent(f5) is False
