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

env.local_formulae["f1"] = parse_fol_formula("∃!x x=x", env)

# This mimics the UI behavior after our patch:
command = "fold ∃! f1 f2 f3\ny"
lines = command.strip().splitlines()
first_line = lines[0]
command_queue = lines[1:] if len(lines) > 1 else []
parts = first_line.strip().split(maxsplit=1)
cmd = parts[0]
args_str = parts[1] if len(parts) > 1 else ""

handle_fold(env, args_str, command_queue=command_queue)

if "f3" in env.local_formulae:
    print(f"Success! f3: {env.local_formulae['f3']}")
else:
    print("Failed!")

