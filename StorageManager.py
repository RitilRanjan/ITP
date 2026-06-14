import os
from typing import List, Tuple, Dict, Any, Optional
from AST import (
    Variable, DummyVariable, MetaVariable, PropositionalVariable,
    Function, FunctionType, Relation, RelationType, Node
)
from Frontend import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError
)
from Environment import Environment

def get_env_chain(env: Environment) -> List[Environment]:
    """Returns a list of environments in the stack, from ground (index 0) to active (index -1)."""
    chain = []
    curr = env
    while curr is not None:
        chain.append(curr)
        curr = curr.parent
    chain.reverse()
    return chain

def save_environment_state(env: Environment, filepath: str) -> None:
    """Serializes the entire environment stack into a human-readable text format."""
    chain = get_env_chain(env)
    
    with open(filepath, "w", encoding="utf-8") as f:
        for idx, e in enumerate(chain):
            f.write(f"[Environment {idx}]\n")
            f.write(f"Goal: {e.goal_formula_name}\n")
            f.write(f"Target Proven: {e.target_proven_formula_name}\n")
            
            # For the ground environment, filter out pre-defined defaults.
            # Variables x, y, S, +, =, ∈, p, q.
            is_ground = (idx == 0)
            
            # Variables
            vars_list = []
            for name in e.local_variables.keys():
                if is_ground and name in {"x", "y"}:
                    continue
                vars_list.append(name)
            f.write(f"Variables: {', '.join(vars_list)}\n")
            
            # Dummy Variables
            dummies = list(e.local_dummy_variables.keys())
            f.write(f"Dummy Variables: {', '.join(dummies)}\n")
            
            # Meta Variables
            metas = list(e.local_meta_variables.keys())
            f.write(f"Meta Variables: {', '.join(metas)}\n")
            
            # Propositional Variables
            props_list = []
            for name in e.local_propositional_variables.keys():
                if is_ground and name in {"p", "q"}:
                    continue
                props_list.append(name)
            f.write(f"Propositional Variables: {', '.join(props_list)}\n")
            
            # User Functions
            f.write("User Functions:\n")
            for name, (arity, definition) in e.local_user_functions.items():
                func_node = e.local_terms.get(name)
                func_type = func_node.func_type.name if func_node else "USER_DEFINED"
                def_str = reconstruct_string(definition)
                f.write(f"  {name} | {arity} | {func_type} | {def_str}\n")
                
            # User Relations
            f.write("User Relations:\n")
            for name, (arity, definition) in e.local_user_relations.items():
                def_str = reconstruct_string(definition)
                f.write(f"  {name} | {arity} | {def_str}\n")
                
            # Terms (excluding function declarations and pre-defined symbols)
            f.write("Terms:\n")
            for name, term_node in e.local_terms.items():
                # Skip pre-defined function symbols in ground env
                if is_ground and name in {"S", "+"}:
                    continue
                # Skip function declarations
                if isinstance(term_node, Function) and name == term_node.name:
                    continue
                def_str = reconstruct_string(term_node)
                f.write(f"  {name} | {def_str}\n")
                
            # Formulae (excluding relation declarations and pre-defined symbols)
            f.write("Formulae:\n")
            for name, formula_node in e.local_formulae.items():
                # Skip pre-defined relation symbols in ground env
                if is_ground and name in {"=", "∈"}:
                    continue
                # Skip relation declarations
                if isinstance(formula_node, Relation) and name == formula_node.name:
                    continue
                def_str = reconstruct_string(formula_node)
                f.write(f"  {name} | {def_str}\n")
                
            # Theorems
            f.write("Theorems:\n")
            for name, theorem_node in e.local_theorems.items():
                def_str = reconstruct_string(theorem_node)
                f.write(f"  {name} | {def_str}\n")
                
            f.write("\n")

