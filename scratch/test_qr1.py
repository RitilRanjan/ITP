from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import rule_QR1, rule_PC1, axiom_E1

env = Environment()
x = Variable("x")
y = Variable("y")
env.add_variable(x)
env.add_variable(y)
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

f1_str = "x=x ⇒ y=y"
f1_node = parse_fol_formula(f1_str, env)
e1_x = parse_fol_formula("x=x", env)
e1_y = parse_fol_formula("y=y", env)

print(f"PC1 holds? {rule_PC1([e1_x, e1_y], f1_node)}")

goal_str = "x=x ⇒ (∀y y=y)"
goal_node = parse_fol_formula(goal_str, env)
print(f"QR1 holds? {rule_QR1([f1_node], goal_node)}")
