from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Parser import Parser, lex

env = Environment()
handle_ct(env, 'S "S ?t1" S ?t1')

tokens = lex("S add_2 ?t1")
parser = Parser(env)
parser.tokens = [t for t in tokens if not t.isspace()]
parser.pos = 0

old_try_match = parser.try_match_pattern
def wrapped_try_match(*args, **kwargs):
    print("try_match_pattern called with:", args, kwargs, "tokens:", parser.tokens[parser.pos:])
    res = old_try_match(*args, **kwargs)
    print("result:", res)
    return res

parser.try_match_pattern = wrapped_try_match
try:
    print(parser.parse_expr(0, "term"))
except Exception as e:
    import traceback; traceback.print_exc()
