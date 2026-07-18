from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Parser import Parser

env = Environment()
handle_ct(env, 'S "S ?t1" S ?t1')
handle_ct(env, "1 add_2 S S ?t1")
print("add_2 in env.terms:", 'add_2' in env.terms)

from backend.MacroExpander import compute_macro_free_variables
try:
    compute_macro_free_variables(["add_3", "?t1"], ["S", "add_2", "?t1"], env, "term")
except Exception as e:
    import traceback; traceback.print_exc()
