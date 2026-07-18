from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_cv, handle_ct, handle_cf
from backend.Registry import AXIOMS
import traceback
import builtins

env = Environment()
env.theory = "ZFC"
env.theorems.update(AXIOMS)

handle_cv(env, "A B C")
handle_cf(env, 'subset "?t1 ⊆ ?t2" ∀?v3 (?v3 ∈ ?t1 ⇒ ?v3 ∈ ?t2)')

def patch_try_match_pattern():
    import backend.Parser
    orig = backend.Parser.Parser.try_match_pattern
    def new_match(self, pattern, expected_target, name, left_node=None):
        print(f"try_match_pattern({name}) pattern={pattern} left={left_node}")
        res = orig(self, pattern, expected_target, name, left_node)
        print(f"try_match_pattern({name}) returned {res}")
        return res
    backend.Parser.Parser.try_match_pattern = new_match

patch_try_match_pattern()
try:
    print("Testing (A ⊆ B ∧ B ⊆ C) ⇒ A ⊆ C")
    handle_cf(env, "goal (A ⊆ B ∧ B ⊆ C) ⇒ A ⊆ C")
except Exception as e:
    traceback.print_exc()
