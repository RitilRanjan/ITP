from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Parser import Parser, lex

env = Environment()
handle_ct(env, 'S "S ?t1" S ?t1')
handle_ct(env, "1 add_2 S S ?t1")

tokens = lex("S add_2 ?t1")
parser = Parser(env)
parser.tokens = [t for t in tokens if not t.isspace()]
parser.pos = 0
try:
    print(parser.parse_expr(0, "term"))
    print("pos:", parser.pos, "len:", len(parser.tokens))
except Exception as e:
    import traceback; traceback.print_exc()
