from typing import Callable, Tuple, List, Optional
from Environment import Environment
from AST import Variable
from Frontend import reconstruct_string

def get_user_input(prompt: str, command_queue: list = None, inputs_collected: list = None) -> str:
    """Helper to fetch input interactively or from queue, and record it."""
    if command_queue:
        ans = command_queue.pop(0)
        print(f"{prompt}{ans}")
    else:
        ans = input(prompt).strip()
    if inputs_collected is not None:
        inputs_collected.append(ans)
    return ans

def validate_new_name(env: Environment, name: str, allowed_category: Optional[str] = None) -> bool:
    from Frontend import LOGICAL_CONNECTIVES, QUANTIFIERS
    if name in LOGICAL_CONNECTIVES or name in QUANTIFIERS or name in ("⊤", "⊥", "ε", "ι"):
        print(f"Error: Logical symbols like '{name}' cannot be used as names.")
        return False
    if "ε" in name or "ι" in name:
        print("Error: Name cannot contain 'ε' or 'ι'.")
        return False
    if "," in name:
        print("Error: Name cannot contain commas.")
        return False
    if ":" in name:
        print("Error: Name cannot contain colons (:).")
        return False
    if any(c.isspace() for c in name):
        print("Error: Name cannot contain whitespace, tab, or newline characters.")
        return False
    if name.startswith("_"):
        if allowed_category != "dummy_variable":
            print("Error: Names starting with '_' are reserved for dummy variables only.")
            return False
    if name.startswith("?"):
        if allowed_category != "meta_variable":
            print("Error: Names starting with '?' are reserved for meta variables only.")
            return False
            
    if name.isdigit():
        if allowed_category != "term":
            print("Error: Pure digits can only be used to name terms.")
            return False
            
    clash = False
    if name in env.variables:
        clash = True
    if name in env.dummy_variables:
        clash = True
    if name in env.meta_variables:
        clash = True
    if name in env.terms:
        clash = True
    if name in env.propositional_variables:
        clash = True
    if name in env.formulae:
        clash = True
        
    if clash:
        print(f"Error: Name '{name}' is already in use by another environment object.")
        return False
    return True

def resolve_term(env: Environment, term_name: str):
    """Resolves a term name to its AST node. Works for defined terms and variables."""
    from SubstitutionManager import clone_ast
    if term_name in env.terms:
        return clone_ast(env.terms[term_name])
    if term_name in env.variables:
        from AST import Variable
        return Variable(term_name)
    return None

def get_target_resolutions(env: Environment, f1: str, is_term: bool):
    registry = env.terms if is_term else env.formulae
    local_registry = env.local_terms if is_term else env.local_formulae
    
    if f1 not in registry:
        if env.parent is None:
            raise ValueError(f"Cannot target active goal because ground environment has no active goal.")
        return [(env.goal_formula_name, f1, False, False)]
        
    if f1 not in local_registry:
        if env.parent is None:
            raise ValueError(f"Cannot target active goal because ground environment has no active goal.")
        return [(env.goal_formula_name, f1, False, False)]
        
    if env.parent is None:
        return [(f1, f1, True, False)]
        
    if f1 == env.goal_formula_name:
        return [(f1, f1, True, False)]
        
    return [
        (env.goal_formula_name, f1, True, True),
        (f1, f1, True, False)
    ]

def handle_variable_capture_interactive(env: Environment, e: Exception, f_clone, symbol: str, command_queue: list = None, inputs_collected: list = None):
    print(f"Variable capture detected! Expanded form would be: {reconstruct_string(e.expanded_ast)}")
    for cap_var in e.capturing_vars:
        while True:
            new_name = get_user_input(f"Enter replacement variable for capturing variable '{cap_var}': ", command_queue, inputs_collected)
            if not validate_new_name(env, new_name, "variable"):
                continue
            if new_name not in env.variables:
                env.add_variable(Variable(new_name))
                print(f"Created new variable '{new_name}'.")
            
            from SubstitutionManager import substitute_bound
            substitute_bound(f_clone, cap_var, Variable(new_name), None)
            print(f"Replaced capturing variable '{cap_var}' with '{new_name}'.")
            break
    return f_clone
