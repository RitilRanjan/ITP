from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from CommandHandlers.transformation_handlers import handle_fold
import sys
import io

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# We need to simulate user input for get_fresh_variable_interactive
# In CommandHandlers/transformation_handlers.py:
# from CommandHandlers.utils import get_user_input
# get_user_input uses built-in input() if command_queue/inputs_collected are empty/None

import builtins
inputs = ["y"]
def mock_input(prompt):
    return inputs.pop(0)
builtins.input = mock_input

env.local_formulae["f1"] = parse_fol_formula("∃!x x=x", env)
handle_fold(env, "∃! f1 f2 f3")

if "f3" in env.local_formulae:
    print(f"f3: {env.local_formulae['f3']}")

