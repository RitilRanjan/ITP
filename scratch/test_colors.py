import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cf
from Frontend import reconstruct_string

env = Environment()
handle_cf(env, "f1 ((((A ⇒ B) ∧ C) ∨ D) ⇔ E)")
print("Output:", reconstruct_string(env.formulae["f1"]))
