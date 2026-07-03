from main import get_default_env
from Frontend import parse_term, reconstruct_string

env = get_default_env()
term = parse_term("S 0", env)
print("Term representation:", reconstruct_string(term))
print("Term AST:", term)
