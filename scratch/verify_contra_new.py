import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from CommandHandlers.mission_handlers import handle_contra
from CommandHandlers.logic_handlers import handle_apply
from Frontend import reconstruct_string

env = Environment()
from CommandHandlers.env_handlers import handle_cv, handle_cf
handle_cv(env, "A")
handle_cf(env, "goal A ∈ A")
env.goal_formula_name = "goal"

# Test contra
child_env = handle_contra(env, "goal p_not_A contradiction")
print("Target proven:", child_env.target_proven_formula_name)
print("Goal formula:", reconstruct_string(child_env.formulae["contradiction"], color_mode="none"))
print("Assumed premise:", reconstruct_string(child_env.formulae["p_not_A"], color_mode="none"))

# Now prove contradiction using a tautological premise
handle_cf(child_env, "my_premise ¬(A ∈ A) ∧ (A ∈ A)")
child_env.add_theorem("my_premise")

# Apply
handle_apply(child_env, "contradiction PC1 my_premise")
if "contradiction" in child_env.theorems:
    print("Contradiction proven successfully!")
else:
    print("Failed to prove contradiction.")
