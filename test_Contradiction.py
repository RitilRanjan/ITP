import pytest
import os
from Environment import Environment
from AST import Variable, Relation, RelationType, Connective, is_structurally_equal
from main import validate_new_name, clone_ast, get_default_env
from Frontend import parse_fol_formula, parse_prop_formula, reconstruct_string
from StorageManager import save_environment_state, load_environment_state

def test_contradiction_validation_and_ast_setup():
    parent = get_default_env()
    
    # Create f1 and f3 via parsing to ensure formatting is present
    f1 = parse_fol_formula("x = x", parent)
    f3 = parse_fol_formula("x ∈ x", parent)
    parent.local_formulae["f1"] = f1
    parent.local_formulae["f3"] = f3
    
    # f2 and f4 name clash checks (simulate logic in main.py)
    f2_name = "f2"
    f4_name = "f4"
    
    assert validate_new_name(parent, f2_name, "formula")
    assert validate_new_name(parent, f4_name, "formula")
    
    # Clashing validation: using existing name 'x'
    assert not validate_new_name(parent, "x", "formula")
    
    # Set up child env contradiction ASTs
    f1_str = reconstruct_string(f1)
    f3_str = reconstruct_string(f3)
    neg_f1_node = parse_fol_formula(f"¬ ( {f1_str} )", parent)
    neg_f3_node = parse_fol_formula(f"¬ ( {f3_str} )", parent)
    goal_node = parse_fol_formula(f"¬ ( {f3_str} ) ∧ ( {f3_str} )", parent)
    
    child = Environment(parent=parent, goal_formula_name=f4_name, target_proven_formula_name="f1")
    child.formulae[f2_name] = neg_f1_node
    child.theorems[f2_name] = clone_ast(neg_f1_node)
    child.formulae[f4_name] = goal_node
    
    # Scoping check
    assert "f1" in child.formulae
    assert "f3" in child.formulae
    assert "f2" in child.formulae
    assert "f4" in child.formulae
    assert "f2" in child.theorems
    assert "f1" not in child.theorems
    
    # Check that f2's definition is ¬(f1)
    assert isinstance(child.formulae["f2"], Connective)
    assert child.formulae["f2"].name == "¬"
    assert is_structurally_equal(child.formulae["f2"].arguments[0], f1)
    
    # Check that f4's definition is ¬(f3) ∧ (f3)
    assert isinstance(child.formulae["f4"], Connective)
    assert child.formulae["f4"].name == "∧"
    assert child.formulae["f4"].arguments[0].name == "¬"
    assert is_structurally_equal(child.formulae["f4"].arguments[0].arguments[0], f3)
    assert is_structurally_equal(child.formulae["f4"].arguments[1], f3)


def test_contradiction_proving_resolution():
    parent = get_default_env()
    f1 = parse_fol_formula("x = x", parent)
    f3 = parse_fol_formula("x ∈ x", parent)
    parent.local_formulae["f1"] = f1
    parent.local_formulae["f3"] = f3
    
    f2_name = "f2"
    f4_name = "f4"
    
    f1_str = reconstruct_string(f1)
    f3_str = reconstruct_string(f3)
    neg_f1_node = parse_fol_formula(f"¬ ( {f1_str} )", parent)
    neg_f3_node = parse_fol_formula(f"¬ ( {f3_str} )", parent)
    goal_node = parse_fol_formula(f"¬ ( {f3_str} ) ∧ ( {f3_str} )", parent)
    
    child = Environment(parent=parent, goal_formula_name=f4_name, target_proven_formula_name="f1")
    child.formulae[f2_name] = neg_f1_node
    child.theorems[f2_name] = clone_ast(neg_f1_node)
    child.formulae[f4_name] = goal_node
    
    # Simulate proving the goal f4
    child.theorems[f4_name] = clone_ast(goal_node)
    
    # Run the REPL loop popping simulation
    env = child
    while env.goal_formula_name is not None and env.goal_formula_name in env.theorems:
        goal_name = env.goal_formula_name
        goal_node_val = env.theorems[goal_name]
        p = env.parent
        
        if getattr(env, "target_proven_formula_name", None):
            target_name = env.target_proven_formula_name
            p.theorems[target_name] = clone_ast(p.formulae[target_name])
        else:
            p.theorems[goal_name] = clone_ast(goal_node_val)
            
        env = p
        
    assert env is parent
    # The goal f4 itself is not in parent theorems, but the target f1 is!
    assert "f4" not in parent.theorems
    assert "f1" in parent.theorems


def test_contradiction_serialization():
    # Setup hierarchy
    parent = get_default_env()
    f1 = parse_fol_formula("x = x", parent)
    f3 = parse_fol_formula("x ∈ x", parent)
    parent.local_formulae["f1"] = f1
    parent.local_formulae["f3"] = f3
    
    f2_name = "f2"
    f4_name = "f4"
    
    f1_str = reconstruct_string(f1)
    f3_str = reconstruct_string(f3)
    neg_f1_node = parse_fol_formula(f"¬ ( {f1_str} )", parent)
    neg_f3_node = parse_fol_formula(f"¬ ( {f3_str} )", parent)
    goal_node = parse_fol_formula(f"¬ ( {f3_str} ) ∧ ( {f3_str} )", parent)
    
    child = Environment(parent=parent, goal_formula_name=f4_name, target_proven_formula_name="f1")
    child.formulae[f2_name] = neg_f1_node
    child.theorems[f2_name] = clone_ast(neg_f1_node)
    child.formulae[f4_name] = goal_node
    
    # Save environment state to file
    filepath = "contra_temp_state.txt"
    try:
        save_environment_state(child, filepath)
        
        # Reload environment state using actual default env loader
        loaded_child = load_environment_state(filepath, get_default_env)
        
        # Check that loaded child env contains target_proven_formula_name
        assert loaded_child.goal_formula_name == f4_name
        assert loaded_child.target_proven_formula_name == "f1"
        assert "f2" in loaded_child.formulae
        assert "f2" in loaded_child.theorems
        assert "f4" in loaded_child.formulae
        
        # Check correct formula equality
        assert loaded_child.formulae["f2"].name == "¬"
        assert loaded_child.formulae["f4"].name == "∧"
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
