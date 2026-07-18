from backend.Parser import parse_term
from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct, handle_var

env = Environment()
handle_var(env, "x")
handle_ct(env, 'g "g ?t1"')
handle_ct(env, 'f "f ?u1"')

try:
    ast2 = parse_term("f g x", env)
    print("PASSED: f g x parsed successfully as", type(ast2))
except Exception as e:
    print("FAILED: f g x rejected", str(e))
