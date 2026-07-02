from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import axiom_Q1

env = Environment()
x = Variable("x")
y = Variable("y")
env.add_variable(x)
env.add_variable(y)
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

f_str = "(∀ x x=x) ⇒ y=y"
f_node = parse_fol_formula(f_str, env)
print(f"Parsed: {f_node}")
print(f"Q1 holds? {axiom_Q1(f_node)}")
