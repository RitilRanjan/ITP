import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cV, handle_cp
from CommandHandlers.mission_handlers import handle_contra

env = Environment()
handle_cV(env, "P Q")
handle_cp(env, "f1 P")
handle_cp(env, "f3 Q")

env.goal_formula_name = "f1"

# Test contra with 3 args (implicit f1)
env2 = handle_contra(env, "f2 f3 f4")
print("contra 3 args env2.goal_formula_name:", env2.goal_formula_name)
if env2.goal_formula_name == "f4":
    print("Test 1 PASS")
else:
    print("Test 1 FAIL")

# Test contra with 4 args (explicit f1)
env.goal_formula_name = None
env3 = handle_contra(env, "f1 f2 f3 f4")
print("contra 4 args env3.goal_formula_name:", env3.goal_formula_name)
if env3.goal_formula_name == "f4":
    print("Test 2 PASS")
else:
    print("Test 2 FAIL")
