from main import get_default_env
from Frontend import parse_prop_formula, reconstruct_string
from CommandHandlers.CommandRegistry import registry

env = get_default_env()
registry.dispatch("ct", env, "1 S 0")
formula = parse_prop_formula("1 = S 0", env)
print("Formula representation:", reconstruct_string(formula))
print("Formula AST:", formula)
