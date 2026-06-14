import pytest
from Environment import Environment
from AST import Variable, Relation, RelationType
from main import validate_new_name, clone_ast

def test_environment_scoping():
    parent = Environment()
    parent.add_variable(Variable("x"))
    
    child = Environment(parent=parent, goal_formula_name="f1")
    child.add_variable(Variable("y"))
    
    # Scoping lookup checks
    assert "x" in child.variables
    assert "y" in child.variables
    assert "y" not in parent.variables
    
    # validate_new_name clashes check
    assert not validate_new_name(child, "x", "term")
    assert validate_new_name(child, "z", "variable")

def test_mission_proving_simulation():
    parent = Environment()
    goal = Relation("=", 2, RelationType.PRE_DEFINED, [Variable("x"), Variable("x")])
    parent.local_formulae["f1"] = goal
    
    child = Environment(parent=parent, goal_formula_name="f1")
    
    # Simulate proving the goal
    child.theorems["f1"] = clone_ast(goal)
    
    # Simulate the REPL loop goal check
    env = child
    while env.goal_formula_name is not None and env.goal_formula_name in env.theorems:
        goal_name = env.goal_formula_name
        goal_node = env.theorems[goal_name]
        p = env.parent
        p.theorems[goal_name] = clone_ast(goal_node)
        env = p
        
    assert env is parent
    assert "f1" in parent.theorems
