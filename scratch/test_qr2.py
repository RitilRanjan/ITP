from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import rule_QR2, rule_PC1, axiom_E1

env = Environment()
x = Variable("x")
y = Variable("y")
env.add_variable(x)
env.add_variable(y)
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

f1_str = "y=y ⇒ x=x"
f1_node = parse_fol_formula(f1_str, env)
e1_x = parse_fol_formula("x=x", env)
e1_y = parse_fol_formula("y=y", env)

print(f"PC1 holds? {rule_PC1([e1_y, e1_x], f1_node)}")

goal_str = "(∃y y=y) ⇒ x=x"
goal_node = parse_fol_formula(goal_str, env)
print(f"QR2 holds? {rule_QR2([f1_node], goal_node)}")
