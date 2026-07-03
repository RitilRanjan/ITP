import sys
import os
import builtins
from CommandHandlers.mission_handlers import handle_mission, handle_contra
from CommandHandlers.logic_handlers import (
    handle_left_right, handle_and, handle_imply, handle_intro,
    handle_apply
)
from CommandHandlers.env_handlers import (
    handle_cv, handle_cV, handle_ct, handle_cf, handle_cp,
    handle_st, handle_sf, handle_sb, handle_sa, handle_sp
)
from CommandHandlers.definition_handlers import (
    handle_def_f, handle_def_r
)
from CommandHandlers.state_handlers import (
    handle_save, handle_load, handle_save_h, handle_load_h,
    handle_auto, handle_search, handle_backward_search, handle_advanced_search, handle_dt
)
from CommandHandlers.transformation_handlers import (
    handle_fold, handle_simp, handle_neg
)
import CommandHandlers.terminal_handlers
from CommandHandlers.utils import validate_new_name, get_target_resolutions, handle_variable_capture_interactive

from typing import Optional, Tuple
import re
import builtins

original_print = builtins.print

def custom_print(*args, **kwargs):
    if "file" in kwargs:
        original_print(*args, **kwargs)
        return
        
    text = " ".join(str(a) for a in args)
    
    if "\033[" in text or "\x1b[" in text:
        original_print(*args, **kwargs)
        return
        
    if text.startswith("ITP ") or text.startswith("\nITP ") or \
       text.startswith("Interactive Theorem Prover REPL") or \
       text.startswith("Enter a command or") or \
       text.startswith("Enable foundational proof logging") or \
       text.startswith("Proof logging disabled"):
        original_print(*args, **kwargs)
        return
        
    if text == "":
        original_print(*args, **kwargs)
        return
        
    def replacer(match):
        return f"\033[34m{match.group(0)}\033[36m"
        
    subbed = re.sub(r"'[^']*'", replacer, text)
    colored_text = f"\033[36m{subbed}\033[0m"
    original_print(colored_text, **kwargs)

builtins.print = custom_print

from Environment import Environment
from AST import (
    Node, SetBuilder, Variable, DummyVariable, PropositionalVariable, Function, FunctionType,
    Relation, RelationType, Quantifier, Connective, MetaVariable, Constant
)
from Frontend import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError, lex
)
from SubstitutionManager import (
    substitute_free, substitute_bound, substitute_all, substitute_term, substitute_proposition,
    is_substitutable_free, is_substitutable_bound, clone_ast, get_term_vars
)

from AutoProver import auto_prove
from GraphSearch import forward_search
from BackwardSearch import backward_search, advanced_search
from ProofLogger import proof_logger
# Global flag to track if the current command resulted in an error or warning
has_error = False
_original_print = builtins.print

def print(*args, **kwargs):
    global has_error
    msg = " ".join(str(x) for x in args)
    if msg.startswith("Error:") or msg.startswith("Parser Error:") or msg.startswith("Warning:"):
        has_error = True
    _original_print(*args, **kwargs)

from DefinitionExpander import (
    expand_user_defined_function_in_term, expand_user_defined_function_in_formula,
    expand_user_defined_relation_in_formula, expand_existential_in_formula,
    expand_unique_existential_in_formula, expand_set_builder_in_formula,
    expand_epsilon_in_formula, expand_iota_in_formula,
    VariableCaptureError
)

