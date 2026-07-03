from Environment import Environment
from CommandHandlers.CommandRegistry import registry
import CommandHandlers.env_handlers
import CommandHandlers.logic_handlers
import CommandHandlers.mission_handlers

env = Environment(parent=None)
# inject S and 0
from AST import Constant, Function, FunctionType
env.local_terms["0"] = Constant("0")
env.local_functions["S"] = Function("S", arity=1, func_type=FunctionType.PREFIX, arguments=[])

registry.dispatch("ct", env, "1 S 0")
registry.dispatch("cf", env, "goal 1 = S 0")

from Frontend import reconstruct_string
if "goal" in env.formulae:
    print("Parsed goal:", reconstruct_string(env.formulae["goal"]))
else:
    print("Failed to parse goal")
