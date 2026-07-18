import json

with open("games/natural number game/level6_start_env.json", "r") as f:
    data = json.load(f)

for env_config in data:
    env_config["dummy_variables"] = []
    env_config["prop_variables"] = []
    env_config["meta_variables"] = []
    
    if "terms" in env_config:
        env_config["constants"] = []
        new_terms = []
        for term in env_config["terms"]:
            if term[0] == "0":
                env_config["constants"].append(term)
            else:
                new_terms.append(term)
        env_config["terms"] = new_terms
        
    if "formulae" in env_config:
        new_formulae = []
        for fml in env_config["formulae"]:
            # Check if it was in theorems
            is_proven = 0
            if "theorems" in env_config:
                for thm in env_config["theorems"]:
                    if thm[0] == fml[0]:
                        is_proven = 1
                        break
            new_formulae.append([fml[0], fml[1], is_proven])
        env_config["formulae"] = new_formulae
        
    if "theorems" in env_config:
        del env_config["theorems"]

with open("games/natural number game/level6_start_env.json", "w") as f:
    json.dump(data, f, indent=2)

print("Done")
