import io
import contextlib
import sys
sys.path.append('.')
from CommandHandlers.CommandRegistry import registry
from Environment import Environment
from FirstOrderLogic import Variable, Function, Relation
from CommandHandlers.env_handlers import * # To load handlers

env = Environment()
env.add_local_term("x", Variable("x"))
env.add_local_formula("f1", Relation("P", Variable("x")))

args_str = "x t2 1 f1"
cmd = "st"
f = io.StringIO()
with contextlib.redirect_stdout(f):
    registry.dispatch(cmd, env, args_str)

output = f.getvalue()
print("OUTPUT FROM COMMAND:")
print(repr(output))
