import os
import re
from typing import List, Tuple, Dict, Any, Optional
from AST import (
    Variable, DummyVariable, MetaVariable, PropositionalVariable,
    Function, FunctionType, Relation, RelationType, Node
)
from Frontend import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError, strip_ansi
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

def serialize_environment_state(env: Environment) -> str:
    """Serializes the entire environment stack into a human-readable Markdown format and returns it as a string."""
    chain = get_env_chain(env)
    
    import io
    f = io.StringIO()
    f.write("# Environment State\n\n")
    f.write("This file contains the saved state of the theorem prover.\n\n")
    
    # 1. Write the pretty HTML summary
    for idx, e in enumerate(chain):
        if e.parent is None:
            header = "Ground Environment"
        else:
            orig = getattr(e, "original_goal_formula_name", e.goal_formula_name)
            ar = getattr(e, "and_right_formula_name", None)
            if orig != e.goal_formula_name and ar:
                header = f"Child Environment (Original: {orig} &rarr; &Psi;: {e.goal_formula_name}, &Phi;: {ar})"
            elif orig != e.goal_formula_name:
                header = f"Child Environment (Original: {orig} &rarr; Current: {e.goal_formula_name})"
            else:
                header = f"Child Environment (Goal: {e.goal_formula_name})"
                
        f.write(f"## {header}\n\n")
        
        # Formulate lists
        f.write(f"- **Variables**: {', '.join(e.local_variables.keys()) or 'None'}\n")
        f.write(f"- **Theorems**: {len(e.local_theorems)}\n\n")
        
        # Print proven theorems beautifully
        if e.local_theorems:
            f.write("### Proven Theorems\n")
            for k in e.local_theorems:
                v = e.local_formulae[k]
                f.write(f"- **{k}**: {reconstruct_string(v, color_mode='html')}\n")
            f.write("\n")
            
        f.write("---\n\n")
        
    # 2. Write the machine-readable ITP block
    f.write("## Data Payload\n")
    f.write("```itp\n")
    for idx, e in enumerate(chain):
        f.write(f"[Environment {idx}]\n")
        f.write(f"Goal: {e.goal_formula_name}\n")
        f.write(f"Original Goal: {e.original_goal_formula_name}\n")
        f.write(f"And Right: {e.and_right_formula_name}\n")
        f.write(f"Target Proven: {e.target_proven_formula_name}\n")
        
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
            def_str = reconstruct_string(definition, color_mode="none")
            f.write(f"  {name} | {arity} | {func_type} | {def_str}\n")
            
        # User Relations
        f.write("User Relations:\n")
        for name, (arity, definition) in e.local_user_relations.items():
            def_str = reconstruct_string(definition, color_mode="none")
            f.write(f"  {name} | {arity} | {def_str}\n")
            
        # Terms
        f.write("Terms:\n")
        for name, term_node in e.local_terms.items():
            if is_ground and name in {"S", "+"}: continue
            if isinstance(term_node, Function) and name == term_node.name: continue
            def_str = reconstruct_string(term_node, color_mode="none")
            f.write(f"  {name} | {def_str}\n")
            
        # Formulae
        f.write("Formulae:\n")
        for name, formula_node in e.local_formulae.items():
            if is_ground and name in {"=", "∈"}: continue
            if isinstance(formula_node, Relation) and name == formula_node.name: continue
            def_str = reconstruct_string(formula_node, color_mode="none")
            f.write(f"  {name} | {def_str}\n")
            
        # Theorems
        f.write("Theorems:\n")
        for name in e.local_theorems:
            theorem_node = e.local_formulae[name]
            def_str = reconstruct_string(theorem_node, color_mode="none")
            f.write(f"  {name} | {def_str}\n")
            
        f.write("\n")
    f.write("```\n")
    return f.getvalue()

def deserialize_environment_state(full_content: str, get_default_env_func) -> Environment:
    """Loads and reconstructs the environment stack from a saved markdown string."""
        
    # Extract the payload inside ```itp ... ```
    match = re.search(r"```itp\n(.*?)```", full_content, re.DOTALL)
    if match:
        payload = match.group(1)
        lines = payload.splitlines()
    else:
        # Fallback to reading the whole file in case it's an old save
        lines = full_content.splitlines()
        
    env_configs = []
    curr_config = None
    curr_section = None
    
    for line in lines:
        line_stripped = strip_ansi(line).strip()
        if not line_stripped:
            continue
            
        # Parse environment boundary
        if line_stripped.startswith("[Environment ") and line_stripped.endswith("]"):
            curr_config = {
                "goal": None,
                "original_goal": None,
                "and_right": None,
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
        elif line_stripped.startswith("Original Goal:"):
            og_val = line_stripped.split(":", 1)[1].strip()
            curr_config["original_goal"] = None if og_val == "None" or not og_val else og_val
            curr_section = None
        elif line_stripped.startswith("And Right:"):
            ar_val = line_stripped.split(":", 1)[1].strip()
            curr_config["and_right"] = None if ar_val == "None" or not ar_val else ar_val
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
        elif line_stripped.startswith("Theorems:"):
            curr_section = "theorems"
        elif strip_ansi(line).startswith("  ") or strip_ansi(line).startswith("\t"):
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
            # Restore original goal and and_right if present
            if config.get("original_goal") is not None:
                env.original_goal_formula_name = config["original_goal"]
            if config.get("and_right") is not None:
                env.and_right_formula_name = config["and_right"]
            
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
            if name not in env.local_formulae:
                try:
                    theorem_node = parse_fol_formula(def_str, env)
                except (UnrecognizedSymbolError, ParserError):
                    theorem_node = parse_prop_formula(def_str, env)
                env.local_formulae[name] = theorem_node
            env.local_theorems.add(name)
        active_env = env
        
    return active_env

def serialize_history(commands: List[str]) -> str:
    import io
    f = io.StringIO()
    f.write("# Command History\n\n")
    f.write("```\n")
    for cmd in commands:
        f.write(cmd + "\n")
    f.write("```\n")
    return f.getvalue()

def deserialize_history(content: str) -> List[str]:
    match = re.search(r"```\n(.*?)```", content, re.DOTALL)
    if match:
        lines = match.group(1).splitlines()
    else:
        lines = content.splitlines()
        
    commands = []
    for line in lines:
        cleaned = strip_ansi(line).strip()
        if cleaned and not cleaned.startswith("#"):
            commands.append(cleaned)
    return commands
