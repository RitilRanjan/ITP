import sys
import os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.transformation_handlers import handle_fold
from CommandHandlers.definition_handlers import handle_def_r
from CommandHandlers.env_handlers import handle_cv, handle_cf
from CommandHandlers.mission_handlers import handle_mission
env = Environment()
handle_cv(env, "z A B")
handle_def_r(env, "2 x∉y ¬x∈y")
handle_cf(env, "lemma {x∈A | x∉x} ∉ A")
env2 = handle_mission(env, "lemma")
handle_fold(env2, "fold all")
print("Goal after fold all:", env2.goal_formula_name)
from Frontend import reconstruct_string
print("Formula:", reconstruct_string(env2.formulae[env2.goal_formula_name]))
