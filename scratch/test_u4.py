from backend.Parser import Parser
from backend.Environment import Environment
from backend.AST import Variable

env = Environment()
env.local_variables["x"] = Variable("x")

p = Parser(env)
p.tokens = ["x"]
p.pos = 0

print("Trying to parse x:")
try:
    res = p.parse_expr(0, "term")
    print("res:", type(res), res)
except Exception as e:
    print("ERROR:", e)

