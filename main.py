import sys
import os
import builtins
from typing import Optional
from Environment import Environment
from AST import (
    Variable, DummyVariable, PropositionalVariable, Function, FunctionType,
    Relation, RelationType, Quantifier, Connective, MetaVariable
)
from Frontend import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError
)
from SubstitutionManager import (
    substitute_free, substitute_bound, substitute_all, substitute_term, substitute_proposition,
    is_substitutable_free, is_substitutable_bound, clone_ast
)
from StorageManager import (
    save_environment_state, load_environment_state, save_history, load_history
)
from AutoProver import auto_prove

# Global flag to track if the current command resulted in an error or warning
has_error = False
_original_print = builtins.print

def print(*args, **kwargs):
    global has_error
    msg = " ".join(str(x) for x in args)
    if msg.startswith("Error:") or msg.startswith("Parser Error:") or msg.startswith("Warning:"):
        has_error = True
    _original_print(*args, **kwargs)

from DeductiveSystem import (
    axiom_E1, axiom_E2, axiom_E3, axiom_Q1, axiom_Q2,
    rule_QR1, rule_QR2, rule_PC1, rule_PC2
)
from ZFC_Rules import (
    axiom_extension, axiom_pairing, axiom_union, axiom_power_set,
    axiom_regularity, axiom_infinity, axiom_choice, axiom_specification,
    axiom_replacement
)
from DefinitionExpander import (
    expand_user_defined_function_in_term,
    expand_user_defined_function_in_formula,
    expand_user_defined_relation_in_formula,
    expand_existential_in_formula,
    expand_unique_existential_in_formula,
    expand_iota_function_in_formula
)

AXIOMS = {
    # Logical Axioms
    "E1": axiom_E1,
    "E2": axiom_E2,
    "E3": axiom_E3,
    "Q1": axiom_Q1,
    "Q2": axiom_Q2,
    # ZFC Axioms
    "extension": axiom_extension,
    "pairing": axiom_pairing,
    "union": axiom_union,
    "power_set": axiom_power_set,
    "regularity": axiom_regularity,
    "infinity": axiom_infinity,
    "choice": axiom_choice,
    "specification": axiom_specification,
    "replacement": axiom_replacement,
}

RULES = {
    "QR1": rule_QR1,
    "QR2": rule_QR2,
    "PC1": rule_PC1,
    "PC2": rule_PC2,
}

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

def show_environment(env: Environment):
    """Prints a simplified, human-readable view of the environment objects for all environments in the chain."""
    # Collect all environments from ground to current active
    chain = []
    curr = env
    while curr is not None:
        chain.append(curr)
        curr = curr.parent
    chain.reverse()
    
    for e in chain:
        print("\n" + "=" * 40)
        if e.parent is None:
            header = " GROUND ENVIRONMENT "
        else:
            header = f" CHILD ENVIRONMENT (Goal: {e.goal_formula_name}) "
        print(header.center(40, "="))
        print("=" * 40)
        
        # 1. Variables
        vars_str = ", ".join(e.local_variables.keys()) if e.local_variables else "None"
        print(f"Variables: {vars_str}")
        
        # 2. Dummy Variables
        dummy_str = ", ".join(e.local_dummy_variables.keys()) if e.local_dummy_variables else "None"
        print(f"Dummy Variables: {dummy_str}")
        
        # 3. Meta Variables
        meta_str = ", ".join(e.local_meta_variables.keys()) if e.local_meta_variables else "None"
        print(f"Meta Variables: {meta_str}")
        
        # 4. Propositional Variables
        prop_vars_str = ", ".join(e.local_propositional_variables.keys()) if e.local_propositional_variables else "None"
        print(f"Propositional Variables: {prop_vars_str}")
        
        # 5. Functions (symbol declarations)
        funcs = []
        for k, v in e.local_terms.items():
            if isinstance(v, Function) and k == v.name:
                if k in e.local_user_functions:
                    arity, df = e.local_user_functions[k]
                    funcs.append(f"{k} {arity} = {reconstruct_string(df)}")
                else:
                    funcs.append(f"{k} {v.arity}")
        funcs_str = ", ".join(funcs) if funcs else "None"
        print(f"Functions: {funcs_str}")
        
        # 6. Relations (symbol declarations)
        rels = []
        for k, v in e.local_formulae.items():
            if isinstance(v, Relation) and k == v.name:
                if k in e.local_user_relations:
                    arity, df = e.local_user_relations[k]
                    rels.append(f"{k} {arity} ⇔ {reconstruct_string(df)}")
                else:
                    rels.append(f"{k} {v.arity}")
        rels_str = ", ".join(rels) if rels else "None"
        print(f"Relations: {rels_str}")
        
        # 7. Terms (user-registered terms)
        print("\nTerms:")
        terms = []
        for k, v in e.local_terms.items():
            if not (isinstance(v, Function) and k == v.name):
                terms.append(f"  {k}: {reconstruct_string(v)}")
        if terms:
            for t in terms:
                print(t)
        else:
            print("  None")
            
        # 8. Formulae (user-registered formulae)
        print("\nFormulae:")
        formulae = []
        for k, v in e.local_formulae.items():
            if not (isinstance(v, Relation) and k == v.name):
                formulae.append(f"  {k}: {reconstruct_string(v)}")
        if formulae:
            for f in formulae:
                print(f)
        else:
            print("  None")
            
        # 9. Proven Theorems
        print("\nProven Theorems:")
        theorems = []
        for k, v in e.local_theorems.items():
            theorems.append(f"  {k}: {reconstruct_string(v)}")
        if theorems:
            for th in theorems:
                print(th)
        else:
            print("  None")
        print("=" * 40)

