import pytest
from backend.AST import PropositionalVariable, Connective
from backend.Environment import Environment
from backend.Parser import parse_prop_formula
from backend.TruthEvaluator import get_prop_variables, evaluate_prop, is_tautology

def get_test_env():
    env = Environment()
    # Add enough propositional variables
    for i in range(20):
        env.add_propositional_variable(PropositionalVariable(f"p{i}"))
        env.add_propositional_variable(PropositionalVariable(f"q{i}"))
    env.add_propositional_variable(PropositionalVariable("p"))
    env.add_propositional_variable(PropositionalVariable("q"))
    env.add_propositional_variable(PropositionalVariable("r"))
    return env

def test_get_prop_variables():
    env = get_test_env()
    f = parse_prop_formula("p ∧ q ⇒ p ∨ r", env)
    assert get_prop_variables(f) == {"p", "q", "r"}

def test_is_tautology_simple():
    env = get_test_env()
    
    # Law of Excluded Middle: p ∨ ¬ p
    f1 = parse_prop_formula("p ∨ ¬ p", env)
    assert is_tautology(f1) is True
    
    # Not a tautology: p ∧ q
    f2 = parse_prop_formula("p ∧ q", env)
    assert is_tautology(f2) is False
    
    # Implication: p ⇒ p
    f3 = parse_prop_formula("p ⇒ p", env)
    assert is_tautology(f3) is True

def test_is_tautology_complex():
    env = get_test_env()
    
    # Peirce's Law: ((p ⇒ q) ⇒ p) ⇒ p
    f1 = parse_prop_formula("((p ⇒ q) ⇒ p) ⇒ p", env)
    assert is_tautology(f1) is True
    
    # De Morgan's Law: ¬ (p ∧ q) ⇔ ¬ p ∨ ¬ q
    f2 = parse_prop_formula("¬ (p ∧ q) ⇔ ¬ p ∨ ¬ q", env)
    assert is_tautology(f2) is True
    
    # Transitivity of implication: (p ⇒ q) ∧ (q ⇒ r) ⇒ (p ⇒ r)
    f3 = parse_prop_formula("(p ⇒ q) ∧ (q ⇒ r) ⇒ (p ⇒ r)", env)
    assert is_tautology(f3) is True
    
    # Not a tautology (converse of implication): (p ⇒ q) ⇒ (q ⇒ p)
    f4 = parse_prop_formula("(p ⇒ q) ⇒ (q ⇒ p)", env)
    assert is_tautology(f4) is False

def test_variable_count_limit():
    env = get_test_env()
    
    # 16 variables: p0 to p15 (should work)
    vars_16 = [f"p{i}" for i in range(16)]
    expr_16 = " ∧ ".join(vars_16)
    f_16 = parse_prop_formula(expr_16, env)
    assert len(get_prop_variables(f_16)) == 16
    # Should not raise an error, just evaluate (which evaluates to False)
    assert is_tautology(f_16) is False
    
    # 17 variables: p0 to p16 (should raise ValueError)
    vars_17 = [f"p{i}" for i in range(17)]
    expr_17 = " ∧ ".join(vars_17)
    f_17 = parse_prop_formula(expr_17, env)
    assert len(get_prop_variables(f_17)) == 17
    
    with pytest.raises(ValueError):
        is_tautology(f_17)
