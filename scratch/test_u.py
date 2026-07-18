from backend.Parser import parse_term
from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.AST import Variable

env = Environment()
env.local_variables["x"] = Variable("x")
handle_ct(env, 'g "g ?t1"')
handle_ct(env, 'f "f ?u1"')

try:
    ast1 = parse_term("f x", env)
    print("FAILED: f x was parsed successfully as", ast1)
except Exception as e:
    print("PASSED: f x rejected", str(e))

try:
    ast2 = parse_term("f g x", env)
    print("PASSED: f g x parsed successfully as", type(ast2))
except Exception as e:
    print("FAILED: f g x rejected", str(e))