def get_default_env(theory: str = "ZFC") -> Environment:
    env = Environment(theory=theory)
    
    dummy = Variable("x")
    # Pre-defined relation symbol = (equality, arity 2)
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    if theory == "ZFC":
        env.add_term(Constant("∅"))
        env.add_term(Constant("U"))
        env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    elif theory == "NT":
        env.add_term(Constant("0"))
        env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
        env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
        env.add_term(Function(name="*", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
        env.add_term(Function(name="^", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    # Pre-defined propositional variables
    env.add_propositional_variable(PropositionalVariable("p"))
    env.add_propositional_variable(PropositionalVariable("q"))
    
    return env
    
def snapshot_env_keys(env: Environment) -> dict:
    return {
        "id": id(env),
        "variables": set(env.local_variables.keys()),
        "dummies": set(env.local_dummy_variables.keys()),
        "metas": set(env.local_meta_variables.keys()),
        "props": set(env.local_propositional_variables.keys()),
        "terms": set(env.local_terms.keys()),
        "formulae": set(env.local_formulae.keys()),
        "theorems": set(env.local_theorems),
        "user_functions": set(env.local_user_functions.keys()),
        "user_relations": set(env.local_user_relations.keys())
    }

from RecycleBinManager import RecycleBinManager

def main():
    # Ensure directories exist
    os.makedirs("save_files", exist_ok=True)
    os.makedirs("history_files", exist_ok=True)

    print("Interactive Theorem Prover REPL")
    print("Available formal theories: ZFC, NT (Number Theory)")
    try:
        theory = input("Choose theory (default ZFC): ").strip().upper()
        if theory not in ["ZFC", "NT"]:
            theory = "ZFC"
    except (KeyboardInterrupt, EOFError):
        theory = "ZFC"
    
    env = get_default_env(theory=theory)
    print(f"Started session in {theory} theory.")
    print("Enter a command or 'exit' to quit. Use 'show' to view the environment.")
    
    # Ask user whether to enable foundational proof logging
    try:
        want_log = input("Enable foundational proof logging to proofs.html? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        want_log = "n"
    if want_log == "y":
        proof_logger.open("proofs.html")
        print("Proof logging enabled. Steps will be written to proofs.html.")
    else:
        print("Proof logging disabled.")
    
    rb = RecycleBinManager(swap_dir="swap_files_cli")
    
    import atexit
    atexit.register(proof_logger.close)
    atexit.register(rb.cleanup)
    rb.cleanup()
    command_queue = []
    
    while True:
        # Reset error flag
        global has_error
        has_error = False
        
        depth = 0
        curr = env
        while curr.parent is not None:
            depth += 1
            curr = curr.parent
        prompt_str = f"ITP {depth}> "

        is_from_queue = False
        if command_queue:
            line = command_queue.pop(0)
            print(f"{prompt_str}{line}")
            is_from_queue = True
        else:
            try:
                line = input(f"\n{prompt_str}").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting. Goodbye!")
                sys.exit(0)
            
        if not line:
            continue
        parts = line.split(maxsplit=1)
        cmd = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        if cmd == "undo":
            success, env, msg = rb.undo(env)
            print(msg)
            continue
            
        if cmd == "redo":
            success, env, msg = rb.redo(env)
            print(msg)
            continue
            
        if cmd == "rb_stat":
            print(rb.stat())
            continue
            
        if cmd == "rb_empty":
            sub_args = args_str.split()
            target = sub_args[0] if len(sub_args) > 0 else "all"
            try:
                count = int(sub_args[1]) if len(sub_args) > 1 else None
            except ValueError:
                print("Error: Count must be an integer.")
                continue
            print(rb.empty(target, count))
            continue
            
        if cmd == "rb_swap":
            sub_args = args_str.split()
            if len(sub_args) < 2:
                print("Error: Usage: rb_swap <perm|temp> <count>")
                continue
            target = sub_args[0]
            try:
                count = int(sub_args[1])
            except ValueError:
                print("Error: Count must be an integer.")
                continue
            print(rb.swap(target, count))
            continue
            
        rb.truncate_history_if_needed(cmd)
        
        from RecycleBinManager import snapshot_env_keys
        old_env_ref = env
        before_snapshot = snapshot_env_keys(env)
        mission_entered = False
        mission_resolved = False
        
        # Dispatch the command via registry
        from CommandHandlers.CommandRegistry import registry
        
        # Check if the command is registered
        if registry.is_registered(cmd):
            # Command arguments passed to the handlers are just the remainder string
            # Handlers will lex() it internally.
            inputs_collected = []
            kwargs = {
                "command_queue": command_queue,
                "inputs_collected": inputs_collected
            }
            if cmd in {"load", "load_h"}:
                kwargs["get_default_env"] = get_default_env
            if cmd in {"save_h", "load_h"}:
                kwargs["history_commands"] = rb.history_commands
                
            new_env = registry.dispatch(cmd, env, args_str, **kwargs)
            if new_env is not None and isinstance(new_env, Environment):
                env = new_env
                
            if cmd in {"load", "load_h"} and not has_error:
                rb.history_commands.clear()
                rb.permanent_recycle_bin.clear()
                rb.temporary_recycle_bin.clear()
                rb.history_pointer = None
                rb.cleanup()
        else:
            print(f"Unknown command '{cmd}'. Supported commands: " + ", ".join(sorted(registry.handlers.keys())))

        # Record command in history if it succeeded and was entered by the user
        if not is_from_queue and not has_error:
            if cmd not in {"exit", "load", "load_h", "save", "save_h", "help", "guide", "rb_stat", "rb_empty", "rb_swap"}:
                if inputs_collected:
                    line = line + "\n" + "\n".join(inputs_collected)
                rb.record_command(line, before_snapshot, old_env_ref, env, mission_entered, mission_resolved)

        # Check if the goal in the current child environment is proven
        while env.goal_formula_name is not None and env.goal_formula_name in env.theorems:
            # Guard for 'and' environments: BOTH Ψ (goal_formula_name) AND Φ (and_right) must
            # be proven before closing the conjunction. This prevents premature closure if the
            # user exits the grandchild (abandoning Φ) and then proves Ψ directly.
            and_right = getattr(env, "and_right_formula_name", None)
            if and_right is not None and and_right not in env.theorems:
                break  # Φ not yet proven; cannot close the conjunction

            goal_name = env.goal_formula_name
            original_goal_name = getattr(env, "original_goal_formula_name", goal_name)
            print(f"\nGoal statement '{goal_name}' is proven!")

            goal_node = env.theorems[goal_name]
            parent = env.parent

            # Read the proof annotation stored by the tactic command
            pa = getattr(env, "proof_annotation", None)

            # If this is a contra child environment, register the target formula f1 in the parent
            if getattr(env, "target_proven_formula_name", None):
                target_name = env.target_proven_formula_name
                parent.theorems[target_name] = clone_ast(parent.formulae[target_name])
                print(f"Target formula '{target_name}' has been successfully proven in parent environment via contradiction!")
                # Log: contradiction elimination (PC2: {¬P, ¬Q∧Q} ⊢ P)
                if pa and pa.get("method") == "contradiction-elim":
                    proof_logger.log(
                        [
                            (pa["assumption_name"], pa["assumption_node"]),
                            (pa["contradiction_name"], env.theorems.get(pa["contradiction_name"], pa["contradiction_node"])),
                        ],
                        target_name, parent.formulae[target_name],
                        "rule: PC2 (contradiction-elim)"
                    )
                else:
                    proof_logger.log_summary(target_name, parent.formulae[target_name], "contradiction-elim")
            elif and_right is not None:
                # 'and' environment: both Ψ and Φ proven → register the original conjunction in parent
                print(f"Both parts proven (Ψ='{goal_name}', Φ='{and_right}'). "
                      f"Conjunction goal '{original_goal_name}' is proven!")
                if original_goal_name in parent.formulae:
                    parent.theorems[original_goal_name] = clone_ast(parent.formulae[original_goal_name])
                else:
                    # conjunction was defined inside the child — carry the node up
                    parent.theorems[original_goal_name] = clone_ast(env.formulae[original_goal_name])
                # Log: conjunction introduction (PC2: {Ψ, Φ} ⊢ Ψ∧Φ)
                conj_node = parent.theorems[original_goal_name]
                if pa and pa.get("method") == "∧-intro":
                    proof_logger.log(
                        [
                            (pa["left_name"], env.theorems.get(pa["left_name"], pa["left_node"])),
                            (pa["right_name"], env.theorems.get(pa["right_name"], pa["right_node"])),
                        ],
                        original_goal_name, conj_node,
                        "rule: PC2 (∧-intro)"
                    )
                else:
                    proof_logger.log_summary(original_goal_name, conj_node, "∧-intro")
            else:
                # Normal mission / left / right: register the (possibly reduced) goal in the parent.
                parent.theorems[goal_name] = clone_ast(goal_node)
                if original_goal_name != goal_name and original_goal_name in parent.formulae:
                    parent.theorems[original_goal_name] = clone_ast(parent.formulae[original_goal_name])
                    print(f"Original mission goal '{original_goal_name}' is also proven in parent environment.")

                # Emit proof log line for this closure based on tactic annotation
                if pa is not None:
                    method = pa.get("method", "")
                    orig_node = parent.theorems.get(original_goal_name, goal_node)

                    if method == "⇒-intro":
                        # imply: {f2: Ψ, f1: Φ} ⊢ goal: Ψ⇒Φ  (rule: PC2)
                        conseq_node = env.theorems.get(pa["consequent_name"], pa["consequent_node"])
                        proof_logger.log(
                            [
                                (pa["assumption_name"], pa["assumption_node"]),
                                (pa["consequent_name"], conseq_node),
                            ],
                            original_goal_name, orig_node,
                            "rule: PC2 (⇒-intro)"
                        )
                    elif method == "∀-intro":
                        # intro ∀: {f1: Ψ(v)} ⊢ original_goal: ∀x Ψ(x)  (rule: QR1)
                        body_node = env.theorems.get(pa["body_name"], pa["body_node"])
                        proof_logger.log(
                            [(pa["body_name"], body_node)],
                            original_goal_name, orig_node,
                            f"rule: QR1 (∀-intro, fresh-var: {pa['fresh_var']})"
                        )
                    elif method == "∃-intro":
                        # intro ∃: {f1: Ψ(t1)} ⊢ original_goal: ∃x Ψ(x)  (axiom: Q2)
                        body_node = env.theorems.get(pa["body_name"], pa["body_node"])
                        proof_logger.log(
                            [(pa["body_name"], body_node)],
                            original_goal_name, orig_node,
                            f"axiom: Q2 (∃-intro, witness: {pa['witness_name']})"
                        )
                    elif method in ("∨-intro-left", "∨-intro-right"):
                        # left/right: {f1: Φ} ⊢ original_goal: Φ∨Ψ  (rule: PC2)
                        disj_node = env.theorems.get(pa["disjunct_name"], pa["disjunct_node"])
                        proof_logger.log(
                            [(pa["disjunct_name"], disj_node)],
                            original_goal_name, orig_node,
                            f"rule: PC2 ({method})"
                        )
                    elif method == "rule: QR1" or method == "rule: QR2":
                        # apply2: {f1: premise} ⊢ original_goal  (rule: QR1/QR2)
                        rule = pa.get("rule", method)
                        reduced_node = env.theorems.get(pa["reduced_goal_name"], pa["reduced_goal_node"])
                        proof_logger.log(
                            [(pa["reduced_goal_name"], reduced_node)],
                            original_goal_name, orig_node,
                            f"rule: {rule}"
                        )
                    elif method == "modus-ponens":
                        # apply3: {f1: Ψ⇒Φ, f2: Ψ} ⊢ goal: Φ  (rule: PC2)
                        impl_node = env.theorems.get(pa["impl_name"], pa["impl_node"])
                        ant_node = env.theorems.get(pa["antecedent_name"], pa["antecedent_node"])
                        proof_logger.log(
                            [
                                (pa["impl_name"], impl_node),
                                (pa["antecedent_name"], ant_node),
                            ],
                            original_goal_name, orig_node,
                            "rule: PC2 (modus-ponens)"
                        )
                    else:
                        proof_logger.log_summary(original_goal_name, orig_node, method or "tactic-proof")
                # else: no annotation means the proof was done by a direct command (already logged)

            # Destroy the child environment and restore the parent
            env = parent
            print(f"Child environment destroyed. Returned to parent environment.")


if __name__ == "__main__":
    main()
