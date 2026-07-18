from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
import backend.CommandHandlers.logic_handlers 
import backend.CommandHandlers.definition_handlers
from backend.AST import DummyVariable, Relation, RelationType

def test_force():
    env = Environment()
    dummy = DummyVariable("x")
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    registry.dispatch("cv", env, "x y")
    registry.dispatch("cf", env, "f1 ∀x (x = x)")
    
    print(f"Before force, f1 in theorems: {'f1' in env.theorems}")
    
    registry.dispatch("force", env, "f1")
    
    print(f"After force, f1 in theorems: {'f1' in env.theorems}")
    
    registry.dispatch("cf", env, "goal ∀y (y = y)")
    registry.dispatch("mission", env, "goal")
    
    child_env = env.children[-1]
    registry.dispatch("force", child_env, "goal")
    
    print(f"After mission force, goal in parent theorems: {'goal' in env.theorems}")
    print(f"Number of children remaining: {len(env.children)}")

test_force()
