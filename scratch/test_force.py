from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
import backend.CommandHandlers.logic_handlers # ensure handlers are registered
import backend.CommandHandlers.definition_handlers

def test_force():
    env = Environment(theory="ZFC")
    # Define a formula
    registry.dispatch("cv", "x", env)
    registry.dispatch("cv", "y", env)
    registry.dispatch("cf", "f1 ∀x (x = x)", env)
    
    if "f1" not in env.formulae:
        print("Failed to create f1")
        return
        
    print(f"Before force, f1 in theorems: {'f1' in env.theorems}")
    
    registry.dispatch("force", "f1", env)
    
    print(f"After force, f1 in theorems: {'f1' in env.theorems}")
    
    # Test mission forcing
    registry.dispatch("cf", "goal ∀y (y = y)", env)
    registry.dispatch("mission", "goal", env)
    
    # Current env is now the child env
    child_env = env.children[-1]
    registry.dispatch("force", "goal", child_env)
    
    # After mission completes, the child is popped, and goal is added to parent theorems
    print(f"After mission force, goal in parent theorems: {'goal' in env.theorems}")
    print(f"Number of children remaining: {len(env.children)}")

if __name__ == "__main__":
    test_force()
