from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_f
from CommandHandlers.transformation_handlers import handle_fold
import builtins
import sys
import contextlib
import io
from CommandHandlers.CommandRegistry import registry

def test_cmd(cmd_str, input_val=None):
    if input_val is not None:
        inputs.append(input_val)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        cmd, args = cmd_str.split(maxsplit=1) if " " in cmd_str else (cmd_str, "")
        registry.dispatch(cmd, env, args)
    return f.getvalue()

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

print("def_f P:")
print(test_cmd("def_f 1 P x εy S y = x"))

print("cf f1:")
print(test_cmd("cf f1 P S x = x"))

print("fold P:")
print(test_cmd("fold P f1 f2 p_def"))

print("fold epsilon:")
print(test_cmd("fold ε f2 f3 e_def", "y"))

print("f3:")
if "f3" in env.local_formulae:
    print(env.local_formulae["f3"])
else:
    print("f3 not found!")

# Now let's try Q2
# We need to apply Q2 to f3 (the right hand side)
# We want to prove ∃y (S y = S x ∧ y = x)
print("apply q2 Q2:")
# syntax: apply <out> <axiom> <formula> <var> <term>
print(test_cmd("apply q2 Q2 S y = S x ∧ y = x y x"))

print("q2:")
if "q2" in env.local_formulae:
    print(env.local_formulae["q2"])
    
print("apply e1 E1 x=x:")
print(test_cmd("apply e1 E1 x=x"))

print("apply e2 E1 S x = S x:")
print(test_cmd("apply e2 E1 S x = S x"))

# Use PC2 to prove f3 from q2, e1, e2
print("apply f3_proven PC2 q2 e1 e2:")
print(test_cmd("apply f3_proven PC2 q2 e1 e2"))

# Use PC2 to prove f1 from p_def, e_def, f3_proven
print("apply f1_proven PC2 p_def e_def f3_proven:")
print(test_cmd("apply f1_proven PC2 p_def e_def f3_proven"))

# Use QR1 to prove goal from f1_proven
print("apply goal QR1 f1_proven:")
print(test_cmd("apply goal QR1 f1_proven"))

print("goal:")
if "goal" in env.local_formulae:
    print(env.local_formulae["goal"])
