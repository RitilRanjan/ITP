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
    handle_def_f, handle_def_r, handle_iota, handle_epsilon
)
from CommandHandlers.state_handlers import (
    handle_show, handle_help, handle_save, handle_load, handle_save_h, handle_load_h,
    handle_auto, handle_search, handle_backward_search, handle_advanced_search, handle_dt
)
from CommandHandlers.transformation_handlers import (
    handle_fold, handle_simp, handle_neg
)
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
    Relation, RelationType, Quantifier, Connective, MetaVariable
)
from Frontend import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError, lex
)
from SubstitutionManager import (
    substitute_free, substitute_bound, substitute_all, substitute_term, substitute_proposition,
    is_substitutable_free, is_substitutable_bound, clone_ast, get_term_vars
)
from StorageManager import (
    save_environment_state, load_environment_state, save_history, load_history
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
    expand_epsilon_function_in_formula, expand_iota_function_in_formula,
    VariableCaptureError
)

def get_default_env() -> Environment:
    """Initializes the environment with default testing data."""
    env = Environment()
    
    # Pre-defined variables
    env.add_variable(Variable(name="x"))
    env.add_variable(Variable(name="y"))
    
    # Pre-defined function symbol S (successor, arity 1)
    # Satisfies arity with a dummy variable argument
    dummy = Variable("x")
    env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    
    # Pre-defined function symbol + (arity 2)
    env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    # Pre-defined relation symbol = (equality, arity 2)
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    # Pre-defined relation symbol ∈ (membership, arity 2)
    env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    
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

def compute_env_delta(before: dict, after: dict) -> dict:
    delta = {"added": {}, "removed": {}}
    for k in before.keys():
        if k == "id":
            continue
        added = after[k] - before[k]
        removed = before[k] - after[k]
        if added:
            delta["added"][k] = added
        if removed:
            delta["removed"][k] = removed
    return delta

import uuid
import pickle
import shutil

