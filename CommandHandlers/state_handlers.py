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

@registry.register("show", category="Environment Tools", help_text="Print the active environment variables and formulae")
def handle_show(env: Environment, args_str: str) -> None:
    show_environment(env)

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

@registry.register("guide", category="Environment Tools", help_text="Show this command guide", aliases=["help"])
def handle_help(env: Environment, args_str: str) -> None:
    W = 80
    def _cyan(s: str) -> str: return f"\033[36m{s}\033[0m"
    def _blue(s: str) -> str: return f"\033[34m{s}\033[0m"
    def _bold(s: str) -> str: return f"\033[1m{s}\033[0m"
    def _green(s: str) -> str: return f"\033[32m{s}\033[0m"

    print(_cyan("=" * W))
    print(_cyan(_bold(" INTERACTIVE THEOREM PROVER — COMMAND GUIDE ".center(W, "="))))
    print(_cyan("=" * W))

    print("\n" + _blue(_bold("── Universal Transformation Syntax ────────────────────────────────────────────────")))
    print("  Many transformation commands share a standardized 'fold'-style syntax:")
    print("      " + _green("command [args...] [occurrences] [<target>] [<out>] [<equiv>]"))
    print("\n  " + _bold("Arguments:"))
    print("    [occ]      : Comma-separated list of 1-based indices (e.g. 1,3). 0/omit for all.")
    print("    <target>   : The formula or term to modify.")
    print("    <out>      : Optional name for the new formula/term. If omitted, it will")
    print("                 modify the <target> in-place (if created locally).")
    print("    <equiv>    : Optional name for a new proven equivalence (target ⇔ out).")
    print("\n  " + _bold("The 0-Argument Rule:"))
    print("    If <target> is omitted, the command defaults to the ACTIVE GOAL.")
    print("    If <out> is also omitted, it modifies the goal in-place.")

    print("\n" + _blue(_bold("── Substitutions & Transformations ────────────────────────────────────────────────")))
    print(_bold("  [Term Substitutions]"))
    print("  st   v t1        [occ] <target> [<out>]             Substitute term t1 for var v in term")
    print(_bold("  [Formula Substitutions]"))
    print("  sf   v t1        [occ] [<target>] [<out>]           Substitute term t1 for free var v")
    print("  sa   v t1        [occ] [<target>] [<out>]           Substitute t1 for ALL occurrences of v")
    print("  sp   pv p1       [occ] [<target>] [<out>]           Substitute prop-formula p1 for prop-var pv")
    print("  sb   v t1        [occ] [<target>] [<out>] [<equiv>] Rename bound variable v to var t1")
    print(_bold("  [Logic & Negation]"))
    print("  neg-             [occ] [<target>] [<out>] [<equiv>] Remove ¬¬Ψ→Ψ")
    print("  neg+             [occ] [<target>] [<out>] [<equiv>] Wrap Ψ→¬¬Ψ")
    print("  fold <sym>       [occ] [<target>] [<out>] [<equiv>] Unroll definitions (∃, ∃!, {, func/rel)")
    print("  fold all               [<target>] [<out>] [<equiv>] Recursively unroll all definitions")
    print(_bold("  [Equational Rewriting]"))
    print("  simp_l_eq <thm>  [occ] [<target>] [<out>] [<equiv>] Replace LHS with RHS of theorem")
    print("  simp_r_eq <thm>  [occ] [<target>] [<out>] [<equiv>] Replace RHS with LHS of theorem")
    print("  simp_l_bi <thm>  [occ] [<target>] [<out>] [<equiv>] Replace LHS with RHS of bi-implication")
    print("  simp_r_bi <thm>  [occ] [<target>] [<out>] [<equiv>] Replace RHS with LHS of bi-implication")

    print("\n" + _blue(_bold("── Logic Elimination & Introduction (Mission Tactics) ─────────────────────────────")))
    print("  intro  [<target>] <term> [<out>] [<equiv>] Instantiates ∀/∃ premises or reduces goals")
    print("  left   [<target>] [<out>]                  Reduce goal/premise Ψ∨Φ to Ψ")
    print("  right  [<target>] [<out>]                  Reduce goal/premise Ψ∨Φ to Φ")
    print("  and    [<target>] [<out1>] <out2>          Split Ψ∧Φ into two goals/premises")
    print("  imply  [<target>] [<out1>] <out2>          Split Ψ⇒Φ or reduce goal to consequent")

    print("\n" + _blue(_bold("── Mission Management & Inference ─────────────────────────────────────────────────")))
    print("  mission <f>                 Enter a child environment to prove goal formula f")
    print("  contra  [<f1>] f2 f3        Proof by contradiction: f2 = ¬f1, goal f3 = ⊥")
    print("  exit                        Leave current environment / resolve mission")
    print("  show                        Print the active environment variables and formulae")
    print("  apply   [<target>] <ax/r>   Prove goal or <target> using axiom/rule and premises")
    print("  apply2  <QR1|QR2> f1        Back-compute required premise from goal")
    print("  apply3  f1 f2               Modus ponens backwards (goal matches RHS of f1)")
    print("  auto    <formula>           Auto-prove via fundamental axioms, QR1/QR2, PC2/PC3")
    
    print("\n" + _blue(_bold("── Automated Search ───────────────────────────────────────────────────────────────")))
    print("  search <formula> [time] [space]              Forward graph search")
    print("  backward_search <formula> [time] [space]     Refutation-based backward search")
    print("  advanced_search <formula> [flags...]         Advanced heuristic backward search")

    print("\n" + _blue(_bold("── Definitions & Environment Tools ────────────────────────────────────────────────")))
    print("  cv  <name1> [name2 ...]     Create FOL variables")
    print("  cV  <name1> [name2 ...]     Create propositional variables")
    print("  ct  <name> <term_expr>      Create a term")
    print("  cf  <name> <fol_expr>       Create a 1st-order formula")
    print("  cp  <name> <prop_expr>      Create a propositional formula")
    print("  dt  <theorem>               Delete a proven theorem (from any environment)")
    print("  save / load                 Save/Load environment state to disk")
    print("  save_h / load_h             Save/Load command history to disk")
    print("=" * W)

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
