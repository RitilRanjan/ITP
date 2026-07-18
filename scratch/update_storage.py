import re
import ast

with open("backend/StorageManager.py", "r") as f:
    content = f.read()

# Modify serialize_environment_state
content = content.replace('"terms": [],\n            "formulae": [],\n            "theorems": []', '"constants": [],\n            "terms": [],\n            "formulae": []')

content = content.replace("""        for k, v in e.local_terms.items():
            config["terms"].append((k, str(v)))
            
        for k, v in e.local_formulae.items():
            config["formulae"].append((k, str(v)))
            
        for k in e.local_theorems:
            v = e.local_formulae[k]
            config["theorems"].append((k, str(v)))""", """        for k, v in e.local_terms.items():
            from backend.AST import Constant
            if isinstance(v, Constant):
                config["constants"].append((k, str(v)))
            else:
                config["terms"].append((k, str(v)))
            
        for k, v in e.local_formulae.items():
            proven = 1 if k in e.local_theorems else 0
            config["formulae"].append((k, str(v), proven))""")


# Modify deserialize_environment_state
content = content.replace("""        for name, def_str in config.get("terms", []):
            if name not in env.local_terms:
                term_node = parse_term(def_str, env)
                env.local_terms[name] = term_node
            
        for name, def_str in config.get("formulae", []):
            if name not in env.local_formulae:
                try:
                    formula_node = parse_fol_formula(def_str, env)
                except (UnrecognizedSymbolError, ParserError):
                    formula_node = parse_prop_formula(def_str, env)
                env.local_formulae[name] = formula_node
            
        for name, def_str in config.get("theorems", []):
            if name not in env.local_formulae:
                try:
                    theorem_node = parse_fol_formula(def_str, env)
                except (UnrecognizedSymbolError, ParserError):
                    theorem_node = parse_prop_formula(def_str, env)
                env.local_formulae[name] = theorem_node
            env.local_theorems.add(name)""", """        for name, def_str in config.get("constants", []):
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
                    theorem_node = parse_fol_formula(def_str, env)
                except (UnrecognizedSymbolError, ParserError):
                    theorem_node = parse_prop_formula(def_str, env)
                env.local_formulae[name] = theorem_node
            env.local_theorems.add(name)""")

with open("backend/StorageManager.py", "w") as f:
    f.write(content)

with open("app.py", "r") as f:
    app_content = f.read()

app_content = app_content.replace("""                        with open(level_path, "r") as f:
                            level_data = json.load(f)
                        
                        level_id = f"{selected_game}/{level}\"""", """                        with open(level_path, "r") as f:
                            level_data = json.load(f)
                        
                        if not isinstance(level_data, dict):
                            continue
                            
                        level_id = f"{selected_game}/{level}\"""")

with open("app.py", "w") as f:
    f.write(app_content)

print("Done")
