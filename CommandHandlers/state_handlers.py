import os
import sys
from typing import List, Callable, Optional, Tuple, Any

from Environment import Environment
from Frontend import show_environment, lex
from StorageManager import save_environment_state, load_environment_state, save_history, load_history
from AutoProver import auto_prove
from GraphSearch import forward_search
from BackwardSearch import backward_search, advanced_search
from ProofLogger import proof_logger
from CommandHandlers.CommandRegistry import registry



@registry.register("exit", category="Environment Tools", help_text="Leave current environment / resolve mission")
def handle_exit(env: Environment, args_str: str) -> Optional[Environment]:
    if env.parent is not None:
        goal_name = env.goal_formula_name
        print(f"Terminated child environment for goal '{goal_name}' without proving it. Returned to parent environment.")
        return env.parent
    else:
        print("Goodbye!")
        import sys
        sys.exit(0)



@registry.register("save", category="Environment Tools", help_text="Save the environment state to disk")
def handle_save(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    try:
        from CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return
    if not name:
        print("Error: Filename cannot be empty.")
        return
    filepath = os.path.join("save_files", name)
    if os.path.exists(filepath):
        print("Error: A save file with that name already exists.")
        return
    try:
        save_environment_state(env, filepath)
        print(f"Saved state to '{filepath}'")
    except Exception as e:
        print(f"Error: {e}")

@registry.register("load", category="Environment Tools", help_text="Load the environment state from disk")
def handle_load(env: Environment, args_str: str, get_default_env, command_queue: list = None, inputs_collected: list = None) -> Any:
    try:
        from CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename to load: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return None
    if not name:
        print("Error: Filename cannot be empty.")
        return None
    filepath = os.path.join("save_files", name)
    if not os.path.exists(filepath):
        print(f"Error: Save file '{filepath}' not found.")
        return None
    try:
        new_env = load_environment_state(filepath, get_default_env)
        print(f"Loaded state from '{filepath}'")
        return new_env
    except Exception as e:
        print(f"Error: {e}")
        return None

@registry.register("save_h", category="Environment Tools", help_text="Save command history to disk")
def handle_save_h(env: Environment, args_str: str, history_commands: list, command_queue: list = None, inputs_collected: list = None) -> None:
    try:
        from CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return
    if not name:
        print("Error: Filename cannot be empty.")
        return
    filepath = os.path.join("history_files", name)
    if os.path.exists(filepath):
        print("Error: A history file with that name already exists.")
        return
    try:
        # Extract only command strings if necessary
        clean_history = [cmd[0] if isinstance(cmd, tuple) else cmd for cmd in history_commands]
        save_history(clean_history, filepath)
        print(f"Saved history to '{filepath}'")
    except Exception as e:
        print(f"Error: {e}")

@registry.register("load_h", category="Environment Tools", help_text="Load command history from disk")
def handle_load_h(env: Environment, args_str: str, history_commands: list, command_queue: list = None, inputs_collected: list = None) -> None:
    try:
        from CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename to load: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return
    if not name:
        print("Error: Filename cannot be empty.")
        return
    filepath = os.path.join("history_files", name)
    if not os.path.exists(filepath):
        print(f"Error: History file '{filepath}' not found.")
        return
    try:
        cmds = load_history(filepath)
        history_commands.clear()
        command_queue.extend(cmds)
        print(f"Loaded history from '{filepath}'. Replaying {len(cmds)} commands...")
    except Exception as e:
        print(f"Error: {e}")

@registry.register("auto", category="Automated Proofs", help_text="Auto-prove via fundamental axioms, QR1/QR2, PC2")
def handle_auto(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: auto <formula>")
        return
    f1_name = cmd_args[0]
    if f1_name not in env.formulae:
        print(f"Error: Formula '{f1_name}' not found.")
        return
    
    try:
        success = auto_prove(f1_name, env, visited_nodes=None, proof_logger=proof_logger)
        if success:
            print(f"Formula '{f1_name}' has been successfully proven automatically!")
        else:
            print(f"Failed to prove formula '{f1_name}' automatically.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error during auto proof: {e}")

@registry.register("search", category="Automated Proofs", help_text="Forward graph search")
def handle_search(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: search <formula> [time_limit_sec] [space_limit_nodes]")
        return
    f1_name = cmd_args[0]
    time_limit = 10.0
    space_limit = 10000
    if len(cmd_args) >= 2:
        try:
            time_limit = float(cmd_args[1])
        except ValueError:
            print("Error: time_limit must be a float or integer representing seconds.")
            return
    if len(cmd_args) >= 3:
        try:
            space_limit = int(cmd_args[2])
        except ValueError:
            print("Error: space_limit must be an integer representing maximum structures.")
            return
    
    try:
        forward_search(env, f1_name, time_limit, space_limit)
        if f1_name in env.theorems:
            proof_logger.log_summary(f1_name, env.formulae[f1_name], "forward-graph-search")
    except Exception as e:
        print(f"Error during graph search: {e}")

@registry.register("backward_search", category="Automated Proofs", help_text="Refutation-based backward search")
def handle_backward_search(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: backward_search <formula> [time_limit_sec] [space_limit_nodes] [+proof]")
        return
    
    f1_name = cmd_args[0]
    time_limit = 10.0
    space_limit = 10000
    generate_proof = False
    
    for arg in cmd_args[1:]:
        if arg == "+proof":
            generate_proof = True
        else:
            try:
                if "." in arg:
                    time_limit = float(arg)
                else:
                    space_limit = int(arg)
            except ValueError:
                print(f"Error: Invalid argument '{arg}'")
                return
    try:
        success = backward_search(env, f1_name, time_limit, space_limit, generate_proof, proof_logger=proof_logger)
        if success:
            print(f"Goal '{f1_name}' has been successfully proven and added to the environment.")
    except Exception as e:
        print(f"Error during backward search: {e}")

@registry.register("advanced_search", category="Automated Proofs", help_text="Advanced heuristic backward search")
def handle_advanced_search(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: advanced_search <formula> [time_limit_sec] [space_limit_nodes] [+sos] [+unit] [+subsumption] [+paramodulation] [+ordering] [+proof]")
        return
    
    f1_name = cmd_args[0]
    time_limit = 10.0
    space_limit = 10000
    generate_proof = False
    flags = {"sos": False, "unit": False, "subsumption": False, "paramodulation": False, "ordering": False}
    
    # parse numeric arguments and flags
    for arg in cmd_args[1:]:
        if arg == "+proof":
            generate_proof = True
        elif arg.startswith("+"):
            flag_name = arg[1:].lower()
            if flag_name in flags:
                flags[flag_name] = True
            else:
                print(f"Warning: Unknown flag '{arg}'")
        else:
            try:
                if "." in arg:
                    time_limit = float(arg)
                else:
                    space_limit = int(arg)
            except ValueError:
                print(f"Error: Invalid argument '{arg}'")
                return
                
    try:
        success = advanced_search(env, f1_name, time_limit, space_limit, flags, generate_proof, proof_logger=proof_logger)
        if success:
            print(f"Goal '{f1_name}' has been successfully proven and added to the environment.")
    except Exception as e:
        print(f"Error during advanced backward search: {e}")

@registry.register("dt", category="Environment Tools", help_text="Delete a proven theorem")
def handle_dt(env: Environment, args_str: str) -> None:
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    if len(cmd_args) < 1:
        print("Error: Usage: dt <theorem>")
        return
    th_name = cmd_args[0]
    if th_name not in env.theorems:
        print(f"Error: Theorem '{th_name}' not found in proven theorems.")
        return
    env.remove_theorem(th_name)
    print(f"Deleted proven theorem '{th_name}'.")
