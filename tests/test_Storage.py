import os
import pytest
from Environment import Environment
from AST import (
    Variable, DummyVariable, MetaVariable, PropositionalVariable,
    Function, FunctionType, Relation, RelationType, Node
)
from Frontend import parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string
from StorageManager import (
    save_environment_state, load_environment_state, save_history, load_history
)
from main import get_default_env

def test_state_save_and_load():
    # 1. Prepare environment
    env = get_default_env()
    
    # Add variables and other objects
    env.add_variable(Variable("z"))
    env.add_variable(Variable("w"))
    env.add_dummy_variable(DummyVariable("_1"))
    env.add_dummy_variable(DummyVariable("_2"))
    env.add_dummy_variable(DummyVariable("_3"))
    env.add_meta_variable(MetaVariable("?M"))
    env.add_propositional_variable(PropositionalVariable("r"))
    
    # Add user-defined function
    # def_f 1 f z S _1
    def_f_node = parse_term("S _1", env)
    env.user_functions["f"] = (1, def_f_node)
    decl_f = Function("f", 1, FunctionType.USER_DEFINED, [DummyVariable("_1")])
    env.local_terms["f"] = decl_f
    
    # Add user-defined relation
    # def_r 2 x R y x = y
    def_r_node = parse_fol_formula("_1 = _2", env)
    env.user_relations["R"] = (2, def_r_node)
    decl_r = Relation("R", 2, RelationType.USER_DEFINED, [DummyVariable("_1"), DummyVariable("_2")])
    env.local_formulae["R"] = decl_r
    
    # Add term, formula, and theorem
    t1_node = parse_term("f z", env)
    env.local_terms["t1"] = t1_node
    
    f1_node = parse_fol_formula("z R w", env)
    env.local_formulae["f1"] = f1_node
    env.local_theorems["th1"] = f1_node
    
    # 2. Save
    filepath = "save_files/test_state_1.md"
    save_environment_state(env, filepath)
    
    # Verify save file exists
    assert os.path.exists(filepath)
    
    # 3. Load
    loaded_env = load_environment_state(filepath, get_default_env)
    
    # 4. Verify loaded environment
    assert "z" in loaded_env.variables
    assert "w" in loaded_env.variables
    assert "_3" in loaded_env.dummy_variables
    assert "?M" in loaded_env.meta_variables
    assert "r" in loaded_env.propositional_variables
    assert "f" in loaded_env.user_functions
    assert "R" in loaded_env.user_relations
    assert "t1" in loaded_env.terms
    assert "f1" in loaded_env.formulae
    assert "th1" in loaded_env.theorems
    
    # Clean up
    if os.path.exists(filepath):
        os.remove(filepath)

def test_nested_states():
    # 1. Prepare nested hierarchy
    parent = get_default_env()
    parent.add_variable(Variable("z"))
    
    # Create child environment
    child = Environment(parent=parent, goal_formula_name="f1")
    child.add_variable(Variable("w"))
    
    # Add local theorem in child
    f1_node = parse_fol_formula("z = w", child)
    child.local_formulae["f1"] = f1_node
    child.local_theorems["th1"] = f1_node
    
    # 2. Save
    filepath = "save_files/test_state_nested.md"
    save_environment_state(child, filepath)
    
    # 3. Load
    loaded_child = load_environment_state(filepath, get_default_env)
    
    # 4. Verify
    assert loaded_child.goal_formula_name == "f1"
    assert "w" in loaded_child.local_variables
    assert "z" in loaded_child.variables
    assert "z" not in loaded_child.local_variables
    assert "th1" in loaded_child.local_theorems
    
    # Clean up
    if os.path.exists(filepath):
        os.remove(filepath)

def test_history_save_and_load():
    cmds = ["cv z", "cf f1 z=z", "ua E1 f1"]
    filepath = "history_files/test_history_1.md"
    
    # Save
    save_history(cmds, filepath)
    assert os.path.exists(filepath)
    
    # Load
    loaded_cmds = load_history(filepath)
    assert loaded_cmds == cmds
    
    # Clean up
    if os.path.exists(filepath):
        os.remove(filepath)
