import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "y A")
handle_cf(env, "f1 ∀y (y ∈ A)")
handle_cf(env, "f2 ∃y (y ∈ A)")

q1 = env.formulae["f1"]
body1 = q1.formula
print("q1:", reconstruct_string(q1, color_mode="none"))
print("body1 prefix:", body1.prefix_formatting)
print("body1 postfix:", body1.postfix_formatting)

q2 = env.formulae["f2"]
body2 = q2.formula
print("q2:", reconstruct_string(q2, color_mode="none"))
print("body2 prefix:", body2.prefix_formatting)
print("body2 postfix:", body2.postfix_formatting)
