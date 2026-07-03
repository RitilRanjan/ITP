from main import get_default_env
from Frontend import Parser, reconstruct_string

env = get_default_env()
parser = Parser(env, "S 0")
term = parser.parse_term()
print("Term representation:", reconstruct_string(term))
print("Term AST:", term)
