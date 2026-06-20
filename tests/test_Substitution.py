import pytest
from AST import Variable, PropositionalVariable, Function, FunctionType, Relation, RelationType, Connective, Quantifier
from Environment import Environment
from Frontend import parse_term, parse_fol_formula, parse_prop_formula
from SubstitutionManager import (
    get_free, get_bound, check_free, check_bound,
    is_substitutable_free, is_substitutable_bound,
    substitute_free, substitute_bound, substitute_all, substitute_term, substitute_proposition,
    find_substituted, clone_ast
)

def get_test_env():
    env = Environment()
    env.add_variable(Variable("x"))
    env.add_variable(Variable("y"))
    env.add_variable(Variable("z"))
    env.add_variable(Variable("A"))
    env.add_propositional_variable(PropositionalVariable("p"))
    env.add_propositional_variable(PropositionalVariable("q"))
    
    dummy = Variable("x")
    env.add_term(Function("S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_term(Function("+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    env.add_formula(Relation("=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation("∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_free_bound():
    env = get_test_env()
    
    # x = y ∨ ∀ x ( x ∈ A )
    f = parse_fol_formula("x = y ∨ ∀ x ( x ∈ A )", env)
    assert get_free(f) == {"x", "y", "A"}
    assert get_bound(f) == {"x"}
    
    assert check_free(f, "x") is True
    assert check_bound(f, "x") is True
    assert check_free(f, "y") is True
    assert check_bound(f, "y") is False

def test_substitutable_free():
    env = get_test_env()
    
    # ∀ y ( x = y )
    f = parse_fol_formula("∀ y ( x = y )", env)
    term_y = parse_term("y", env)
    term_z = parse_term("z", env)
    
    # y is not substitutable for x because y is bound by ∀y enclosing x
    assert is_substitutable_free("x", term_y, f) is False
    # z is substitutable because z is not bound by any enclosing quantifier of x
    assert is_substitutable_free("x", term_z, f) is True

def test_substitutable_bound():
    env = get_test_env()
    
    # ∀ x ( x = y )
    f = parse_fol_formula("∀ x ( x = y )", env)
    
    # Renaming bound x to z is valid because z is not free in scope, nor captured
    assert is_substitutable_bound("x", "z", f) is True
    # Renaming bound x to y is invalid because y is free in the scope x = y
    assert is_substitutable_bound("x", "y", f) is False

def test_substitutions():
    env = get_test_env()
    
    # Test substitute_term
    t = parse_term("S x + S x", env)
    t_rep = parse_term("y", env)
    # substitute all x
    t_cloned = clone_ast(t)
    substitute_term(t_cloned, "x", t_rep)
    assert get_term_vars(t_cloned) == {"y"}
    
    # substitute 2nd occurrence of x only
    t_cloned2 = clone_ast(t)
    substitute_term(t_cloned2, "x", t_rep, occurrence_idx=2)
    # 2nd occurrence is replaced, 1st remains
    # S x + S y
    assert get_term_vars(t_cloned2) == {"x", "y"}

def get_term_vars(node):
    from SubstitutionManager import get_term_vars as gtv
    return gtv(node)

def test_find_substituted():
    env = get_test_env()
    
    f1 = parse_fol_formula("x = y", env)
    f2 = parse_fol_formula("S x = y", env)
    res = find_substituted(f1, f2)
    assert res is not None
    assert isinstance(res, Function)
    assert res.name == "S"
    
    f3 = parse_fol_formula("S y = y", env)
    # x in f1 was replaced by S y?
    # f1 is x = y. If we replace x with S y, we get S y = y. Yes!
    res2 = find_substituted(f1, f3)
    assert res2 is not None
    assert res2.name == "S"

def test_replace_structurally():
    env = get_test_env()
    from SubstitutionManager import replace_structurally
    from Frontend import reconstruct_string
    
    t1 = parse_term("x + y + x", env)
    
    x_node = parse_term("x", env)
    sz_node = parse_term("S z", env)
    
    t2 = replace_structurally(t1, x_node, sz_node, occurrence_idx=2)
    assert reconstruct_string(t2) == "x + y + S z"
    
    t3 = replace_structurally(t1, x_node, sz_node)
    assert reconstruct_string(t3) == "S z + y + S z"
    
    f1 = parse_fol_formula("x = y ∨ x = y", env)
    xy_node = parse_fol_formula("x = y", env)
    sz_node2 = parse_fol_formula("S z = y", env)
    
    f2 = replace_structurally(f1, xy_node, sz_node2, occurrence_idx=1)
    assert reconstruct_string(f2).replace(" ", "") == "S z = y ∨ x = y".replace(" ", "")


def test_remove_double_neg():
    env = get_test_env()
    from SubstitutionManager import remove_double_neg
    from Frontend import reconstruct_string

    # Build ¬¬(x=y) ∨ ¬¬(x=y)
    f1 = parse_fol_formula("x = y", env)
    nn1 = Connective(name="¬", arity=1, arguments=[Connective(name="¬", arity=1, arguments=[f1])])
    import copy
    nn2 = copy.deepcopy(nn1)
    formula = Connective(name="∨", arity=2, arguments=[nn1, nn2])

    # Remove all double negations
    result_all = remove_double_neg(formula)
    r_str = reconstruct_string(result_all).replace(" ", "")
    assert "¬¬" not in r_str, f"Expected no double negations, got: {r_str}"

    # Remove only the first occurrence
    result_1 = remove_double_neg(formula, occurrence_idx=1)
    r1_str = reconstruct_string(result_1).replace(" ", "")
    # Second ¬¬ should still be present
    assert r1_str.count("¬¬") == 1, f"Expected exactly one ¬¬ remaining, got: {r1_str}"

    # Remove only the second occurrence
    result_2 = remove_double_neg(formula, occurrence_idx=2)
    r2_str = reconstruct_string(result_2).replace(" ", "")
    # First ¬¬ should still be present
    assert r2_str.count("¬¬") == 1, f"Expected exactly one ¬¬ remaining, got: {r2_str}"


def test_add_double_neg():
    env = get_test_env()
    from SubstitutionManager import add_double_neg
    from Frontend import reconstruct_string, parse_fol_formula

    f1 = parse_fol_formula("x = y", env)

    # Wrap at the first (and only) occurrence of the top formula
    result = add_double_neg(f1, occurrence_idx=1)
    r_str = reconstruct_string(result).replace(" ", "")
    assert r_str.startswith("¬¬"), f"Expected ¬¬ prefix, got: {r_str}"

    # No occurrence_idx: wraps the root (and descends into children)
    # For a bare atomic formula, this just wraps it
    result_all = add_double_neg(f1)
    r_all = reconstruct_string(result_all).replace(" ", "")
    assert "¬¬" in r_all, f"Expected ¬¬ in result, got: {r_all}"
