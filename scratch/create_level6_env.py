from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
import backend.CommandHandlers.logic_handlers
import backend.CommandHandlers.definition_handlers
from backend.StorageManager import serialize_environment_state

def main():
    env = Environment(theory="NT")
    registry.dispatch("cv", env, "x")
    registry.dispatch("cv", env, "y")
    registry.dispatch("cv", env, "n")
    registry.dispatch("cv", env, "m")
    
    # In level 5, the proof was for ∀x 0 + x = x
    registry.dispatch("cf", env, "add_id_left ∀x (0 + x = x)")
    
    if "add_id_left" not in env.formulae:
        print("Failed to create formula!")
        return
        
    registry.dispatch("force", env, "add_id_left")
    
    env_str = serialize_environment_state(env)
    
    path = "games/natural number game/level6_start_env.txt"
    with open(path, "w") as f:
        f.write(env_str)
    
    print(f"Successfully generated {path}")

if __name__ == "__main__":
    main()
