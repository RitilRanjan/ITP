from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Parser import parse_term
from backend.AST import Variable
env = Environment()
env.add_variable(Variable("x"))
handle_ct(env, '"add_2 ?t1" S(S(?t1))')
print("Long terms:", env.long_terms.keys())
try:
    node = parse_term('add_2 x', env)
    print("Parsed node:", node)
except Exception as e:
    print("Error:", e)
