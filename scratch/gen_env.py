from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_cv, handle_ct, handle_cf
from backend.Registry import AXIOMS
import json

def gen_env(vars_str, formulae):
    env = Environment()
    env.theory = "ZFC"
    env.theorems.update(AXIOMS)
    handle_cv(env, vars_str)
    handle_cf(env, 'subset "?t1 ⊆ ?t2" ∀?v3 (?v3 ∈ ?t1 ⇒ ?v3 ∈ ?t2)')
    for f in formulae:
        handle_cf(env, f)
    
    state = []
    curr = env
    while curr is not None:
        layer = {
            "goal": None,
            "original_goal": None,
            "and_right": None,
            "target_proven_formula_name": None,
            "theory": curr.theory,
            "variables": list(curr.variables.keys()),
            "dummy_variables": [],
            "meta_variables": [],
            "prop_variables": [],
            "user_functions": [],
            "user_relations": [],
            "terms": [],
            "formulae": [[k, getattr(v, 'original_string', v.__str__()), 0] for k, v in curr.formulae.items()],
            "constants": [],
            "long_terms": [],
            "long_formulae": [[k, v.name, v.pattern, v.definition_tokens, v.def_type.name, v.priority] for k, v in curr.long_formulae.items()]
        }
        state.append(layer)
        curr = curr.parent
    return json.dumps(state, indent=2)

print("Level 3:")
with open("games/Set Theory/level3_start_env.json", "w") as f:
    f.write(gen_env("A B C", ["goal (A⊆B ∧ B⊆C) ⇒ A⊆C"]))

print("Level 4:")
with open("games/Set Theory/level4_start_env.json", "w") as f:
    f.write(gen_env("A B", ["goal (A⊆B ∧ B⊆A) ⇒ A=B"]))
