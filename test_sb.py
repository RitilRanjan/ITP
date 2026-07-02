from parser.parser import Parser
from core.environment import Environment
from core.registry import Registry
from commands.definitions import define_formula
from commands.substitutions import substitute_bound_variable

env = Environment()
registry = Registry()
# Let's see if we can dispatch sb
env = define_formula(env, "f1", "x \\in y")
try:
    print("Trying to run sb f1 1 t1")
    new_env = substitute_bound_variable(env, "x", "t1", 1, "f1", None, None)
except Exception as e:
    print(f"Caught Exception: {e}")
