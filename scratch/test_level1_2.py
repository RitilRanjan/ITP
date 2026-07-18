from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_cv, handle_ct, handle_cf
from backend.CommandHandlers.logic_handlers import handle_apply, handle_intro
from backend.CommandHandlers.mission_handlers import handle_mission
from backend.CommandHandlers.transformation_handlers import handle_rw
from backend.Registry import AXIOMS
import traceback
import builtins

# Mock user input
input_iter = iter(["x"])
def mock_input(prompt, *args):
    return next(input_iter)
import backend.CommandHandlers.utils
backend.CommandHandlers.utils.get_user_input = mock_input

env = Environment()
env.theory = "ZFC"
env.theorems.update(AXIOMS)

try:
    print("Testing Level 1:")
    handle_cv(env, "x A B")
    handle_cf(env, "goal ∀x(x∈A ⇔ x∈B) ⇒ A=B")
    handle_apply(env, "goal extension")
    print("Level 1 Success")
except Exception as e:
    traceback.print_exc()

env = Environment()
env.theory = "ZFC"
env.theorems.update(AXIOMS)

try:
    print("\nTesting Level 2:")
    handle_cv(env, "A")
    handle_cf(env, 'subset "?t1 ⊆ ?t2" ∀?v3 (?v3 ∈ ?t1 ⇒ ?v3 ∈ ?t2)')
    handle_cf(env, "goal A ⊆ A")
    env = handle_mission(env, "goal")
    
    # Try rw
    handle_rw(env, '"subset"')
    
    res_env = handle_intro(env, "y")
    if res_env: env = res_env
    
    handle_apply(env, "PC1")
    print("Level 2 Success")
except Exception as e:
    traceback.print_exc()

