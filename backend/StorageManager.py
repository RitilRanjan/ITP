import os
import re
from typing import List, Tuple, Dict, Any, Optional
from backend.AST import (
    Variable, DummyVariable, MetaVariable, PropositionalVariable,
    Node
)
from backend.Parser import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError, strip_ansi
)
from backend.Environment import Environment

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
    import json
    chain = get_env_chain(env)
    
    env_configs = []
    for idx, e in enumerate(chain):
        config = {
            "goal": getattr(e, "goal_formula_name", None),
            "original_goal": getattr(e, "original_goal_formula_name", None),
            "and_right": getattr(e, "and_right_formula_name", None),
            "target_proven_formula_name": getattr(e, "target_proven_formula_name", None),
            "theory": e.theory,
            "variables": list(e.local_variables.keys()),
            "dummy_variables": list(e.local_dummy_variables.keys()),
            "meta_variables": list(e.local_meta_variables.keys()),
            "prop_variables": list(e.local_propositional_variables.keys()),
            "long_terms": [],
            "long_formulae": [],
            "constants": [],
            "terms": [],
            "formulae": [],
            "free_vars_cache": {}
        }
        
        for identifier, definition in e.local_long_terms.items():
            pattern_str = "".join(definition.pattern)
            def_str = "".join(definition.definition_tokens)
            config["long_terms"].append((identifier, pattern_str, def_str))
            
        for identifier, definition in e.local_long_formulae.items():
            pattern_str = "".join(definition.pattern)
            def_str = "".join(definition.definition_tokens)
            config["long_formulae"].append((identifier, pattern_str, def_str))
            
        for k, v in e.local_terms.items():
            from backend.AST import Constant
            if isinstance(v, Constant):
                config["constants"].append((k, reconstruct_string(v, color_mode="none")))
            else:
                config["terms"].append((k, reconstruct_string(v, color_mode="none")))
            
        for k, v in e.local_formulae.items():
            proven = 1 if k in e.local_theorems else 0
            config["formulae"].append((k, reconstruct_string(v, color_mode="none"), proven))
            
        for k, v in e.local_free_vars_cache.items():
            config["free_vars_cache"][k] = list(v)
            
        env_configs.append(config)
        
    return json.dumps(env_configs, indent=2, ensure_ascii=False)


def deserialize_environment_state(content: str, get_default_env_func) -> Environment:
    import json
    try:
        env_configs = json.loads(content)
    except json.JSONDecodeError:
        print("Failed to decode JSON environment state")
        return None
        
    active_env = None
    
    for idx, config in enumerate(env_configs):
        if idx == 0:
            theory = config.get("theory", "ZFC")
            env = get_default_env_func(theory=theory)
            env.target_proven_formula_name = config.get("target_proven_formula_name")
        else:
            theory = config.get("theory", "ZFC")
            env = Environment(
                parent=active_env,
                goal_formula_name=config.get("goal"),
                target_proven_formula_name=config.get("target_proven_formula_name"),
                theory=theory
            )
            if config.get("original_goal") is not None:
                env.original_goal_formula_name = config["original_goal"]
            if config.get("and_right") is not None:
                env.and_right_formula_name = config["and_right"]
            
        for var in config.get("variables", []):
            if var not in env.local_variables:
                env.add_variable(Variable(name=var))
        for d in config.get("dummy_variables", []):
            if d not in env.local_dummy_variables:
                env.add_dummy_variable(DummyVariable(name=d))
        for m in config.get("meta_variables", []):
            if m not in env.local_meta_variables:
                env.add_meta_variable(MetaVariable(name=m))
        for p in config.get("prop_variables", []):
            if p not in env.local_propositional_variables:
                env.add_propositional_variable(PropositionalVariable(name=p))
            
        from backend.Environment import LongDefinition
        from backend.Parser import lex
        
        for item in config.get("long_terms", []):
            if len(item) == 2:
                name, def_str = item
                pattern_str = name
                identifier = name
            else:
                identifier, pattern_str, def_str = item
            pattern = [t for t in lex(pattern_str) if not t.isspace()]
            def_tokens = [t for t in lex(def_str) if not t.isspace()]
            env.local_long_terms[identifier] = LongDefinition(name=identifier, pattern=pattern, definition_tokens=def_tokens)
            
        for item in config.get("long_formulae", []):
            if len(item) == 2:
                name, def_str = item
                pattern_str = name
                identifier = name
            else:
                identifier, pattern_str, def_str = item
            pattern = [t for t in lex(pattern_str) if not t.isspace()]
            def_tokens = [t for t in lex(def_str) if not t.isspace()]
            env.local_long_formulae[identifier] = LongDefinition(name=identifier, pattern=pattern, definition_tokens=def_tokens)
            
        for name, def_str in config.get("constants", []):
            if name not in env.local_terms:
                term_node = parse_term(def_str, env)
                env.local_terms[name] = term_node
                
        for name, def_str in config.get("terms", []):
            if name not in env.local_terms:
                term_node = parse_term(def_str, env)
                env.local_terms[name] = term_node
            
        for item in config.get("formulae", []):
            if len(item) == 3:
                name, def_str, proven = item
            else:
                name, def_str = item
                proven = 0
            if name not in env.local_formulae:
                try:
                    formula_node = parse_fol_formula(def_str, env)
                except (UnrecognizedSymbolError, ParserError):
                    formula_node = parse_prop_formula(def_str, env)
                env.local_formulae[name] = formula_node
            if proven == 1:
                env.local_theorems.add(name)
            
        for name, def_str in config.get("theorems", []):
            if name not in env.local_formulae:
                try:
                    formula_node = parse_fol_formula(def_str, env)
                except (UnrecognizedSymbolError, ParserError):
                    formula_node = parse_prop_formula(def_str, env)
                env.local_formulae[name] = formula_node
            env.local_theorems.add(name)
            
        for name, free_vars_list in config.get("free_vars_cache", {}).items():
            env.local_free_vars_cache[name] = set(free_vars_list)
            
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