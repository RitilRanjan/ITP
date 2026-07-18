import sys
from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from main import get_default_env

env = get_default_env("ZFC")
registry.dispatch("cv", env, "A B C", get_default_env=get_default_env)
registry.dispatch("cf", env, "goal A = B", get_default_env=get_default_env)
print("Goal:", env.formulae["goal"].name)
