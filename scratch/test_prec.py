import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "u x y")
handle_cf(env, "test1 ∃u (u ∈ x) ∧ (u ∈ y)")
print("AST test1:", env.formulae["test1"].name)
if hasattr(env.formulae["test1"], "arguments"):
    print("Arguments:", [type(a) for a in env.formulae["test1"].arguments])