def parse_occurrences(args: List[str], start_idx: int) -> Tuple[Optional[List[int]], int]:
    if start_idx >= len(args): return None, start_idx
    if not args[start_idx].isdigit(): return None, start_idx
    occs = []
    idx = start_idx
    expect_number = True
    while idx < len(args):
        token = args[idx]
        if expect_number:
            if token.isdigit():
                occs.append(int(token))
                expect_number = False
                idx += 1
            else: break
        else:
            if token == ',':
                expect_number = True
                idx += 1
            else: break
    if expect_number and len(occs) > 0: idx -= 1
    return occs, idx

def parse_universal_args(
    env: Environment, 
    cmd_name: str, 
    cmd_args: List[str], 
    fixed_args_count: int, 
    validate_new_name: Callable, 
    supports_equiv: bool = True,
    namespace: str = "formula"
) -> Optional[Tuple[List[str], Optional[List[int]], str, str, Optional[str]]]:
    """
    Parses a command that follows the universal fold syntax:
    command <fixed_args...> [occurrences] [<target>] [<out>] [<equiv>]
    
    If successful, returns:
    (fixed_args, occs, target_name, out_name, equiv_name)
    If parsing fails, prints an error and returns None.
    """
    if len(cmd_args) < fixed_args_count:
        args_format = " ".join([f"<arg{i+1}>" for i in range(fixed_args_count)])
        print(f"Error: Usage: {cmd_name} {args_format} [occurrences] [<target>] [<out>]" + (" [<equiv>]" if supports_equiv else ""))
        return None
        
    fixed_args = cmd_args[:fixed_args_count]
    remaining = cmd_args[fixed_args_count:]
    
    occs, idx = parse_occurrences(remaining, 0)
    if occs is not None:
        if 0 in occs: occs = None
        remaining = remaining[idx:]
        
    target_name = None
    out_name = None
    equiv_name = None
    
    # Determine the namespace to check against
    if namespace == "term":
        global_dict = env.terms
        local_dict = env.local_terms
        default_target = None
    else:
        global_dict = env.formulae
        local_dict = env.local_formulae
        default_target = env.goal_formula_name
        
    # Anti-greedy rollback for ambiguity resolution
    if occs is not None and len(remaining) == 0 and default_target is None:
        if len(occs) == 1:
            # The only parsed occurrence was actually the target term
            remaining.append(str(occs.pop()))
            occs = None
        elif len(occs) > 1:
            # The last parsed occurrence was the target term
            remaining.append(str(occs.pop()))
    
    if len(remaining) == 0:
        if default_target is None:
            print(f"Error: No target specified and no active goal to default to.")
            return None
        target_name = default_target
        out_name = default_target
    elif len(remaining) == 1:
        # 1-argument rule: if the argument is a local variable, modify in-place
        # Otherwise, treat it as the output name for the default target (e.g. goal)
        if remaining[0] in local_dict:
            target_name = remaining[0]
            out_name = remaining[0]
        else:
            if default_target is None:
                print(f"Error: No target specified and no active goal to default to.")
                return None
            target_name = default_target
            out_name = remaining[0]
    elif len(remaining) == 2:
        target_name = remaining[0]
        out_name = remaining[1]
    elif len(remaining) >= 3:
        target_name = remaining[0]
        out_name = remaining[1]
        equiv_name = remaining[2]
        
    if target_name not in global_dict:
        print(f"Error: Target {namespace} '{target_name}' not found.")
        return None
        
    if out_name != target_name and out_name in global_dict:
        print(f"Error: Output {namespace} '{out_name}' already exists.")
        return None
        
    if target_name == out_name:
        if target_name not in local_dict:
            print(f"Error: Cannot modify '{target_name}' in-place because it is not defined in the current local environment. Provide an explicit <out> name.")
            return None
            
    if out_name != target_name and not validate_new_name(env, out_name, namespace):
        return None
        
    if equiv_name is not None:
        if not supports_equiv:
            print(f"Error: Command {cmd_name} does not support an <equiv> argument.")
            return None
        if equiv_name in env.formulae:
            print(f"Error: Equivalence formula '{equiv_name}' already exists.")
            return None
        if not validate_new_name(env, equiv_name, "formula"):
            return None
            
    return fixed_args, occs, target_name, out_name, equiv_name
