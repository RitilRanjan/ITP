import sys, os
sys.path.append(os.path.abspath("."))
import pickle
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv
from CommandHandlers.mission_handlers import handle_mission

env = Environment()
handle_cv(env, "x y")
env = handle_mission(env, "goal x ∈ y")

try:
    with open("scratch/test_pickle.pkl", "wb") as f:
        pickle.dump(env, f)
    with open("scratch/test_pickle.pkl", "rb") as f:
        env_loaded = pickle.load(f)
    print("Pickle successful!")
    print("Loaded goal:", env_loaded.goal_formula_name)
    print("Loaded parent vars:", list(env_loaded.parent.local_variables.keys()))
except Exception as e:
    print("Pickle failed:", e)
