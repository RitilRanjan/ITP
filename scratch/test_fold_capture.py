import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from CommandHandlers.mission_handlers import handle_mission
from CommandHandlers.transformation_handlers import handle_fold
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "C x")
handle_cf(env, "f1 ∀C (¬¬ {x∈C | ¬ x∈x} ∈ C)")
env = handle_mission(env, "f1")

import io
sys.stdin = io.StringIO("y\n")

try:
    handle_fold(env, "all f1 f2")
    print(reconstruct_string(env.formulae["f2"]))
except Exception as e:
    print(f"Error: {e}")
