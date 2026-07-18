import sys
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry

def get_default_env(theory="ZFC"):
    return Environment(theory=theory)

env = get_default_env()
print("CV output:")
registry.dispatch("cv", env, "A B C", get_default_env=get_default_env)
print("CF subset output:")
registry.dispatch("cf", env, "subset \"?t1 ⊆ ?t2\" ∀?v3 (?v3 ∈ ?t1 ⇒ ?v3 ∈ ?t2)", get_default_env=get_default_env)
print("CF goal output:")
registry.dispatch("cf", env, "goal A ⊆ B ⇒ A ⊆ C", get_default_env=get_default_env)

print("Formulae:", list(env.formulae.keys()))
print("Long Formulae:", list(env.long_formulae.keys()))
