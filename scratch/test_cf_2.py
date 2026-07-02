from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_f
import builtins
from CommandHandlers.CommandRegistry import registry
import traceback

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.terms["S"] = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])

inputs = []
def mock_input(prompt):
    return inputs.pop(0)
builtins.input = mock_input

registry.dispatch("def_f", env, "1 P x εy S y = x")
try:
    f1 = parse_fol_formula("P S x = x", env)
    print("Parsed:", f1)
except Exception as e:
    traceback.print_exc()

