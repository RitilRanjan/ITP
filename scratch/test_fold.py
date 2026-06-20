import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from CommandHandlers.transformation_handlers import handle_fold
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "x y A B")
handle_cf(env, "test1 ∀y ¬ y ∈ A")

print("Before fold ∀:", reconstruct_string(env.formulae["test1"]))
handle_fold(env, "∀ test1 folded1")
print("After fold ∀:", reconstruct_string(env.formulae["folded1"]))