class SwapRef:
    def __init__(self, obj):
        os.makedirs("swap_files", exist_ok=True)
        self.filename = os.path.join("swap_files", f"swap_{uuid.uuid4().hex}.pkl")
        with open(self.filename, "wb") as f:
            pickle.dump(obj, f)
            
    def load(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Swap file {self.filename} missing.")
        with open(self.filename, "rb") as f:
            obj = pickle.load(f)
        os.remove(self.filename)
        return obj
        
    def delete(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

def cleanup_swap_files():
    if os.path.exists("swap_files"):
        shutil.rmtree("swap_files", ignore_errors=True)

def main():
    # Ensure directories exist
    os.makedirs("save_files", exist_ok=True)
    os.makedirs("history_files", exist_ok=True)

    env = get_default_env()
    print("Interactive Theorem Prover REPL")
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
    
    import atexit
    atexit.register(proof_logger.close)
    atexit.register(cleanup_swap_files)
    # Wipe swap files on start just in case previous session crashed
    cleanup_swap_files()
    
    history_commands = [] # List of tuples (line, delta)
    permanent_recycle_bin = []
    temporary_recycle_bin = []
    history_pointer = None
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
            if not history_commands:
                print("Error: Nothing to undo.")
                continue
            if history_pointer is None:
                history_pointer = len(history_commands) - 1
            elif history_pointer < 0:
                print("Error: Already at the oldest command. Nothing more to undo.")
                continue
                
            line_str, delta = history_commands[history_pointer]
            
            # 1. Added objects -> Temporary recycle bin
            undone_added = {}
            for k, names in delta.get("added", {}).items():
                if k == "theorems":
                    undone_added[k] = set()
                    for name in names:
                        if name in env.local_theorems:
                            env.local_theorems.remove(name)
                            undone_added[k].add(name)
                else:
                    undone_added[k] = {}
                    dict_ref = getattr(env, f"local_{k}")
                    for name in names:
                        if name in dict_ref:
                            undone_added[k][name] = dict_ref.pop(name)
                        
            # 2. Revert mission entries/resolves
            if delta.get("mission_entered"):
                undone_added["child_env"] = env
                env = env.parent
            elif delta.get("mission_resolved"):
                if not permanent_recycle_bin:
                    print("Error: Memory wiped. The required objects were permanently deleted from the permanent recycle bin.")
                    continue
                perm_item = permanent_recycle_bin.pop()
                if isinstance(perm_item, SwapRef): perm_item = perm_item.load()
                env = perm_item["closed_env"]
            
            # 3. Restored objects -> Pop from Permanent recycle bin
            if "removed_objects" in delta:
                if not delta.get("mission_resolved"):
                    if not permanent_recycle_bin:
                        print("Error: Memory wiped. The required objects were permanently deleted from the permanent recycle bin.")
                        continue
                    perm_item = permanent_recycle_bin.pop()
                    if isinstance(perm_item, SwapRef): perm_item = perm_item.load()
                removed_objects = perm_item["removed_objects"]
                for k, objs in removed_objects.items():
                    if k == "theorems":
                        env.local_theorems.update(objs)
                    else:
                        dict_ref = getattr(env, f"local_{k}")
                        dict_ref.update(objs)
            
            # Push to temporary recycle bin
            # Always append an item to keep the stacks synced, even if empty
            temporary_recycle_bin.append(undone_added)
                
            history_pointer -= 1
            print(f"Undid: {line_str}")
            continue
            
        if cmd == "redo":
            if not history_commands:
                print("Error: Nothing to redo.")
                continue
            if history_pointer is None or history_pointer == len(history_commands) - 1:
                print("Error: Already at the newest command. Nothing more to redo.")
                continue
                
            if not temporary_recycle_bin:
                print("Error: Memory wiped. The required objects were deleted from the temporary recycle bin.")
                continue
                
            history_pointer += 1
            line_str, delta = history_commands[history_pointer]
            
            undone_added = temporary_recycle_bin.pop()
            if isinstance(undone_added, SwapRef): undone_added = undone_added.load()
            
            # 1. Restore added objects from temporary recycle bin
            for k, objs in undone_added.items():
                if k == "child_env":
                    continue
                if k == "theorems":
                    env.local_theorems.update(objs)
                else:
                    dict_ref = getattr(env, f"local_{k}")
                    dict_ref.update(objs)
            
            # 2. Re-apply mission entries/resolves
            if delta.get("mission_entered"):
                env = undone_added["child_env"]
            elif delta.get("mission_resolved"):
                closed_env = env
                env = env.parent
                
            # 3. Remove objects and push to permanent recycle bin
            if "removed_objects" in delta or delta.get("mission_resolved"):
                perm_item = {}
                if delta.get("mission_resolved"):
                    perm_item["closed_env"] = closed_env
                if "removed_objects" in delta:
                    removed_objects = {}
                    for k, names in delta.get("removed", {}).items():
                        if k == "theorems":
                            removed_objects[k] = set()
                            for name in names:
                                if name in env.local_theorems:
                                    env.local_theorems.remove(name)
                                    removed_objects[k].add(name)
                        else:
                            removed_objects[k] = {}
                            dict_ref = getattr(env, f"local_{k}")
                            for name in names:
                                if name in dict_ref:
                                    removed_objects[k][name] = dict_ref.pop(name)
                    perm_item["removed_objects"] = removed_objects
                permanent_recycle_bin.append(perm_item)
                
            print(f"Redid: {line_str}")
            
            # If we reached the end, reset pointer
            if history_pointer == len(history_commands) - 1:
                history_pointer = None
            continue
            
        if cmd == "rb_stat":
            perm_count = sum(len(item.get("removed_objects", {})) + (1 if item.get("closed_env") else 0) for item in permanent_recycle_bin)
            temp_count = sum(len(item) for item in temporary_recycle_bin)
            print(f"Recycle Bin Status:")
            print(f"  Permanent Bin: {perm_count} operations containing deleted objects/environments.")
            print(f"  Temporary Bin: {temp_count} operations containing undone created objects.")
            continue
            
        if cmd == "rb_empty":
            sub_args = args_str.split()
            target = sub_args[0] if len(sub_args) > 0 else "all"
            try:
                count = int(sub_args[1]) if len(sub_args) > 1 else None
            except ValueError:
                print("Error: Count must be an integer.")
                continue
            
            def clear_bin(bin_list, c):
                if c is None or c >= len(bin_list):
                    for item in bin_list:
                        if isinstance(item, SwapRef): item.delete()
                    bin_list.clear()
                else:
                    for item in bin_list[:c]:
                        if isinstance(item, SwapRef): item.delete()
                    del bin_list[:c]
                    
            if target in {"all", "perm"}: clear_bin(permanent_recycle_bin, count)
            if target in {"all", "temp"}: clear_bin(temporary_recycle_bin, count)
            
            print(f"Recycle bins emptied successfully ({target}{' ' + str(count) if count else ''}).")
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
                
            target_bin = permanent_recycle_bin if target == "perm" else (temporary_recycle_bin if target == "temp" else None)
            if target_bin is None:
                print("Error: Target must be 'perm' or 'temp'.")
                continue
                
            swapped = 0
            for i in range(min(count, len(target_bin))):
                if not isinstance(target_bin[i], SwapRef):
                    target_bin[i] = SwapRef(target_bin[i])
                    swapped += 1
            print(f"Successfully swapped {swapped} items from {target} bin to disk.")
            continue
            
        # If a normal command is executed while pointer is active, truncate history
        if history_pointer is not None and cmd not in {"save", "save_h", "load", "load_h", "help", "guide"}:
            history_commands = history_commands[:history_pointer + 1]
            temporary_recycle_bin.clear()
            history_pointer = None
            
        # Snapshot before command
        env_before = snapshot_env_keys(env)
        old_env_ref = env
        
        # Dispatch the command via registry
        from CommandHandlers.CommandRegistry import registry
        
        # Check if the command is registered
        if registry.is_registered(cmd):
            # Command arguments passed to the handlers are just the remainder string
            # Handlers will lex() it internally.
            inputs_collected = []
            kwargs = {
                "get_default_env": get_default_env,
                "history_commands": history_commands,
                "command_queue": command_queue,
                "inputs_collected": inputs_collected
            }
            new_env = registry.dispatch(cmd, env, args_str, **kwargs)
            if new_env is not None and isinstance(new_env, Environment):
                env = new_env
                
            if cmd in {"load", "load_h"} and not has_error:
                history_commands.clear()
                permanent_recycle_bin.clear()
                temporary_recycle_bin.clear()
                history_pointer = None
                cleanup_swap_files()
        else:
            print(f"Unknown command '{cmd}'. Supported commands: " + ", ".join(sorted(registry.handlers.keys())))

        # Record command in history if it succeeded and was entered by the user
        if not is_from_queue and not has_error:
            if cmd not in {"exit", "load", "load_h", "save", "save_h", "help", "guide"}:
                env_after = snapshot_env_keys(env)
                delta = compute_env_delta(env_before, env_after)
                
                # Extract actual removed objects from old_env_ref and store them in the delta
                # so we can push them to the permanent recycle bin
                removed_objects = {}
                for k, names in delta.get("removed", {}).items():
                    if k == "theorems":
                        removed_objects[k] = set(names)
                    else:
                        removed_objects[k] = {}
                        dict_ref = getattr(old_env_ref, f"local_{k}", {})
                        for name in names:
                            if name in dict_ref:
                                removed_objects[k][name] = dict_ref[name]
                
                if removed_objects:
                    delta["removed_objects"] = removed_objects
                
                closed_env = None
                
                # Check for closed mission / entered mission
                if env_before["id"] != env_after["id"]:
                    if getattr(env, "parent", None) and id(env.parent) == env_before["id"]:
                        delta["mission_entered"] = True
                    else:
                        delta["mission_resolved"] = True
                        closed_env = old_env_ref
                        delta["closed_env"] = closed_env
                
                # Push removed items / closed environments to the permanent recycle bin
                if removed_objects or closed_env:
                    permanent_recycle_bin.append({
                        "removed_objects": removed_objects,
                        "closed_env": closed_env
                    })
                
                if inputs_collected:
                    line = line + "\n" + "\n".join(inputs_collected)
                
                history_commands.append((line, delta))

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
