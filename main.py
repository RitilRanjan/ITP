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
            orig = getattr(e, "original_goal_formula_name", e.goal_formula_name)
            and_right = getattr(e, "and_right_formula_name", None)
            if orig != e.goal_formula_name and and_right:
                header = f" CHILD ENVIRONMENT (Original: {orig} → Ψ: {e.goal_formula_name}, Φ: {and_right}) "
            elif orig != e.goal_formula_name:
                header = f" CHILD ENVIRONMENT (Original: {orig} → Current: {e.goal_formula_name}) "
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
            W = 70
            print("=" * W)
            print(" INTERACTIVE THEOREM PROVER — COMMAND GUIDE ".center(W, "="))
            print("=" * W)

            print("\n── Variable & Object Definitions ──────────────────────────────────")
            print("  cv  <name>                  Create a standard (FOL) variable")
            print("  cV  <name>                  Create a propositional variable")
            print("  ct  <name> <term_expr>      Create a term  (e.g. ct t1 S x)")
            print("  cf  <name> <fol_expr>       Create a 1st-order formula (e.g. cf f1 ∀x x=y)")
            print("  cp  <name> <prop_expr>      Create a propositional formula (e.g. cp p1 p∧q)")

            print("\n── Substitutions ────────────────────────────────────────────────────")
            print("  st  t1 v t2 t3 [idx]        Substitute term t2 for variable v in term t1 → t3")
            print("  sf  f1 v t1 f2 [idx]        Substitute term t1 for free variable v in f1 → f2")
            print("  sb  f1 v t1 f2 [idx]        Rename bound variable v to t1 (a variable) in f1 → f2")
            print("  sa  f1 v t1 f2 [idx]        Substitute t1 for ALL occurrences of v in f1 → f2")
            print("  sp  p1 pv p2 p3 [idx]       Substitute prop-formula p2 for prop-var pv in p1 → p3")
            print("  [idx] = 1-based occurrence; omit for all occurrences")

            print("\n── Rewriting by Proven Equations & Bi-implications ─────────────────")
            print("  simp_l_eq target theorem [idx] [new] [equiv]")
            print("      Replace LHS of proven equality 'T3=T4' in target with T4")
            print("  simp_r_eq target theorem [idx] [new] [equiv]")
            print("      Replace RHS of proven equality 'T3=T4' in target with T3")
            print("  simp_l_bi target theorem [idx] [new] [equiv]")
            print("      Replace LHS of proven bi-implication 'F3⇔F4' in target with F4")
            print("  simp_r_bi target theorem [idx] [new] [equiv]")
            print("      Replace RHS of proven bi-implication 'F3⇔F4' in target with F3")
            print("  Targets: named term/formula OR the active goal (when target is omitted)")
            print("  new   = output name (omit for in-place); equiv = optional equivalence theorem")

            print("\n── Double-Negation Simplification ──────────────────────────────────")
            print("  neg- f1 [idx] [f2] [f3]     Remove ¬¬Ψ→Ψ at occurrence idx in formula f1")
            print("  neg- [idx] f2               Remove ¬¬ at occurrence idx in active goal, save as f2")
            print("  neg- f2                     Remove all ¬¬ in active goal, save as f2")
            print("  neg+ f1 [idx] [f2] [f3]     Wrap Ψ→¬¬Ψ at occurrence idx in formula f1")
            print("  neg+ [idx] f2               Wrap at occurrence idx in active goal, save as f2")
            print("  neg+ f2                     Wrap all subformulas in active goal, save as f2")
            print("  (idx=0 or omitted = ALL occurrences; f2/f3 omitted = in-place)")
            print("  f3 (equivalence theorem) only valid when rewriting a named formula, not the goal")

            print("\n── User-Defined Symbols ─────────────────────────────────────────────")
            print("  def_f n F1 v1..vn t1        Define function F1 of arity n (prefix)")
            print("  def_f 2 v1 F1 v2 t1         Define infix function F1 of arity 2")
            print("  def_r n R1 v1..vn f1        Define relation R1 of arity n (prefix)")
            print("  def_r 2 v1 R1 v2 f1         Define infix relation R1 of arity 2")
            print("  iota F1 f1                  Define iota (Hilbert choice) function F1 from a")
            print("                              unique-existence theorem f1=(∃!x Ψ(x))")

            print("\n── Definition Expansion / Folding ──────────────────────────────────")
            print("  fold ∃  <occ> <formula> <out> [f3]")
            print("  fold ∃! <occ> <formula> <y> <out> [f3]")
            print("  fold <symbol> <occ> <input> [args...] <out> [f3]")
            print("  Folds (reverse-expands) a user-defined symbol back into a formula/term.")
            print("  f3 = optional name to store the proven equivalence (f_in ⇔ f_out).")

            print("\n── Direct Proofs & Inference (ground environment) ───────────────────")
            print("  ua   <axiom> <formula>      Prove formula using a logical or ZFC axiom")
            print("  ir   <rule> <concl> [p1..]  Prove conclusion using rule with proven premises")
            print("  dt   <theorem>              Delete a proven theorem from the environment")
            print("  auto <formula>              Auto-prove formula via axioms, QR1/QR2, PC2")
            print("  Logical axioms:  E1  E2  E3  Q1  Q2")
            print("  ZFC axioms:      extension  pairing  union  power_set  regularity")
            print("                   infinity   choice   specification  replacement")
            print("  Inference rules: QR1  QR2  PC1  PC2")

            print("\n── Nested Environments & Mission Tactics ────────────────────────────")
            print("  mission <f>                 Enter a child env with goal formula f")
            print("  contra  f1 f2 f3 f4         Proof by contradiction:")
            print("                              f2 = ¬(def f1) [proven], goal f4 = ¬(def f3)∧(def f3)")
            print("  exit                        Leave current child env (or quit if in ground env)")
            print("  show                        Print the full environment stack")

            print("\n  Tactics (only valid inside a mission environment):")
            print("  apply  <axiom>              Test goal against axiom; close mission if satisfied")
            print("  apply  <rule> p1 p2 .. pn  Test goal against rule with proven premises; close mission")
            print("  apply2 <QR1|QR2> f1         Back-compute required premise from goal; set goal to f1")
            print("                              QR1: goal must be Ψ⇒(∀x Φ)  →  f1 = Ψ⇒Φ")
            print("                              QR2: goal must be (∃x Φ)⇒Ψ  →  f1 = Φ⇒Ψ")
            print("  apply3 f1 f2                f1 must be proven Ψ⇒Φ; Φ must match goal;")
            print("                              change goal to Ψ named f2 (modus ponens backwards)")
            print("  intro  f1 v                 Goal = ∀x Ψ(x): introduce fresh variable v,")
            print("                              set goal to Ψ(v) named f1 (∀-introduction)")
            print("  intro  f1 t1                Goal = ∃x Ψ(x): instantiate with term t1,")
            print("                              set goal to Ψ(def t1) named f1 (∃-introduction)")
            print("  left   f1                   Goal = Ψ∨Φ: reduce goal to Ψ named f1")
            print("  right  f1                   Goal = Ψ∨Φ: reduce goal to Φ named f1")
            print("  and    f1 f2                Goal = Ψ∧Φ: set goal to Ψ (f1) and open a")
            print("                              nested child env with goal Φ (f2)")
            print("  imply  f1 f2                Goal = Ψ⇒Φ: set goal to Φ (f1), add Ψ as")
            print("                              a proven assumption named f2 in the child env")

            print("\n  General-purpose destructuring (usable anywhere):")
            print("  and2   f1 f2                f1 must be Ψ∧Φ: redefine f1 as Ψ, create f2 as Φ")
            print("                              If f1 was proven, both f1 and f2 become proven")
            print("  intro2 f1 t1 f2             f1 must be ∀x Ψ(x): instantiate with term t1,")
            print("                              redefine f1 as the body Ψ(x), create f2 = Ψ(def t1)")
            print("                              If f1 was proven, f2 is also proven (∀-elimination)")

            print("\n── History & Persistence ────────────────────────────────────────────")
            print("  save                        Save environment state to save_files/")
            print("  load                        Load environment state from save_files/")
            print("  save_h                      Save command history to history_files/")
            print("  load_h                      Replay commands from history_files/")

            print("\n── Meta ─────────────────────────────────────────────────────────────")
            print("  help / guide                Show this guide")
            print("=" * W)

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

        elif cmd == "contra":
            cmd_args = args_str.split()
            if len(cmd_args) < 4:
                print("Error: Usage: contra <f1> <f2> <f3> <f4>")
                continue
            f1_name, f2_name, f3_name, f4_name = cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3]
            
            # 1. Verify f1 and f3 exist in active environment's formulae
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found.")
                continue
            if f3_name not in env.formulae:
                print(f"Error: Formula '{f3_name}' not found.")
                continue
                
            # 2. Verify f1 is not already proven
            if f1_name in env.theorems:
                print(f"Error: Goal '{f1_name}' is already proven.")
                continue
            # Also check if structurally identical theorem exists
            f1_node = env.formulae[f1_name]
            already_proven = False
            for k, v in env.theorems.items():
                if v.is_structurally_equal(f1_node):
                    already_proven = True
                    break
            if already_proven:
                print(f"Error: Goal '{f1_name}' (or a structurally identical formula) is already proven.")
                continue
                
            # 3. Verify name uniqueness for f2 and f4
            if f2_name == f4_name:
                print(f"Error: Name '{f2_name}' is already in use by another environment object.")
                continue
                
            # Validate f2 name
            if not validate_new_name(env, f2_name, "formula"):
                continue
            if f2_name in env.formulae or f2_name in env.theorems:
                print(f"Error: Name '{f2_name}' is already in use by another environment object.")
                continue
                
            # Validate f4 name
            if not validate_new_name(env, f4_name, "formula"):
                continue
            if f4_name in env.formulae or f4_name in env.theorems:
                print(f"Error: Name '{f4_name}' is already in use by another environment object.")
                continue
                
            # 4. Construct AST nodes
            f3_node = env.formulae[f3_name]
            f1_str = reconstruct_string(f1_node)
            f3_str = reconstruct_string(f3_node)
            try:
                neg_f1_node = parse_fol_formula(f"¬ ( {f1_str} )", env)
            except Exception:
                neg_f1_node = parse_prop_formula(f"¬ ( {f1_str} )", env)
                
            try:
                goal_node = parse_fol_formula(f"¬ ( {f3_str} ) ∧ ( {f3_str} )", env)
            except Exception:
                goal_node = parse_prop_formula(f"¬ ( {f3_str} ) ∧ ( {f3_str} )", env)
            
            # 5. Instantiation of child environment
            child_env = Environment(parent=env, goal_formula_name=f4_name, target_proven_formula_name=f1_name)
            child_env.formulae[f2_name] = neg_f1_node
            child_env.theorems[f2_name] = clone_ast(neg_f1_node)
            child_env.formulae[f4_name] = goal_node
            
            env = child_env
            print(f"Entered child environment for contradiction proof. Goal: '{f4_name}' (¬{f3_name} ∧ {f3_name}). Assumption '{f2_name}': ¬{f1_name}.")
            
        elif cmd in {"left", "right"}:
            # Only valid inside a child environment (mission)
            if env.goal_formula_name is None:
                print(f"Error: '{cmd}' can only be used inside a child environment (i.e. when there is an active mission goal).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) < 1:
                print(f"Error: Usage: {cmd} <new_goal_name>")
                continue
            new_goal_name = cmd_args[0]
            
            # Retrieve current goal formula
            current_goal_name = env.goal_formula_name
            if current_goal_name not in env.formulae:
                print(f"Error: Current goal formula '{current_goal_name}' not found in environment.")
                continue
            current_goal_node = env.formulae[current_goal_name]
            
            # Check that the goal is of the form Ψ ∨ Φ
            if not (isinstance(current_goal_node, Connective) and current_goal_node.name == "∨" and current_goal_node.arity == 2):
                print(f"Error: The current goal '{current_goal_name}' is not of the form Ψ ∨ Φ. "
                      f"'left'/'right' can only be used on disjunctive goals.")
                continue
            
            # Select the appropriate disjunct
            selected_node = current_goal_node.arguments[0] if cmd == "left" else current_goal_node.arguments[1]
            
            # Validate new_goal_name:
            # It can be an existing formula name only if its definition matches selected_node exactly.
            # It must not clash with anything else.
            if new_goal_name in env.formulae:
                existing_node = env.formulae[new_goal_name]
                if not existing_node.is_structurally_equal(selected_node):
                    print(f"Error: Name '{new_goal_name}' already exists in the environment with a different definition.")
                    continue
                # Name matches: this is fine, we'll reuse it
            else:
                # Brand new name — validate it doesn't clash with non-formula objects
                if not validate_new_name(env, new_goal_name, "formula"):
                    continue
                # Register the new formula
                env.formulae[new_goal_name] = clone_ast(selected_node)
            
            # Update the goal of the current child environment
            env.goal_formula_name = new_goal_name
            print(f"Goal updated to '{new_goal_name}': {reconstruct_string(env.formulae[new_goal_name])}")
            
            # If the new goal is already a proven theorem, close the mission immediately
            # (the while loop at the bottom of the REPL will handle the actual closure)

        elif cmd == "and":
            # Only valid inside a child environment (mission)
            if env.goal_formula_name is None:
                print("Error: 'and' can only be used inside a child environment (i.e. when there is an active mission goal).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) < 2:
                print("Error: Usage: and <f1> <f2>")
                continue
            f1_name, f2_name = cmd_args[0], cmd_args[1]

            # Retrieve current goal formula
            current_goal_name = env.goal_formula_name
            if current_goal_name not in env.formulae:
                print(f"Error: Current goal formula '{current_goal_name}' not found in environment.")
                continue
            current_goal_node = env.formulae[current_goal_name]

            # Check goal is of the form Ψ ∧ Φ
            if not (isinstance(current_goal_node, Connective) and current_goal_node.name == "∧" and current_goal_node.arity == 2):
                print(f"Error: The current goal '{current_goal_name}' is not of the form Ψ ∧ Φ. "
                      "'and' can only be used on conjunctive goals.")
                continue

            psi_node = current_goal_node.arguments[0]  # Ψ (left conjunct)
            phi_node = current_goal_node.arguments[1]  # Φ (right conjunct)

            # --- Validate f1 (name for Ψ) ---
            if f1_name in env.formulae:
                if not env.formulae[f1_name].is_structurally_equal(psi_node):
                    print(f"Error: Name '{f1_name}' already exists in the environment with a different definition.")
                    continue
                f1_new = False
            else:
                if not validate_new_name(env, f1_name, "formula"):
                    continue
                f1_new = True

            # Temporarily register f1 so that validate_new_name for f2 sees it
            if f1_new:
                env.formulae[f1_name] = clone_ast(psi_node)

            # --- Validate f2 (name for Φ) ---
            f2_error = False
            if f2_name in env.formulae:
                if not env.formulae[f2_name].is_structurally_equal(phi_node):
                    print(f"Error: Name '{f2_name}' already exists in the environment with a different definition.")
                    f2_error = True
                f2_new = False
            else:
                if not validate_new_name(env, f2_name, "formula"):
                    f2_error = True
                f2_new = True

            if f2_error:
                # Roll back temporary f1 registration
                if f1_new:
                    del env.local_formulae[f1_name]
                continue

            # Register f2 in the current child env (grandchild will inherit it via ChainMap)
            if f2_new:
                env.formulae[f2_name] = clone_ast(phi_node)

            # --- Modify current child env ---
            # original_goal_formula_name already holds the conjunction name (set at mission time)
            env.goal_formula_name = f1_name
            env.and_right_formula_name = f2_name
            print(f"Conjunction goal '{current_goal_name}' split into:")
            print(f"  Ψ ('{f1_name}'): {reconstruct_string(psi_node)}")
            print(f"  Φ ('{f2_name}'): {reconstruct_string(phi_node)}")
            print(f"Now working on Φ ('{f2_name}') in a nested environment first.")

            # --- Create grandchild environment for Φ ---
            grandchild = Environment(parent=env, goal_formula_name=f2_name)
            env = grandchild
            print(f"Entered nested environment for goal '{f2_name}'.")
            # Immediate closure if f2 is already proven (while loop below handles it)

        elif cmd == "and2":
            # and2 f1 f2
            # f1 must be a formula of the form Ψ ∧ Φ in the current environment.
            # The definition of f1 is changed to just Ψ.
            # A new formula f2 is created with definition Φ.
            # If f1 was a proven theorem, it remains proven (now as Ψ) and f2 is also proven.
            cmd_args = args_str.split()
            if len(cmd_args) != 2:
                print("Error: Usage: and2 f1 f2")
                continue
            f1_name, f2_name = cmd_args[0], cmd_args[1]

            # f1 must already exist
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found in environment.")
                continue

            f1_node = env.formulae[f1_name]

            # f1 must be of the form Ψ ∧ Φ
            if not (isinstance(f1_node, Connective) and f1_node.name == "∧" and f1_node.arity == 2):
                print(f"Error: Formula '{f1_name}' is not of the form Ψ ∧ Φ.")
                continue

            psi_node = f1_node.arguments[0]  # Ψ (left conjunct)
            phi_node = f1_node.arguments[1]  # Φ (right conjunct)

            # Validate f2 — must be an unused name or an existing formula with definition Φ
            if f2_name in env.formulae:
                if not env.formulae[f2_name].is_structurally_equal(phi_node):
                    print(f"Error: Name '{f2_name}' already exists with a different definition.")
                    continue
                # Same definition — fine, will reuse
            else:
                if not validate_new_name(env, f2_name, "formula"):
                    continue

            # Determine if f1 was proven before the modification
            f1_was_proven = f1_name in env.theorems

            # Overwrite f1's definition to Ψ only.
            # We must write into the *local* dict of the current environment to avoid
            # mutating a parent-environment entry.
            if f1_name not in env.local_formulae and f1_name in env.formulae:
                # f1 is inherited from a parent — shadow it locally
                env.local_formulae[f1_name] = clone_ast(psi_node)
            else:
                env.formulae[f1_name] = clone_ast(psi_node)

            # Register f2 = Φ
            if f2_name not in env.formulae:
                env.formulae[f2_name] = clone_ast(phi_node)

            # Propagate proven status
            if f1_was_proven:
                # f1 is now Ψ; the original conjunction being proven implies both parts are,
                # so registering both as theorems is sound.
                env.theorems[f1_name] = clone_ast(psi_node)
                env.theorems[f2_name] = clone_ast(phi_node)
                print(f"'{f1_name}' redefined to: {reconstruct_string(psi_node)}  [proven]")
                print(f"'{f2_name}' created as:   {reconstruct_string(phi_node)}  [proven]")
            else:
                print(f"'{f1_name}' redefined to: {reconstruct_string(psi_node)}")
                print(f"'{f2_name}' created as:   {reconstruct_string(phi_node)}")

        elif cmd == "imply":
            # Only valid inside a child environment (mission)
            if env.goal_formula_name is None:
                print("Error: 'imply' can only be used inside a child environment (i.e. when there is an active mission goal).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) < 2:
                print("Error: Usage: imply <f1> <f2>")
                continue
            f1_name, f2_name = cmd_args[0], cmd_args[1]

            # Retrieve current goal formula
            current_goal_name = env.goal_formula_name
            if current_goal_name not in env.formulae:
                print(f"Error: Current goal formula '{current_goal_name}' not found in environment.")
                continue
            current_goal_node = env.formulae[current_goal_name]

            # Check goal is of the form Ψ ⇒ Φ
            if not (isinstance(current_goal_node, Connective) and current_goal_node.name == "⇒" and current_goal_node.arity == 2):
                print(f"Error: The current goal '{current_goal_name}' is not of the form Ψ ⇒ Φ. "
                      "'imply' can only be used on implication goals.")
                continue

            psi_node = current_goal_node.arguments[0]   # Ψ (antecedent) — becomes assumption f2
            phi_node = current_goal_node.arguments[1]   # Φ (consequent) — becomes new goal f1

            # ----------------------------------------------------------------
            # Validate f1 (new goal name for Φ = consequent)
            # Rules: new name, or existing formula with matching definition
            # ----------------------------------------------------------------
            if f1_name in env.formulae:
                if not env.formulae[f1_name].is_structurally_equal(phi_node):
                    print(f"Error: Name '{f1_name}' already exists in the environment with a different definition.")
                    continue
                f1_new = False
            else:
                if not validate_new_name(env, f1_name, "formula"):
                    continue
                f1_new = True

            # Temporarily register f1 so validate_new_name for f2 sees it
            if f1_new:
                env.formulae[f1_name] = clone_ast(phi_node)

            # ----------------------------------------------------------------
            # Validate f2 (assumption name for Ψ = antecedent)
            # Rules:
            #   1. Completely new name → add to child local_formulae + local_theorems
            #   2. Existing formula in scope (child or parent) with matching def:
            #        a. Already proven in scope → no action (already usable as theorem)
            #        b. Not yet proven → add to child’s local_theorems only
            #           (assumption stays child-scoped; parent is unaffected on closure)
            #   3. Different definition → Error
            #   4. Clashes with non-formula object → Error
            # ----------------------------------------------------------------
            f2_error = False
            f2_action = None   # 'new', 'theorem_only', or 'already_proven'

            if f2_name in env.formulae:
                if not env.formulae[f2_name].is_structurally_equal(psi_node):
                    print(f"Error: Name '{f2_name}' already exists in the environment with a different definition.")
                    f2_error = True
                elif f2_name in env.theorems:
                    # Already a proven theorem in the visible scope — nothing to do
                    f2_action = 'already_proven'
                else:
                    # Formula exists but not proven anywhere in scope —
                    # make it proven locally (child-scoped assumption)
                    f2_action = 'theorem_only'
            else:
                # Brand new name
                if not validate_new_name(env, f2_name, "formula"):
                    f2_error = True
                else:
                    f2_action = 'new'

            if f2_error:
                # Roll back f1 temporary registration
                if f1_new:
                    del env.local_formulae[f1_name]
                continue

            # ----------------------------------------------------------------
            # Apply f2 changes to the child environment
            # ----------------------------------------------------------------
            if f2_action == 'new':
                env.local_formulae[f2_name] = clone_ast(psi_node)
                env.local_theorems[f2_name] = clone_ast(psi_node)
                print(f"Created assumption '{f2_name}' = '{reconstruct_string(psi_node)}' as a proven theorem in this environment.")
            elif f2_action == 'theorem_only':
                env.local_theorems[f2_name] = clone_ast(psi_node)
                print(f"Registered existing formula '{f2_name}' as a proven assumption (Ψ) in this environment. "
                      f"It remains unproven in the parent environment.")
            else:  # 'already_proven'
                print(f"'{f2_name}' = Ψ is already a proven theorem in scope. Using it as assumption.")

            # ----------------------------------------------------------------
            # Update the child env’s goal to f1 (Φ)
            # original_goal_formula_name retains the implication name from mission
            # ----------------------------------------------------------------
            env.goal_formula_name = f1_name
            print(f"Goal updated to '{f1_name}' (Φ): {reconstruct_string(phi_node)}")
            print(f"Assumption '{f2_name}' (Ψ): {reconstruct_string(psi_node)} is available as proven theorem.")
            # The while loop handles immediate closure if f1 is already proven

        elif cmd == "intro":
            # Only valid inside a child environment (mission)
            if env.goal_formula_name is None:
                print("Error: 'intro' can only be used inside a child environment (i.e. when there is an active mission goal).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) < 2:
                print("Error: Usage:")
                print("  For ∀x Ψ(x): intro <f1> <v>  (v must be a completely fresh variable name)")
                print("  For ∃x Ψ(x): intro <f1> <t1> (t1 must be an existing term name)")
                continue
            f1_name, arg2_name = cmd_args[0], cmd_args[1]

            # Retrieve current goal formula
            current_goal_name = env.goal_formula_name
            if current_goal_name not in env.formulae:
                print(f"Error: Current goal formula '{current_goal_name}' not found in environment.")
                continue
            current_goal_node = env.formulae[current_goal_name]

            # Check goal is of the form ∀x Ψ(x) or ∃x Ψ(x)
            if not (isinstance(current_goal_node, Quantifier) and current_goal_node.name in {"∀", "∃"}):
                print(f"Error: The current goal '{current_goal_name}' is not of the form ∀x Ψ(x) or ∃x Ψ(x). "
                      "'intro' can only be used on quantified goals.")
                continue

            bound_var_name = current_goal_node.variable.name   # x (the quantifier's bound var)
            body_node = current_goal_node.formula               # Ψ(x)
            is_universal = (current_goal_node.name == "∀")

            if is_universal:
                v_name = arg2_name
                # ----------------------------------------------------------------
                # v must be a completely fresh name — not found anywhere in the
                # current environment chain (variables, terms, formulae, theorems,
                # propositional variables, etc.).  This guarantees that no existing
                # theorem can mention v, making the ∀-intro rule sound:
                #
                #   If  Ψ(v)  is provable with v *fresh*, then ∀x Ψ(x) holds.
                #
                # (Substituting v for x also severs the connection to any existing
                #  theorems about the original variable x, removing that source of
                #  unsoundness from the original single-argument design.)
                # ----------------------------------------------------------------
                if not validate_new_name(env, v_name, "variable"):
                    # validate_new_name prints the specific clash reason
                    continue

                # ----------------------------------------------------------------
                # Build the new body Ψ(v) by substituting the fresh variable v for
                # every free occurrence of x in the body.  Since v is fresh it
                # cannot be captured by any inner quantifier, so substitution is
                # always valid.
                # ----------------------------------------------------------------
                v_var_node = Variable(name=v_name)
                body_clone = clone_ast(body_node)
                new_body_node = substitute_free(body_clone, bound_var_name, v_var_node)

                # ----------------------------------------------------------------
                # Validate f1: new name, or existing formula with matching def Ψ(v)
                # ----------------------------------------------------------------
                if f1_name in env.formulae:
                    if not env.formulae[f1_name].is_structurally_equal(new_body_node):
                        print(f"Error: Name '{f1_name}' already exists in the environment with a different definition.")
                        continue
                    # Existing name matches Ψ(v) — reuse it (v still must be created below)
                else:
                    if not validate_new_name(env, f1_name, "formula"):
                        continue
                    env.formulae[f1_name] = new_body_node   # already a clone from substitute_free

                # Create v as a variable in the child environment AFTER all checks pass
                env.local_variables[v_name] = Variable(name=v_name)

                # ----------------------------------------------------------------
                # Update the child env's goal to f1 = Ψ(v)
                # original_goal_formula_name retains the ∀x Ψ(x) name from mission
                # ----------------------------------------------------------------
                env.goal_formula_name = f1_name
                print(f"Introduced fresh variable '{v_name}' (replaces bound '{bound_var_name}').")
                print(f"Goal updated to '{f1_name}': {reconstruct_string(new_body_node)}")
                print(f"Prove the body for arbitrary '{v_name}' to close universal goal '{current_goal_name}'.")
                # The while loop handles immediate closure if f1 is already proven

            else:
                # Existential quantifier goal: ∃x Ψ(x)
                t1_name = arg2_name
                # ----------------------------------------------------------------
                # t1 must be the name of a created term in either child or parent environment.
                # ----------------------------------------------------------------
                if t1_name not in env.terms:
                    print(f"Error: Term '{t1_name}' not found in the environment.")
                    continue

                t1_node = env.terms[t1_name]
                body_clone = clone_ast(body_node)
                new_body_node = substitute_free(body_clone, bound_var_name, clone_ast(t1_node))

                # ----------------------------------------------------------------
                # Validate f1: new name, or existing formula with matching def Ψ(definition of t1)
                # ----------------------------------------------------------------
                if f1_name in env.formulae:
                    if not env.formulae[f1_name].is_structurally_equal(new_body_node):
                        print(f"Error: Name '{f1_name}' already exists in the environment with a different definition.")
                        continue
                    # Existing name matches Ψ(definition of t1) — reuse it
                else:
                    if not validate_new_name(env, f1_name, "formula"):
                        continue
                    env.formulae[f1_name] = new_body_node

                # ----------------------------------------------------------------
                # Update the child env's goal to f1 = Ψ(definition of t1)
                # original_goal_formula_name retains the ∃x Ψ(x) name from mission
                # ----------------------------------------------------------------
                env.goal_formula_name = f1_name
                print(f"Goal updated to '{f1_name}': {reconstruct_string(new_body_node)}")
                print(f"Prove the body with term '{t1_name}' (replaces bound '{bound_var_name}') to close existential goal '{current_goal_name}'.")
                # The while loop handles immediate closure if f1 is already proven


        elif cmd == "intro2":
            # intro2 f1 t1 f2
            # f1 must be a formula of the form ∀x Ψ(x) in the current environment.
            # t1 must be the name of an already created term.
            # Creates formula f2 = Ψ(definition of t1), redefines f1 to just Ψ(x) [the body].
            # If f1 was proven, f2 is also proven (by ∀-elimination / universal instantiation).
            cmd_args = args_str.split()
            if len(cmd_args) != 3:
                print("Error: Usage: intro2 f1 t1 f2")
                continue
            f1_name, t1_name, f2_name = cmd_args[0], cmd_args[1], cmd_args[2]

            # f1 must exist
            if f1_name not in env.formulae:
                print(f"Error: Formula '{f1_name}' not found in environment.")
                continue

            f1_node = env.formulae[f1_name]

            # f1 must be ∀x Ψ(x)
            if not (isinstance(f1_node, Quantifier) and f1_node.name == "∀"):
                print(f"Error: Formula '{f1_name}' is not of the form ∀x Ψ(x).")
                continue

            bound_var_name = f1_node.variable.name  # x
            body_node = f1_node.formula              # Ψ(x)

            # t1 must be a known term
            if t1_name not in env.terms:
                print(f"Error: Term '{t1_name}' not found in environment.")
                continue

            t1_node = env.terms[t1_name]

            # Build Ψ(definition of t1) by substituting t1 for every free x in body
            body_clone = clone_ast(body_node)
            instantiated_node = substitute_free(body_clone, bound_var_name, clone_ast(t1_node))

            # Validate f2 — unused name or existing formula with same definition
            if f2_name in env.formulae:
                if not env.formulae[f2_name].is_structurally_equal(instantiated_node):
                    print(f"Error: Name '{f2_name}' already exists with a different definition.")
                    continue
                # Reuse existing name silently
            else:
                if not validate_new_name(env, f2_name, "formula"):
                    continue
                env.formulae[f2_name] = instantiated_node

            # Determine if f1 was proven before modification
            f1_was_proven = f1_name in env.theorems

            # Redefine f1 to the body only (Ψ, with x still bound).
            # Shadow locally if f1 comes from a parent environment.
            if f1_name not in env.local_formulae and f1_name in env.formulae:
                env.local_formulae[f1_name] = clone_ast(body_node)
            else:
                env.formulae[f1_name] = clone_ast(body_node)

            # Propagate proven status: ∀x Ψ(x) proven → Ψ(t1) proven (universal instantiation)
            if f1_was_proven:
                env.theorems[f1_name] = clone_ast(body_node)
                env.theorems[f2_name] = clone_ast(instantiated_node)
                print(f"'{f1_name}' redefined to body: {reconstruct_string(body_node)}  [proven]")
                print(f"'{f2_name}' created as:         {reconstruct_string(instantiated_node)}  [proven]")
            else:
                print(f"'{f1_name}' redefined to body: {reconstruct_string(body_node)}")
                print(f"'{f2_name}' created as:         {reconstruct_string(instantiated_node)}")

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
                
        elif cmd == "apply":
            # Only valid inside a child environment (mission)
            if env.goal_formula_name is None:
                print("Error: 'apply' can only be used inside a mission environment (active goal required).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) < 1:
                print("Error: Usage: apply <axiom>  or  apply <rule> f1 f2 ... fn")
                continue

            name = cmd_args[0]
            goal_name = env.goal_formula_name
            goal_node = env.formulae[goal_name]

            if name in AXIOMS:
                # apply <axiom>  → test goal against the axiom directly
                if len(cmd_args) != 1:
                    print(f"Error: 'apply {name}' takes no additional arguments — it tests the goal statement directly.")
                    continue
                axiom_func = AXIOMS[name]
                try:
                    if axiom_func(goal_node):
                        env.theorems[goal_name] = clone_ast(goal_node)
                        print(f"Goal '{goal_name}' satisfies axiom '{name}'. Mission closed.")
                    else:
                        print(f"Error: Goal '{goal_name}' does not satisfy axiom '{name}'.")
                except Exception as e:
                    print(f"Error during axiom application: {e}")

            elif name in RULES:
                # apply <rule> f1 f2 ... fn  → prove goal using rule with f1..fn as proven premises
                premise_names = cmd_args[1:]
                premise_nodes = []
                valid = True
                for p_name in premise_names:
                    if p_name not in env.theorems:
                        print(f"Error: Premise '{p_name}' is not a proven theorem.")
                        valid = False
                        break
                    premise_nodes.append(env.theorems[p_name])
                if not valid:
                    continue
                rule_func = RULES[name]
                try:
                    if rule_func(premise_nodes, goal_node):
                        env.theorems[goal_name] = clone_ast(goal_node)
                        print(f"Goal '{goal_name}' proven using rule '{name}'. Mission closed.")
                    else:
                        print(f"Error: Goal '{goal_name}' does not follow from the given premises using rule '{name}'.")
                except Exception as e:
                    print(f"Error during rule application: {e}")
            else:
                print(f"Error: Unknown axiom or rule '{name}'. Supported axioms: {', '.join(AXIOMS.keys())}; rules: {', '.join(RULES.keys())}.")
                continue

        elif cmd == "apply2":
            # apply2 <QR1|QR2> f1
            # Reverse-engineer the required single premise for QR1 or QR2 from the goal,
            # create it as formula f1, and change the goal to f1.
            if env.goal_formula_name is None:
                print("Error: 'apply2' can only be used inside a mission environment (active goal required).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) != 2:
                print("Error: Usage: apply2 <QR1|QR2> f1")
                continue
            rule_name = cmd_args[0]
            f1_name = cmd_args[1]

            if rule_name not in ("QR1", "QR2"):
                print(f"Error: 'apply2' only supports QR1 and QR2 (got '{rule_name}').")
                continue

            goal_name = env.goal_formula_name
            goal_node = env.formulae[goal_name]

            # --- Decompose the goal to build the required premise ---
            # QR1 conclusion shape:  ψ ⇒ (∀x φ)   →  required premise: ψ ⇒ φ
            # QR2 conclusion shape:  (∃x φ) ⇒ ψ   →  required premise: φ ⇒ ψ
            if not isinstance(goal_node, Connective) or goal_node.name != "⇒" or len(goal_node.arguments) != 2:
                print(f"Error: Goal '{goal_name}' is not of the form Ψ ⇒ Φ, which is required for {rule_name}.")
                continue

            left, right = goal_node.arguments[0], goal_node.arguments[1]

            if rule_name == "QR1":
                if not isinstance(right, Quantifier) or right.name != "∀":
                    print(f"Error: For QR1 the goal must be of the form Ψ ⇒ (∀x Φ). Got: '{reconstruct_string(goal_node)}'")
                    continue
                x_name = right.variable.name
                phi = right.formula
                from SubstitutionManager import check_free, check_bound
                if check_free(left, x_name):
                    print(f"Error: Cannot apply QR1 — variable '{x_name}' occurs free in Ψ.")
                    continue
                if check_bound(phi, x_name):
                    print(f"Error: Cannot apply QR1 — variable '{x_name}' is bound inside Φ.")
                    continue
                # Required premise: ψ ⇒ φ
                premise_node = Connective(name="⇒", arity=2, arguments=[clone_ast(left), clone_ast(phi)])

            else:  # QR2
                if not isinstance(left, Quantifier) or left.name != "∃":
                    print(f"Error: For QR2 the goal must be of the form (∃x Φ) ⇒ Ψ. Got: '{reconstruct_string(goal_node)}'")
                    continue
                x_name = left.variable.name
                phi = left.formula
                from SubstitutionManager import check_free, check_bound
                if check_free(right, x_name):
                    print(f"Error: Cannot apply QR2 — variable '{x_name}' occurs free in Ψ.")
                    continue
                if check_bound(phi, x_name):
                    print(f"Error: Cannot apply QR2 — variable '{x_name}' is bound inside Φ.")
                    continue
                # Required premise: φ ⇒ ψ
                premise_node = Connective(name="⇒", arity=2, arguments=[clone_ast(phi), clone_ast(right)])

            # Validate and register f1
            # f1 may already exist if it has exactly the same definition
            if f1_name in env.formulae:
                if not env.formulae[f1_name].is_structurally_equal(premise_node):
                    print(f"Error: Name '{f1_name}' is already used for a different formula.")
                    continue
                # Same definition — reuse it (no need to register again)
            else:
                if not validate_new_name(env, f1_name, "formula"):
                    continue
                env.formulae[f1_name] = premise_node

            # Change the goal to f1
            env.goal_formula_name = f1_name
            print(f"Goal changed to '{f1_name}': {reconstruct_string(premise_node)}")
            print(f"Prove '{f1_name}' to close the original goal via {rule_name}.")

        elif cmd == "apply3":
            # apply3 f1 f2
            # Uses proven theorem f1 of the form Ψ ⇒ Φ where Φ is the goal.
            # Changes the goal to Ψ, named f2.
            if env.goal_formula_name is None:
                print("Error: 'apply3' can only be used inside a mission environment (active goal required).")
                continue
            cmd_args = args_str.split()
            if len(cmd_args) != 2:
                print("Error: Usage: apply3 f1 f2")
                continue
            f1_name, f2_name = cmd_args[0], cmd_args[1]

            if f1_name not in env.theorems:
                print(f"Error: '{f1_name}' is not a proven theorem.")
                continue

            impl_node = env.theorems[f1_name]
            if not isinstance(impl_node, Connective) or impl_node.name != "⇒" or len(impl_node.arguments) != 2:
                print(f"Error: Theorem '{f1_name}' is not of the form Ψ ⇒ Φ.")
                continue

            psi, phi = impl_node.arguments[0], impl_node.arguments[1]
            goal_name = env.goal_formula_name
            goal_node = env.formulae[goal_name]

            if not phi.is_structurally_equal(goal_node):
                print(f"Error: The conclusion Φ of '{f1_name}' does not match the current goal '{goal_name}'.")
                continue

            # Validate f2
            if f2_name in env.formulae:
                if not env.formulae[f2_name].is_structurally_equal(psi):
                    print(f"Error: Name '{f2_name}' is already used for a different formula.")
                    continue
                # Same definition — fine
            else:
                if not validate_new_name(env, f2_name, "formula"):
                    continue
                env.formulae[f2_name] = clone_ast(psi)

            env.goal_formula_name = f2_name
            print(f"Goal changed to '{f2_name}': {reconstruct_string(psi)}")
            print(f"Prove '{f2_name}' (Ψ) to close the original goal via modus ponens with '{f1_name}'.")

            # If f2 is already proven, the while loop will close the mission

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

        elif cmd in ["simp_l_eq", "simp_r_eq", "simp_l_bi", "simp_r_bi"]:
            cmd_args = args_str.split()
            if not (1 <= len(cmd_args) <= 5):
                print(f"Error: Invalid number of arguments for {cmd}.")
                continue
                
            arg0 = cmd_args[0]
            
            target_type = None
            target_name = None
            theorem_name = None
            remaining_args = []
            
            if arg0 in env.terms:
                target_type = "term"
                target_name = arg0
                if len(cmd_args) < 2:
                    print("Error: Missing theorem name.")
                    continue
                theorem_name = cmd_args[1]
                remaining_args = cmd_args[2:]
            elif arg0 in env.formulae and len(cmd_args) > 1 and cmd_args[1] in env.formulae and cmd_args[1] in env.theorems:
                target_type = "formula"
                target_name = arg0
                theorem_name = cmd_args[1]
                remaining_args = cmd_args[2:]
            elif env.goal_formula_name is not None and arg0 in env.theorems:
                target_type = "goal"
                target_name = env.goal_formula_name
                theorem_name = arg0
                remaining_args = cmd_args[1:]
            else:
                print(f"Error: Could not resolve target and theorem for {cmd}.")
                continue
                
            occurrence_idx = None
            new_name = None
            equivalence_name = None
            
            idx = 0
            if idx < len(remaining_args) and remaining_args[idx].isdigit():
                occurrence_idx = int(remaining_args[idx])
                idx += 1
            if idx < len(remaining_args):
                new_name = remaining_args[idx]
                idx += 1
            if idx < len(remaining_args) and target_type == "formula":
                equivalence_name = remaining_args[idx]
                idx += 1
                
            if idx < len(remaining_args):
                print("Error: Too many arguments or invalid argument format.")
                continue
                
            if theorem_name not in env.theorems:
                print(f"Error: '{theorem_name}' is not a proven theorem.")
                continue
                
            if new_name is None:
                if target_type == "term" and target_name not in env.local_terms:
                    print(f"Error: Cannot modify term '{target_name}' in-place because it belongs to a parent environment.")
                    continue
                if target_type == "formula" and target_name not in env.local_formulae:
                    print(f"Error: Cannot modify formula '{target_name}' in-place because it belongs to a parent environment.")
                    continue
                if target_type == "goal" and env.goal_formula_name not in env.local_formulae:
                    print(f"Error: Cannot modify goal statement in-place because the goal formula was defined in a parent environment.")
                    continue

            if new_name is not None and not validate_new_name(env, new_name, "formula" if target_type in ["formula", "goal"] else "term"):
                continue
            if equivalence_name is not None and not validate_new_name(env, equivalence_name, "formula"):
                continue
                
            target_node = env.terms[target_name] if target_type == "term" else env.formulae[target_name]
            th_node = env.theorems[theorem_name]
            
            replace_from = None
            replace_to = None
            
            if cmd in ["simp_l_eq", "simp_r_eq"]:
                if not isinstance(th_node, Relation) or th_node.name != "=" or len(th_node.arguments) != 2:
                    print(f"Error: Theorem '{theorem_name}' is not an equality.")
                    continue
                t3, t4 = th_node.arguments
                replace_from = t3 if cmd == "simp_l_eq" else t4
                replace_to = t4 if cmd == "simp_l_eq" else t3
            else:
                if target_type == "term":
                    print(f"Error: {cmd} cannot be applied to terms.")
                    continue
                if not isinstance(th_node, Connective) or th_node.name != "⇔" or len(th_node.arguments) != 2:
                    print(f"Error: Theorem '{theorem_name}' is not a bi-implication.")
                    continue
                f3, f4 = th_node.arguments
                replace_from = f3 if cmd == "simp_l_bi" else f4
                replace_to = f4 if cmd == "simp_l_bi" else f3
                
            from SubstitutionManager import replace_structurally
            
            try:
                new_node = replace_structurally(target_node, replace_from, replace_to, occurrence_idx)
            except Exception as e:
                print(f"Error during substitution: {e}")
                continue
                
            if target_node.is_structurally_equal(new_node):
                print("Notice: No matching occurrences were found to substitute.")
                continue
                
            if target_type == "term":
                save_name = new_name if new_name else target_name
                env.terms[save_name] = new_node
                print(f"Saved modified term as '{save_name}': {reconstruct_string(new_node)}")
            elif target_type == "formula":
                save_name = new_name if new_name else target_name
                env.formulae[save_name] = new_node
                print(f"Saved modified formula as '{save_name}': {reconstruct_string(new_node)}")
                if target_name in env.theorems:
                    env.theorems[save_name] = clone_ast(new_node)
                    print(f"'{save_name}' is also a proven theorem.")
                if equivalence_name is not None:
                    f2_clone = clone_ast(target_node)
                    f3_clone = clone_ast(new_node)
                    equiv_node = Connective(name="⇔", arity=2, arguments=[f2_clone, f3_clone])
                    env.formulae[equivalence_name] = equiv_node
                    env.theorems[equivalence_name] = clone_ast(equiv_node)
                    print(f"Registered equivalence theorem '{equivalence_name}': {reconstruct_string(equiv_node)}")
            elif target_type == "goal":
                save_name = new_name if new_name else target_name
                env.formulae[save_name] = new_node
                env.goal_formula_name = save_name
                print(f"Goal updated to '{save_name}': {reconstruct_string(new_node)}")

        elif cmd in ["neg-", "neg+"]:
            from SubstitutionManager import remove_double_neg, add_double_neg
            transform_fn = remove_double_neg if cmd == "neg-" else add_double_neg

            cmd_args = args_str.split()
            if not (0 < len(cmd_args) <= 4):
                print(f"Error: Usage: {cmd} [f1] [idx] [f2] [f3]  or  {cmd} [idx] f2  or  {cmd} f2")
                continue

            # ── Argument disambiguation ──────────────────────────────────────────────
            # We must decide whether the first token names a *source formula* (f1) or
            # is the *occurrence index* / *output name* when targeting the goal.
            #
            # Rules (matching the spec):
            #   • If arg0 is a formula name in the environment  → target = that formula
            #   • If arg0 is a digit (incl. "0")               → target = goal, arg0 is index
            #   • Otherwise                                     → target = goal, arg0 is the output name (all occurrences)

            arg0 = cmd_args[0]

            target_type: str      # "formula" or "goal"
            target_name: str      # resolved formula name for target
            occurrence_idx: Optional[int] = None
            new_name: Optional[str] = None
            equiv_name: Optional[str] = None
            remaining_args: list

            if arg0 in env.formulae:
                # ── Target is a named formula ─────────────────────────────────────
                target_type = "formula"
                target_name = arg0
                remaining_args = cmd_args[1:]

                # remaining: [idx] [f2] [f3]
                ridx = 0
                if ridx < len(remaining_args) and remaining_args[ridx].lstrip("-").isdigit():
                    raw = int(remaining_args[ridx])
                    occurrence_idx = None if raw == 0 else raw
                    ridx += 1
                if ridx < len(remaining_args):
                    new_name = remaining_args[ridx]; ridx += 1
                if ridx < len(remaining_args):
                    equiv_name = remaining_args[ridx]; ridx += 1
                if ridx < len(remaining_args):
                    print(f"Error: Too many arguments for {cmd}.")
                    continue

            elif arg0.lstrip("-").isdigit():
                # ── Target is the goal statement; arg0 is the occurrence index ────
                if env.goal_formula_name is None:
                    print(f"Error: {cmd} with an index requires an active goal statement (child environment).")
                    continue
                target_type = "goal"
                target_name = env.goal_formula_name
                raw = int(arg0)
                occurrence_idx = None if raw == 0 else raw
                remaining_args = cmd_args[1:]

                # remaining: [f2] [f3]  (no more index expected)
                ridx = 0
                if ridx < len(remaining_args):
                    new_name = remaining_args[ridx]; ridx += 1
                if ridx < len(remaining_args):
                    print(f"Error: When targeting the goal with an index, only one output name is accepted (f3 is not allowed for goal simplifications).")
                    continue

            else:
                # ── Target is the goal statement; arg0 is the output name (all occurrences) ──
                if env.goal_formula_name is None:
                    print(f"Error: No active goal statement. Start a mission environment first.")
                    continue
                target_type = "goal"
                target_name = env.goal_formula_name
                occurrence_idx = None   # all occurrences
                new_name = arg0
                remaining_args = cmd_args[1:]

                ridx = 0
                if ridx < len(remaining_args):
                    print(f"Error: Too many arguments when targeting the goal statement.")
                    continue

            # ── Validate output name ──────────────────────────────────────────────
            if new_name is not None and not validate_new_name(env, new_name, "formula"):
                continue
            if equiv_name is not None and not validate_new_name(env, equiv_name, "formula"):
                continue

            # In-place modifications of parent-environment objects are forbidden
            if new_name is None:
                if target_type == "formula" and target_name not in env.local_formulae:
                    print(f"Error: Cannot modify formula '{target_name}' in-place because it belongs to a parent environment.")
                    continue
                if target_type == "goal" and target_name not in env.local_formulae:
                    print(f"Error: Cannot modify goal statement in-place because the goal formula was defined in a parent environment.")
                    continue

            # ── Apply transformation ──────────────────────────────────────────────
            target_node = env.formulae[target_name]
            try:
                new_node = transform_fn(target_node, occurrence_idx)
            except Exception as e:
                print(f"Error during transformation: {e}")
                continue

            if target_node.is_structurally_equal(new_node):
                op = "double negation" if cmd == "neg-" else "negation introduction"
                print(f"Notice: No applicable site for {op} was found.")
                continue

            save_name = new_name if new_name else target_name

            # ── Persist results ───────────────────────────────────────────────────
            env.formulae[save_name] = new_node
            print(f"Saved formula '{save_name}': {reconstruct_string(new_node)}")

            if target_type == "formula":
                # Propagate proven status
                if target_name in env.theorems:
                    env.theorems[save_name] = clone_ast(new_node)
                    print(f"'{save_name}' is also a proven theorem.")

                # Equivalence theorem (only for formula targets)
                if equiv_name is not None:
                    f_orig = clone_ast(target_node)
                    f_new = clone_ast(new_node)
                    equiv_node = Connective(name="⇔", arity=2, arguments=[f_orig, f_new])
                    env.formulae[equiv_name] = equiv_node
                    env.theorems[equiv_name] = clone_ast(equiv_node)
                    print(f"Registered equivalence theorem '{equiv_name}': {reconstruct_string(equiv_node)}")

            elif target_type == "goal":
                env.goal_formula_name = save_name
                print(f"Goal updated to '{save_name}': {reconstruct_string(new_node)}")
                # Check if the new goal is already proven
                if save_name in env.theorems:
                    parent_env = env.parent
                    goal_name = env.goal_formula_name
                    goal_node = env.formulae[goal_name]
                    parent_env.theorems[goal_name] = clone_ast(goal_node)
                    parent_env.formulae[goal_name] = clone_ast(goal_node)
                    env = parent_env
                    print(f"Mission accomplished! Proved '{goal_name}' in parent environment.")

        else:
            print(f"Unknown command '{cmd}'. Supported commands: cv, cV, ct, cf, cp, st, sf, sb, sa, sp, def_f, def_r, iota, fold, ua, ir, dt, show, exit, mission, contra, left, right, and, and2, imply, intro, intro2, apply, apply2, apply3, help, guide, save, load, save_h, load_h, auto, simp_l_eq, simp_r_eq, simp_l_bi, simp_r_bi, neg-, neg+")
        # Record command in history if it succeeded and was entered by the user
        if not is_from_queue and not has_error:
            if cmd not in {"exit", "load_h", "save", "save_h", "help", "guide"}:
                history_commands.append(line)

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

            # If this is a contra child environment, register the target formula f1 in the parent
            if getattr(env, "target_proven_formula_name", None):
                target_name = env.target_proven_formula_name
                parent.theorems[target_name] = clone_ast(parent.formulae[target_name])
                print(f"Target formula '{target_name}' has been successfully proven in parent environment via contradiction!")
            elif and_right is not None:
                # 'and' environment: both Ψ and Φ proven → register the original conjunction in parent
                print(f"Both parts proven (Ψ='{goal_name}', Φ='{and_right}'). "
                      f"Conjunction goal '{original_goal_name}' is proven!")
                if original_goal_name in parent.formulae:
                    parent.theorems[original_goal_name] = clone_ast(parent.formulae[original_goal_name])
                else:
                    # conjunction was defined inside the child — carry the node up
                    parent.theorems[original_goal_name] = clone_ast(env.formulae[original_goal_name])
            else:
                # Normal mission / left / right: register the (possibly reduced) goal in the parent.
                parent.theorems[goal_name] = clone_ast(goal_node)
                if original_goal_name != goal_name and original_goal_name in parent.formulae:
                    parent.theorems[original_goal_name] = clone_ast(parent.formulae[original_goal_name])
                    print(f"Original mission goal '{original_goal_name}' is also proven in parent environment.")

            # Destroy the child environment and restore the parent
            env = parent
            print(f"Child environment destroyed. Returned to parent environment.")

if __name__ == "__main__":
    main()
