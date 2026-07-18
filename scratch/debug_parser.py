from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Parser import parse_term, Parser

env = Environment()
handle_ct(env, 'S "S ?t1" S ?t1')
handle_ct(env, "1 add_2 S S ?t1")

print("terms:", env.terms.keys())

p = Parser(env)
print("prefix_patterns:", p.prefix_patterns)

try:
    parse_term("S add_2 ?t1", env)
except Exception as e:
    import traceback; traceback.print_exc()
