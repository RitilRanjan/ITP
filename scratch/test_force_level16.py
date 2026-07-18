import sys
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from main import get_default_env

env = get_default_env("ZFC")
registry.dispatch("cv", env, "x y", get_default_env=get_default_env)
registry.dispatch("cf", env, "theorem_1 ∃y ∀x x ∈ y", get_default_env=get_default_env)
registry.dispatch("force", env, "theorem_1", get_default_env=get_default_env)
print("Theorems:", list(env.theorems.keys()))