def load_environment_state(filepath: str, get_default_env_func) -> Environment:
    """Loads and reconstructs the environment stack from a saved file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"State file '{filepath}' not found.")
        
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    env_configs = []
    curr_config = None
    curr_section = None
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Parse environment boundary
        if line_stripped.startswith("[Environment ") and line_stripped.endswith("]"):
            curr_config = {
                "goal": None,
                "target_proven_formula_name": None,
                "variables": [],
                "dummy_variables": [],
                "meta_variables": [],
                "prop_variables": [],
                "user_functions": [],
                "user_relations": [],
                "terms": [],
                "formulae": [],
                "theorems": []
            }
            env_configs.append(curr_config)
            curr_section = None
            continue
            
        if curr_config is None:
            continue
            
        # Parse fields
        if line_stripped.startswith("Goal:"):
            goal_val = line_stripped.split(":", 1)[1].strip()
            curr_config["goal"] = None if goal_val == "None" or not goal_val else goal_val
            curr_section = None
        elif line_stripped.startswith("Target Proven:"):
            target_val = line_stripped.split(":", 1)[1].strip()
            curr_config["target_proven_formula_name"] = None if target_val == "None" or not target_val else target_val
            curr_section = None
        elif line_stripped.startswith("Variables:"):
            val = line_stripped.split(":", 1)[1].strip()
            curr_config["variables"] = [v.strip() for v in val.split(",") if v.strip()]
            curr_section = None
        elif line_stripped.startswith("Dummy Variables:"):
            val = line_stripped.split(":", 1)[1].strip()
            curr_config["dummy_variables"] = [v.strip() for v in val.split(",") if v.strip()]
            curr_section = None
        elif line_stripped.startswith("Meta Variables:"):
            val = line_stripped.split(":", 1)[1].strip()
            curr_config["meta_variables"] = [v.strip() for v in val.split(",") if v.strip()]
            curr_section = None
        elif line_stripped.startswith("Propositional Variables:"):
            val = line_stripped.split(":", 1)[1].strip()
            curr_config["prop_variables"] = [v.strip() for v in val.split(",") if v.strip()]
            curr_section = None
        elif line_stripped == "User Functions:":
            curr_section = "user_functions"
        elif line_stripped == "User Relations:":
            curr_section = "user_relations"
        elif line_stripped == "Terms:":
            curr_section = "terms"
        elif line_stripped == "Formulae:":
            curr_section = "formulae"
        elif line_stripped == "Theorems:":
            curr_section = "theorems"
        elif line.startswith("  ") or line.startswith("\t"):
            # Indented list items
            if curr_section == "user_functions":
                parts = [p.strip() for p in line_stripped.split("|")]
                if len(parts) == 4:
                    curr_config["user_functions"].append((parts[0], int(parts[1]), parts[2], parts[3]))
            elif curr_section == "user_relations":
                parts = [p.strip() for p in line_stripped.split("|")]
                if len(parts) == 3:
                    curr_config["user_relations"].append((parts[0], int(parts[1]), parts[2]))
            elif curr_section == "terms":
                parts = [p.strip() for p in line_stripped.split("|", 1)]
                if len(parts) == 2:
                    curr_config["terms"].append((parts[0], parts[1]))
            elif curr_section == "formulae":
                parts = [p.strip() for p in line_stripped.split("|", 1)]
                if len(parts) == 2:
                    curr_config["formulae"].append((parts[0], parts[1]))
            elif curr_section == "theorems":
                parts = [p.strip() for p in line_stripped.split("|", 1)]
                if len(parts) == 2:
                    curr_config["theorems"].append((parts[0], parts[1]))
                    
    # Reconstruct environment stack
    active_env = None
    
    for idx, config in enumerate(env_configs):
        if idx == 0:
            env = get_default_env_func()
            # Restore ground level target_proven_formula_name if any
            env.target_proven_formula_name = config.get("target_proven_formula_name")
        else:
            env = Environment(
                parent=active_env,
                goal_formula_name=config["goal"],
                target_proven_formula_name=config.get("target_proven_formula_name")
            )
            
        # Populate objects in order of dependencies
        # 1. Variables
        for var in config["variables"]:
            env.add_variable(Variable(name=var))
        # 2. Dummy variables
        for d in config["dummy_variables"]:
            env.add_dummy_variable(DummyVariable(name=d))
        # 3. Meta variables
        for m in config["meta_variables"]:
            env.add_meta_variable(MetaVariable(name=m))
        # 4. Propositional variables
        for p in config["prop_variables"]:
            env.add_propositional_variable(PropositionalVariable(name=p))
            
        # 5. User functions
        for name, arity, type_str, def_str in config["user_functions"]:
            definition = parse_term(def_str, env)
            env.user_functions[name] = (arity, definition)
            # Register function declaration node in terms
            decl_node = Function(
                name=name,
                arity=arity,
                func_type=FunctionType[type_str],
                arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
            )
            env.local_terms[name] = decl_node
            
        # 6. User relations
        for name, arity, def_str in config["user_relations"]:
            definition = parse_fol_formula(def_str, env)
            env.user_relations[name] = (arity, definition)
            # Register relation declaration node in formulae
            decl_node = Relation(
                name=name,
                arity=arity,
                rel_type=RelationType.USER_DEFINED,
                arguments=[DummyVariable(name=f"_{i+1}") for i in range(arity)]
            )
            env.local_formulae[name] = decl_node
            
        # 7. Terms
        for name, def_str in config["terms"]:
            term_node = parse_term(def_str, env)
            env.local_terms[name] = term_node
            
        # 8. Formulae
        for name, def_str in config["formulae"]:
            try:
                formula_node = parse_fol_formula(def_str, env)
            except (UnrecognizedSymbolError, ParserError):
                formula_node = parse_prop_formula(def_str, env)
            env.local_formulae[name] = formula_node
            
        # 9. Theorems
        for name, def_str in config["theorems"]:
            try:
                theorem_node = parse_fol_formula(def_str, env)
            except (UnrecognizedSymbolError, ParserError):
                theorem_node = parse_prop_formula(def_str, env)
            env.local_theorems[name] = theorem_node
            
        active_env = env
        
    return active_env

def save_history(commands: List[str], filepath: str) -> None:
    """Saves a list of commands in sequence to a history file."""
    with open(filepath, "w", encoding="utf-8") as f:
        for cmd in commands:
            f.write(cmd + "\n")

def load_history(filepath: str) -> List[str]:
    """Loads and returns all executable commands from a history file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"History file '{filepath}' not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # strip whitespace and skip empty lines or comments
    commands = []
    for line in lines:
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            commands.append(cleaned)
    return commands
