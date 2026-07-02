from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.transformation_handlers import handle_fold
import builtins
import io
import contextlib
from CommandHandlers.CommandRegistry import registry

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.add_formula(Relation(name="P", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[dummy]))
env.add_formula(Relation(name="Q", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[dummy]))

inputs = ["y", "z"]
def mock_input(prompt):
    return inputs.pop(0)
builtins.input = mock_input

f = io.StringIO()
with contextlib.redirect_stdout(f):
    registry.dispatch("cf", env, "f1 Q(ιx P x)")
    registry.dispatch("fold", env, "ι f1 f2 goal")
print(f.getvalue())
if "goal" in env.local_formulae:
    print(env.local_formulae["goal"])