def validate_new_name(env, name: str, allowed_category: Optional[str] = None) -> bool:
    if name.startswith("_"):
        if allowed_category != "dummy_variable":
            print("Error: Names starting with '_' are reserved for dummy variables only.")
            return False
    if name.startswith("?"):
        if allowed_category != "meta_variable":
            print("Error: Names starting with '?' are reserved for meta variables only.")
            return False
            
    clash = False
    if allowed_category != "variable" and name in env.variables:
        clash = True
    if allowed_category != "dummy_variable" and name in env.dummy_variables:
        clash = True
    if allowed_category != "meta_variable" and name in env.meta_variables:
        clash = True
    if allowed_category != "term" and name in env.terms:
        clash = True
    if allowed_category != "propositional_variable" and name in env.propositional_variables:
        clash = True
    if allowed_category != "formula" and name in env.formulae:
        clash = True
        
    if clash:
        print(f"Error: Name '{name}' is already in use by another environment object.")
        return False
    return True

def main():
    # Ensure directories exist
    os.makedirs("save_files", exist_ok=True)
    os.makedirs("history_files", exist_ok=True)

    env = get_default_env()
    print("Interactive Theorem Prover REPL")
    print("Enter a command or 'exit' to quit. Use 'show' to view the environment.")
    
    history_commands = []
    command_queue = []
    
    while True:
        # Reset error flag
        global has_error
        has_error = False
        
        is_from_queue = False
        if command_queue:
            line = command_queue.pop(0)
            print(f"ITP> {line}")
            is_from_queue = True
        else:
            try:
                line = input("\nITP> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting. Goodbye!")
                sys.exit(0)
            
        if not line:
            continue
        parts = line.split(maxsplit=1)
        cmd = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        if cmd == "exit":
            if env.parent is not None:
                goal_name = env.goal_formula_name
                env = env.parent
                print(f"Terminated child environment for goal '{goal_name}' without proving it. Returned to parent environment.")
                continue
            else:
                print("Goodbye!")
                sys.exit(0)
            
        elif cmd == "show":
            show_environment(env)
            
        elif cmd in {"help", "guide"}:
            print("=" * 60)
            print(" INTERACTIVE THEOREM PROVER COMMAND GUIDE ".center(60, "="))
            print("=" * 60)
            print("\nVariable and Formula Definitions:")
            print("  cv <name>                           - Create standard variable (e.g. cv x)")
            print("  cV <name>                           - Create propositional variable (e.g. cV p)")
            print("  ct <name> <term_expr>               - Create term definition (e.g. ct t1 S x)")
            print("  cf <name> <fol_expr>                - Create FOL formula (e.g. cf f1 ∀x (x = y))")
            print("  cp <name> <prop_expr>               - Create propositional formula (e.g. cp p1 p ∧ q)")
            print("\nSubstitutions:")
            print("  st <term1> <var> <term2> <term3> [idx]  - Substitute term2 for var in term1 to create term3")
            print("  sf <formula1> <var> <term1> <formula2> [idx] - Substitute term1 for free var in formula1 to create formula2")
            print("  sb <formula1> <var> <term1> <formula2> [idx] - Substitute term1 (must be variable) for bound var in formula1 to create formula2")
            print("  sa <formula1> <var> <term1> <formula2> [idx] - Substitute all occurrences of var in formula1 to create formula2")
            print("  sp <p_formula1> <p_var> <p_formula2> <p_formula3> [idx] - Substitute p_formula2 for p_var in p_formula1 to create p_formula3")
            print("\nUser-Defined Symbols:")
            print("  def_f <arity> <F1> <v1> ... <vn> <t1> - Create user-defined function (arity > 2)")
            print("  def_f 2 <v1> <F1> <v2> <t1>         - Create infix user-defined function (arity = 2)")
            print("  def_r <arity> <R1> <v1> ... <vn> <f1> - Create user-defined relation (arity > 2)")
            print("  def_r 2 <v1> <R1> <v2> <f1>         - Create infix user-defined relation (arity = 2)")
            print("  iota <F1> <f1>                      - Define iota function F1 from unique existence theorem f1")
            print("\nDefinition Expansion / Folding:")
            print("  fold ∃ <occurrence> <formula> <output> [f3]")
            print("  fold ∃! <occurrence> <formula> <y> <output> [f3]")
            print("  fold <symbol> <occurrence> <input> [args...] <output> [f3]")
            print("\nProofs and Inference:")
            print("  ua <axiom> <formula>                - Prove formula using logical/ZFC axiom (e.g. ua E1 f1)")
            print("  ir <rule> <conclusion> [premises]   - Prove conclusion using rule and premises (e.g. ir PC1 f2 f1)")
            print("  dt <theorem>                        - Delete a proven theorem from environment")
            print("  auto <formula>                      - Attempt to prove formula automatically using axioms & rules")
            print("  (Axioms: E1, E2, E3, Q1, Q2, extension, pairing, union, power_set, regularity, infinity, choice, specification, replacement)")
            print("  (Rules: QR1, QR2, PC1, PC2)")
            print("\nNested Environments:")
            print("  mission <formula>                   - Enter child environment to prove formula")
            print("  exit                                - Leave child environment or exit program")
            print("\nState and History Management:")
            print("  help / guide                        - Show this help message")
            print("  save                                - Save current environment states to save_files/")
            print("  load                                - Load saved environment states from save_files/")
            print("  save_h                              - Save command history to history_files/")
            print("  load_h                              - Load and execute commands from history_files/")
            print("\nOther:")
            print("  show                                - View the current environment stack")
            print("=" * 60)

        elif cmd == "save":
            try:
                name = input("Enter filename: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                continue
            if not name:
                print("Error: Filename cannot be empty.")
                continue
            filepath = os.path.join("save_files", name)
            if os.path.exists(filepath):
                print("Error: A save file with that name already exists.")
                continue
            try:
                save_environment_state(env, filepath)
                print(f"Saved state to '{filepath}'")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "load":
            try:
                name = input("Enter filename to load: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                continue
            if not name:
                print("Error: Filename cannot be empty.")
                continue
            filepath = os.path.join("save_files", name)
            if not os.path.exists(filepath):
                print(f"Error: Save file '{filepath}' not found.")
                continue
            try:
                env = load_environment_state(filepath, get_default_env)
                print(f"Loaded state from '{filepath}'")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "save_h":
            try:
                name = input("Enter filename: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                continue
            if not name:
                print("Error: Filename cannot be empty.")
                continue
            filepath = os.path.join("history_files", name)
            if os.path.exists(filepath):
                print("Error: A history file with that name already exists.")
                continue
            try:
                save_history(history_commands, filepath)
                print(f"Saved history to '{filepath}'")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "load_h":
            try:
                name = input("Enter filename to load: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                continue
            if not name:
                print("Error: Filename cannot be empty.")
                continue
            filepath = os.path.join("history_files", name)
            if not os.path.exists(filepath):
                print(f"Error: History file '{filepath}' not found.")
                continue
            try:
                cmds = load_history(filepath)
                history_commands.clear()
                command_queue.extend(cmds)
                print(f"Loaded history from '{filepath}'. Replaying {len(cmds)} commands...")
            except Exception as e:
                print(f"Error: {e}")
            
        elif cmd == "auto":
            cmd_args = args_str.split()
            if len(cmd_args) < 1:
                print("Error: Usage: auto <formula>")
                continue
            f1_name = cmd_args[0]
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found.")
                continue
            
            try:
                success = auto_prove(f1_name, env)
                if success:
                    print(f"Formula '{f1_name}' has been successfully proven automatically!")
                else:
                    print(f"Failed to prove formula '{f1_name}' automatically.")
            except Exception as e:
                print(f"Error during auto proof: {e}")

        elif cmd == "mission":
            cmd_args = args_str.split()
            if len(cmd_args) < 1:
                print("Error: Usage: mission <formula>")
                continue
            f1_name = cmd_args[0]
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found.")
                continue
            if f1_name in env.theorems:
                print(f"Error: Goal '{f1_name}' is already proven.")
                continue
            # Also check if any existing theorem has the exact same formula
            goal_node = env.formulae[f1_name]
            already_proven = False
            for k, v in env.theorems.items():
                if v.is_structurally_equal(goal_node):
                    already_proven = True
                    break
            if already_proven:
                print(f"Error: Goal '{f1_name}' (or a structurally identical formula) is already proven.")
                continue
            
            env = Environment(parent=env, goal_formula_name=f1_name)
            print(f"Entered child environment for goal '{f1_name}'.")
            
        elif cmd == "cv":
            if not args_str:
                print("Error: Missing variable name.")
                continue
            name = args_str.strip()
            if not validate_new_name(env, name, "variable"):
                continue
            try:
                env.add_variable(Variable(name=name))
                print(f"Created standard variable '{name}'")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "cV":
            if not args_str:
                print("Error: Missing propositional variable name.")
                continue
            name = args_str.strip()
            if not validate_new_name(env, name, "propositional_variable"):
                continue
            try:
                env.add_propositional_variable(PropositionalVariable(name=name))
                print(f"Created propositional variable '{name}'")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "ct":
            sub_parts = args_str.split(maxsplit=1)
            if len(sub_parts) < 2:
                print("Error: Usage: ct <name> <definition>")
                continue
            name = sub_parts[0]
            expr = sub_parts[1]
            if not validate_new_name(env, name, "term"):
                continue
            try:
                ast = parse_term(expr, env)
                env.terms[name] = ast
                print(f"Created term '{name}' = '{reconstruct_string(ast)}'")
            except (UnrecognizedSymbolError, ParserError) as pe:
                print(f"Parser Error: {pe}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "cf":
            sub_parts = args_str.split(maxsplit=1)
            if len(sub_parts) < 2:
                print("Error: Usage: cf <name> <definition>")
                continue
            name = sub_parts[0]
            expr = sub_parts[1]
            if not validate_new_name(env, name, "formula"):
                continue
            try:
                ast = parse_fol_formula(expr, env)
                env.formulae[name] = ast
                print(f"Created formula '{name}' = '{reconstruct_string(ast)}'")
            except (UnrecognizedSymbolError, ParserError) as pe:
                print(f"Parser Error: {pe}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "cp":
            sub_parts = args_str.split(maxsplit=1)
            if len(sub_parts) < 2:
                print("Error: Usage: cp <name> <definition>")
                continue
            name = sub_parts[0]
            expr = sub_parts[1]
            if not validate_new_name(env, name, "formula"):
                continue
            try:
                ast = parse_prop_formula(expr, env)
                env.formulae[name] = ast
                print(f"Created propositional formula '{name}' = '{reconstruct_string(ast)}'")
            except (UnrecognizedSymbolError, ParserError) as pe:
                print(f"Parser Error: {pe}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "st":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: st <term1> <var> <term2> <term3> [index]")
                continue
            t1_name, x, t2_name, t3_name = cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3]
            idx = int(cmd_args[4]) if len(cmd_args) > 4 else None
            
            if t1_name not in env.terms:
                print(f"Error: Term '{t1_name}' not found in environment.")
                continue
            if t2_name not in env.terms:
                print(f"Error: Term '{t2_name}' not found in environment.")
                continue
                
            if not validate_new_name(env, t3_name, "term"):
                continue
                
            t1_clone = clone_ast(env.terms[t1_name])
            t2_clone = clone_ast(env.terms[t2_name])
            
            try:
                substitute_term(t1_clone, x, t2_clone, idx)
                env.terms[t3_name] = t1_clone
                print(f"Created term '{t3_name}' = '{reconstruct_string(t1_clone)}'")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "sf":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: sf <formula1> <var> <term1> <formula2> [index]")
                continue
            f1_name, x, t1_name, f2_name = cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3]
            idx = int(cmd_args[4]) if len(cmd_args) > 4 else None
            
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found in environment.")
                continue
            if t1_name not in env.terms:
                print(f"Error: Term '{t1_name}' not found in environment.")
                continue
                
            if not validate_new_name(env, f2_name, "formula"):
                continue
                
            f1_clone = clone_ast(env.formulae[f1_name])
            t1_clone = clone_ast(env.terms[t1_name])
            
            try:
                subst_valid = is_substitutable_free(x, t1_clone, f1_clone, idx)
                if not subst_valid:
                    print("Warning: This substitution changes the semantic meaning (variable capture occurs).")
                    
                substitute_free(f1_clone, x, t1_clone, idx)
                env.formulae[f2_name] = f1_clone
                print(f"Created formula '{f2_name}' = '{reconstruct_string(f1_clone)}'")
                
                if f1_name in env.theorems and subst_valid:
                    env.theorems[f2_name] = f1_clone
                    print(f"Registered formula '{f2_name}' as a proven theorem.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "sb":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: sb <formula1> <var> <term1> <formula2> [index]")
                continue
            f1_name, x, t1_name, f2_name = cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3]
            idx = int(cmd_args[4]) if len(cmd_args) > 4 else None
            
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found in environment.")
                continue
            if t1_name not in env.terms:
                print(f"Error: Term '{t1_name}' not found in environment.")
                continue
                
            t1_node = env.terms[t1_name]
            if not isinstance(t1_node, Variable):
                print(f"Error: Bound substitution requires the replacement term '{t1_name}' to be a variable.")
                continue
                
            if not validate_new_name(env, f2_name, "formula"):
                continue
                
            f1_clone = clone_ast(env.formulae[f1_name])
            
            try:
                subst_valid = is_substitutable_bound(x, t1_node, f1_clone, idx)
                if not subst_valid:
                    print("Warning: This substitution changes the semantic meaning.")
                    
                substitute_bound(f1_clone, x, t1_node, idx)
                env.formulae[f2_name] = f1_clone
                print(f"Created formula '{f2_name}' = '{reconstruct_string(f1_clone)}'")
                
                if f1_name in env.theorems and subst_valid:
                    env.theorems[f2_name] = f1_clone
                    print(f"Registered formula '{f2_name}' as a proven theorem.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "sa":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: sa <formula1> <var> <term1> <formula2> [index]")
                continue
            f1_name, x, t1_name, f2_name = cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3]
            idx = int(cmd_args[4]) if len(cmd_args) > 4 else None
            
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found in environment.")
                continue
            if t1_name not in env.terms:
                print(f"Error: Term '{t1_name}' not found in environment.")
                continue
                
            if not validate_new_name(env, f2_name, "formula"):
                continue
                
            f1_clone = clone_ast(env.formulae[f1_name])
            t1_clone = clone_ast(env.terms[t1_name])
            
            try:
                from SubstitutionManager import collect_all_occurrences
                subst_valid = is_substitutable_free(x, t1_clone, f1_clone, idx)
                
                occs = collect_all_occurrences(f1_clone)
                has_bound = any(o["node"].name == x and not o["is_free"] for o in occs)
                if has_bound:
                    if not isinstance(t1_clone, Variable):
                        subst_valid = False
                    else:
                        subst_valid = subst_valid and is_substitutable_bound(x, t1_clone, f1_clone, idx)
                        
                if not subst_valid:
                    print("Warning: This substitution changes the semantic meaning.")
                    
                substitute_all(f1_clone, x, t1_clone, idx)
                env.formulae[f2_name] = f1_clone
                print(f"Created formula '{f2_name}' = '{reconstruct_string(f1_clone)}'")
                
                if f1_name in env.theorems and subst_valid:
                    env.theorems[f2_name] = f1_clone
                    print(f"Registered formula '{f2_name}' as a proven theorem.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "sp":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: sp <prop_formula1> <prop_var> <prop_formula2> <prop_formula3> [index]")
                continue
            p1_name, q, p2_name, p3_name = cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3]
            idx = int(cmd_args[4]) if len(cmd_args) > 4 else None
            
            if p1_name not in env.formulae:
                print(f"Error: Propositional formula '{p1_name}' not found in environment.")
                continue
            if p2_name not in env.formulae:
                print(f"Error: Propositional formula '{p2_name}' not found in environment.")
                continue
                
            if not validate_new_name(env, p3_name, "formula"):
                continue
                
            p1_clone = clone_ast(env.formulae[p1_name])
            p2_clone = clone_ast(env.formulae[p2_name])
            
            try:
                substitute_proposition(p1_clone, q, p2_clone, idx)
                env.formulae[p3_name] = p1_clone
                print(f"Created propositional formula '{p3_name}' = '{reconstruct_string(p1_clone)}'")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "ua":
            cmd_args = args_str.split()
            if len(cmd_args) < 2:
                print("Error: Usage: ua <axiom> <formula>")
                continue
            ax_name, f_name = cmd_args[0], cmd_args[1]
            if ax_name not in AXIOMS:
                print(f"Error: Unknown axiom '{ax_name}'. Supported axioms: {', '.join(AXIOMS.keys())}")
                continue
            if f_name not in env.formulae:
                print(f"Error: Formula '{f_name}' not found in environment.")
                continue
            
            formula = env.formulae[f_name]
            axiom_func = AXIOMS[ax_name]
            try:
                if axiom_func(formula):
                    env.theorems[f_name] = clone_ast(formula)
                    print(f"Proven theorem '{f_name}' using axiom {ax_name}.")
                else:
                    print(f"Error: Formula '{f_name}' does not satisfy axiom {ax_name}.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "ir":
            cmd_args = args_str.split()
            if len(cmd_args) < 2:
                print("Error: Usage: ir <rule> <conclusion> [premise1 ... premiseK]")
                continue
            rule_name = cmd_args[0]
            conclusion_name = cmd_args[1]
            premise_names = cmd_args[2:]
            
            if rule_name not in RULES:
                print(f"Error: Unknown inference rule '{rule_name}'. Supported rules: {', '.join(RULES.keys())}")
                continue
            if conclusion_name not in env.formulae:
                print(f"Error: Conclusion formula '{conclusion_name}' not found in environment.")
                continue
            
            # Verify all premises exist in proven theorems
            valid_premises = True
            premise_nodes = []
            for p_name in premise_names:
                if p_name not in env.theorems:
                    print(f"Error: Premise '{p_name}' is not a proven theorem.")
                    valid_premises = False
                    break
                premise_nodes.append(env.theorems[p_name])
                
            if not valid_premises:
                continue
                
            conclusion_node = env.formulae[conclusion_name]
            rule_func = RULES[rule_name]
            try:
                if rule_func(premise_nodes, conclusion_node):
                    env.theorems[conclusion_name] = clone_ast(conclusion_node)
                    print(f"Proven theorem '{conclusion_name}' using rule {rule_name}.")
                else:
                    print(f"Error: Conclusion '{conclusion_name}' does not follow from the premises using rule {rule_name}.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "dt":
            cmd_args = args_str.split()
            if len(cmd_args) < 1:
                print("Error: Usage: dt <theorem>")
                continue
            th_name = cmd_args[0]
            if th_name not in env.theorems:
                print(f"Error: Theorem '{th_name}' not found in proven theorems.")
                continue
            env.remove_theorem(th_name)
            print(f"Deleted proven theorem '{th_name}'.")
            
        elif cmd == "def_f":
            cmd_args = args_str.split()
            if len(cmd_args) < 3:
                print("Error: Usage: def_f n F1 v1 v2 ... vn t1 (infix: def_f 2 v1 F1 v2 t1)")
                continue
            try:
                arity = int(cmd_args[0])
            except ValueError:
                print("Error: Arity must be an integer.")
                continue

            if arity == 2:
                if len(cmd_args) != 5:
                    print("Error: Usage for arity 2: def_f 2 v1 F1 v2 t1")
                    continue
                v1_name, f_name, v2_name, t1_name = cmd_args[1], cmd_args[2], cmd_args[3], cmd_args[4]
                variables = [v1_name, v2_name]
            else:
                if len(cmd_args) != arity + 3:
                    print(f"Error: Usage for arity {arity}: def_f {arity} F1 v1 v2 ... v{arity} t1")
                    continue
                f_name = cmd_args[1]
                variables = cmd_args[2:-1]
                t1_name = cmd_args[-1]

            if not validate_new_name(env, f_name, "term"):
                continue

            if t1_name not in env.terms:
                print(f"Error: Term '{t1_name}' not found in environment.")
                continue

            valid_vars = True
            for v in variables:
                if v not in env.variables:
                    print(f"Error: Variable '{v}' not found in environment.")
                    valid_vars = False
                    break
            if not valid_vars:
                continue

            definition = clone_ast(env.terms[t1_name])
            for i, var_name in enumerate(variables):
                dummy_name = f"_{i+1}"
                dummy_var = DummyVariable(name=dummy_name)
                env.add_dummy_variable(dummy_var)
                definition = substitute_term(definition, var_name, dummy_var)

            env.user_functions[f_name] = (arity, definition)
            decl_node = Function(
                name=f_name,
                arity=arity,
                func_type=FunctionType.USER_DEFINED,
                arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
            )
            env.terms[f_name] = decl_node
            print(f"Defined function '{f_name}' of arity {arity} = '{reconstruct_string(definition)}'")
            
        elif cmd == "def_r":
            cmd_args = args_str.split()
            if len(cmd_args) < 3:
                print("Error: Usage: def_r n R1 v1 v2 ... vn f1 (infix: def_r 2 v1 R1 v2 f1)")
                continue
            try:
                arity = int(cmd_args[0])
            except ValueError:
                print("Error: Arity must be an integer.")
                continue

            if arity == 2:
                if len(cmd_args) != 5:
                    print("Error: Usage for arity 2: def_r 2 v1 R1 v2 f1")
                    continue
                v1_name, r_name, v2_name, f1_name = cmd_args[1], cmd_args[2], cmd_args[3], cmd_args[4]
                variables = [v1_name, v2_name]
            else:
                if len(cmd_args) != arity + 3:
                    print(f"Error: Usage for arity {arity}: def_r {arity} R1 v1 v2 ... v{arity} f1")
                    continue
                r_name = cmd_args[1]
                variables = cmd_args[2:-1]
                f1_name = cmd_args[-1]

            if not validate_new_name(env, r_name, "formula"):
                continue

            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found in environment.")
                continue

            valid_vars = True
            for v in variables:
                if v not in env.variables:
                    print(f"Error: Variable '{v}' not found in environment.")
                    valid_vars = False
                    break
            if not valid_vars:
                continue

            definition = clone_ast(env.formulae[f1_name])
            for i, var_name in enumerate(variables):
                dummy_name = f"_{i+1}"
                dummy_var = DummyVariable(name=dummy_name)
                env.add_dummy_variable(dummy_var)
                definition = substitute_free(definition, var_name, dummy_var)

            env.user_relations[r_name] = (arity, definition)
            decl_node = Relation(
                name=r_name,
                arity=arity,
                rel_type=RelationType.USER_DEFINED,
                arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
            )
            env.formulae[r_name] = decl_node
            print(f"Defined relation '{r_name}' of arity {arity} = '{reconstruct_string(definition)}'")

        elif cmd == "iota":
            cmd_args = args_str.split()
            if len(cmd_args) < 2:
                print("Error: Usage: iota F1 f1")
                continue
            f_name, f1_name = cmd_args[0], cmd_args[1]
            
            if f1_name not in env.theorems:
                print(f"Error: Theorem '{f1_name}' not found in proven theorems.")
                continue
            
            theorem_node = env.theorems[f1_name]
            if not (isinstance(theorem_node, Quantifier) and theorem_node.name == "∃!"):
                print(f"Error: Theorem '{f1_name}' is not of the form ∃! x Ψ(x).")
                continue
                
            bound_var_name = theorem_node.variable.name
            from SubstitutionManager import get_free
            free_vars = get_free(theorem_node.formula)
            free_vars.discard(bound_var_name)
            
            if len(free_vars) == 0:
                ordered_vars = []
            elif len(free_vars) == 1:
                ordered_vars = list(free_vars)
            else:
                print(f"Multiple free variables found: {', '.join(sorted(free_vars))}")
                while True:
                    try:
                        user_seq = input("Enter sequence of variables separated by spaces: ").strip()
                    except (KeyboardInterrupt, EOFError):
                        print("\nOperation cancelled.")
                        ordered_vars = None
                        break
                    seq_vars = user_seq.split()
                    if set(seq_vars) != free_vars or len(seq_vars) != len(free_vars):
                        print(f"Error: Must enter exactly the variables {', '.join(sorted(free_vars))} without duplicates.")
                        continue
                    ordered_vars = seq_vars
                    break
                if ordered_vars is None:
                    continue
            
            if not validate_new_name(env, f_name, "term"):
                continue
                
            arity = len(ordered_vars)
            definition = clone_ast(theorem_node.formula)
            for i, var_name in enumerate(ordered_vars):
                dummy_name = f"_{i+1}"
                dummy_var = DummyVariable(name=dummy_name)
                env.add_dummy_variable(dummy_var)
                definition = substitute_free(definition, var_name, dummy_var)
                
            env.user_functions[f_name] = (arity, definition)
            decl_node = Function(
                name=f_name,
                arity=arity,
                func_type=FunctionType.IOTA_DEFINED,
                arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
            )
            env.terms[f_name] = decl_node
            print(f"Defined iota function '{f_name}' of arity {arity} = '{reconstruct_string(definition)}'")

        elif cmd == "fold":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: fold <symbol> <occurrence> <input> [args...] <output>")
                continue
                
            symbol = cmd_args[0]
            try:
                occurrence_idx = int(cmd_args[1])
            except ValueError:
                print("Error: Occurrence index must be an integer.")
                continue
                
            input_name = cmd_args[2]
            
            # 1. Fold existential quantifier ∃
            if symbol == "∃":
                if len(cmd_args) not in [4, 5]:
                    print("Error: Usage: fold ∃ <occurrence> <formula> <output> [f3]")
                    continue
                output_name = cmd_args[3]
                f3_name = cmd_args[4] if len(cmd_args) == 5 else None
                if input_name not in env.formulae:
                    print(f"Error: Formula '{input_name}' not found.")
                    continue
                if not validate_new_name(env, output_name, "formula"):
                    continue
                try:
                    expanded = expand_existential_in_formula(env.formulae[input_name], occurrence_idx)
                    env.formulae[output_name] = expanded
                    print(f"Expanded ∃ at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
                    if input_name in env.theorems:
                        env.theorems[output_name] = clone_ast(expanded)
                        print(f"Registered theorem '{output_name}'")
                    elif output_name in env.theorems:
                        env.theorems[input_name] = clone_ast(env.formulae[input_name])
                        print(f"Registered theorem '{input_name}'")
                    
                    if f3_name is not None:
                        if validate_new_name(env, f3_name, "formula"):
                            f1_clone = clone_ast(env.formulae[input_name])
                            f2_clone = clone_ast(expanded)
                            f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                            env.formulae[f3_name] = f3_node
                            env.theorems[f3_name] = clone_ast(f3_node)
                            print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                except Exception as e:
                    print(f"Error: {e}")
            
            # 2. Fold unique existential quantifier ∃!
            elif symbol == "∃!":
                if len(cmd_args) not in [5, 6]:
                    print("Error: Usage: fold ∃! <occurrence> <formula> <y> <output> [f3]")
                    continue
                y = cmd_args[3]
                output_name = cmd_args[4]
                f3_name = cmd_args[5] if len(cmd_args) == 6 else None
                if input_name not in env.formulae:
                    print(f"Error: Formula '{input_name}' not found.")
                    continue
                if not validate_new_name(env, output_name, "formula"):
                    continue
                if y not in env.variables:
                    if not validate_new_name(env, y, "variable"):
                        continue
                    env.add_variable(Variable(y))
                    print(f"Registered fresh variable '{y}'")
                try:
                    expanded = expand_unique_existential_in_formula(env.formulae[input_name], occurrence_idx, y)
                    env.formulae[output_name] = expanded
                    print(f"Expanded ∃! at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
                    if input_name in env.theorems:
                        env.theorems[output_name] = clone_ast(expanded)
                        print(f"Registered theorem '{output_name}'")
                    elif output_name in env.theorems:
                        env.theorems[input_name] = clone_ast(env.formulae[input_name])
                        print(f"Registered theorem '{input_name}'")
                    
                    if f3_name is not None:
                        if validate_new_name(env, f3_name, "formula"):
                            f1_clone = clone_ast(env.formulae[input_name])
                            f2_clone = clone_ast(expanded)
                            f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                            env.formulae[f3_name] = f3_node
                            env.theorems[f3_name] = clone_ast(f3_node)
                            print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                except Exception as e:
                    print(f"Error: {e}")
                    
            # 3. User-defined function / relation or iota function
            else:
                if input_name in env.terms:
                    if len(cmd_args) != 4:
                        print("Error: Usage: fold <function> <occurrence> <term> <output>")
                        continue
                    output_name = cmd_args[3]
                    if not validate_new_name(env, output_name, "term"):
                        continue
                    try:
                        expanded = expand_user_defined_function_in_term(env, env.terms[input_name], symbol, occurrence_idx)
                        env.terms[output_name] = expanded
                        print(f"Expanded function '{symbol}' at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
                    except Exception as e:
                        print(f"Error: {e}")
                        
                elif input_name in env.formulae:
                    if len(cmd_args) in [4, 5]:
                        output_name = cmd_args[3]
                        f3_name = cmd_args[4] if len(cmd_args) == 5 else None
                        if not validate_new_name(env, output_name, "formula"):
                            continue
                        
                        if symbol in env.user_relations:
                            try:
                                expanded = expand_user_defined_relation_in_formula(env, env.formulae[input_name], symbol, occurrence_idx)
                                env.formulae[output_name] = expanded
                                print(f"Expanded relation '{symbol}' at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
                                if input_name in env.theorems:
                                    env.theorems[output_name] = clone_ast(expanded)
                                    print(f"Registered theorem '{output_name}'")
                                elif output_name in env.theorems:
                                    env.theorems[input_name] = clone_ast(env.formulae[input_name])
                                    print(f"Registered theorem '{input_name}'")
                                
                                if f3_name is not None:
                                    if validate_new_name(env, f3_name, "formula"):
                                        f1_clone = clone_ast(env.formulae[input_name])
                                        f2_clone = clone_ast(expanded)
                                        f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                                        env.formulae[f3_name] = f3_node
                                        env.theorems[f3_name] = clone_ast(f3_node)
                                        print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                            except Exception as e:
                                print(f"Error: {e}")
                        elif symbol in env.user_functions:
                            try:
                                expanded = expand_user_defined_function_in_formula(env, env.formulae[input_name], symbol, occurrence_idx)
                                env.formulae[output_name] = expanded
                                print(f"Expanded function '{symbol}' at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
                                if input_name in env.theorems:
                                    env.theorems[output_name] = clone_ast(expanded)
                                    print(f"Registered theorem '{output_name}'")
                                elif output_name in env.theorems:
                                    env.theorems[input_name] = clone_ast(env.formulae[input_name])
                                    print(f"Registered theorem '{input_name}'")
                                
                                if f3_name is not None:
                                    if validate_new_name(env, f3_name, "formula"):
                                        f1_clone = clone_ast(env.formulae[input_name])
                                        f2_clone = clone_ast(expanded)
                                        f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                                        env.formulae[f3_name] = f3_node
                                        env.theorems[f3_name] = clone_ast(f3_node)
                                        print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                            except Exception as e:
                                print(f"Error: {e}")
                        else:
                            print(f"Error: Symbol '{symbol}' is not a defined function or relation.")
                            
                    elif len(cmd_args) in [6, 7]:
                        u = cmd_args[3]
                        v = cmd_args[4]
                        output_name = cmd_args[5]
                        f3_name = cmd_args[6] if len(cmd_args) == 7 else None
                        
                        if not validate_new_name(env, output_name, "formula"):
                            continue
                        
                        if u not in env.variables:
                            if not validate_new_name(env, u, "variable"):
                                continue
                            env.add_variable(Variable(u))
                            print(f"Registered fresh variable '{u}'")
                        if v not in env.variables:
                            if not validate_new_name(env, v, "variable"):
                                continue
                            env.add_variable(Variable(v))
                            print(f"Registered fresh variable '{v}'")
                            
                        try:
                            expanded = expand_iota_function_in_formula(env, env.formulae[input_name], symbol, occurrence_idx, u, v)
                            env.formulae[output_name] = expanded
                            print(f"Expanded iota function '{symbol}' at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
                            if input_name in env.theorems:
                                env.theorems[output_name] = clone_ast(expanded)
                                print(f"Registered theorem '{output_name}'")
                            elif output_name in env.theorems:
                                env.theorems[input_name] = clone_ast(env.formulae[input_name])
                                print(f"Registered theorem '{input_name}'")
                            
                            if f3_name is not None:
                                if validate_new_name(env, f3_name, "formula"):
                                    f1_clone = clone_ast(env.formulae[input_name])
                                    f2_clone = clone_ast(expanded)
                                    f3_node = Connective(name="⇔", arity=2, arguments=[f1_clone, f2_clone])
                                    env.formulae[f3_name] = f3_node
                                    env.theorems[f3_name] = clone_ast(f3_node)
                                    print(f"Registered theorem '{f3_name}' = '{reconstruct_string(f3_node)}'")
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print("Error: Usage: fold <symbol> <occurrence> <formula> <output> [f3]  OR  fold <iota_function> <occurrence> <formula> <u> <v> <output> [f3]")
                        continue
                else:
                    print(f"Error: Input '{input_name}' not found as a term or formula.")

        else:
            print(f"Unknown command '{cmd}'. Supported commands: cv, cV, ct, cf, cp, st, sf, sb, sa, sp, def_f, def_r, iota, fold, ua, ir, dt, show, exit, mission, help, guide, save, load, save_h, load_h, auto")
        # Record command in history if it succeeded and was entered by the user
        if not is_from_queue and not has_error:
            if cmd not in {"exit", "load_h", "save", "save_h", "help", "guide"}:
                history_commands.append(line)

        # Check if the goal in the current child environment is proven
        while env.goal_formula_name is not None and env.goal_formula_name in env.theorems:
            goal_name = env.goal_formula_name
            print(f"\nGoal statement '{goal_name}' is proven!")
            
            goal_node = env.theorems[goal_name]
            parent = env.parent
            
            # Register the goal formula in the parent environment as a proven theorem
            parent.theorems[goal_name] = clone_ast(goal_node)
            
            # Destroy the child environment and restore the parent
            env = parent
            print(f"Child environment destroyed. Returned to parent environment.")

if __name__ == "__main__":
    main()
