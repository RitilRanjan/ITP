import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "x y")
handle_cf(env, "test1 ∃x ∀y (x ∈ y)")
print("Parsed correctly!")
