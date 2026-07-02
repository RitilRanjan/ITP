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
import app

def test_cmd(cmd_str):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        registry.dispatch(cmd_str.split()[0], env, cmd_str.split(maxsplit=1)[1] if " " in cmd_str else "")
    return f.getvalue()

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.terms["S"] = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])
env.local_formulae["injection"] = parse_fol_formula("∀x ∀y (S x = S y ⇒ x = y)", env)
env.add_theorem("injection")

inputs = ["y", "z"]
def mock_input(prompt):
    return inputs.pop(0)
builtins.input = mock_input

print(test_cmd("def_f 1 P x ιy S y = x"))
print(test_cmd("cf p_def P S x = x"))
print(test_cmd("fold P p_def p_unfold goal2"))
print(test_cmd("fold ι p_unfold p_unfold2 goal3"))

# We want to prove p_unfold2: ∃y (∀z (S z = S x ⇔ y = z) ∧ y = x)
# We can prove S z = S x ⇒ z = x from injection
# We can prove z = x ⇒ x = z using E3? 
# (z=x ∧ z=z) ⇒ (z=z ⇒ x=z)
# (x=z ∧ z=z) ⇒ (S x = S z) from E2.
