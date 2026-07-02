from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import axiom_Q2, rule_PC1, axiom_E1

env = Environment()
x = Variable("x")
y = Variable("y")
env.add_variable(x)
env.add_variable(y)
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

f_str = "y=y ⇒ ∃x x=x"
f_node = parse_fol_formula(f_str, env)
print(f"Q2 holds? {axiom_Q2(f_node)}")

e1_str = "y=y"
e1_node = parse_fol_formula(e1_str, env)
print(f"E1 holds? {axiom_E1(e1_node)}")

goal_str = "∃x x=x"
goal_node = parse_fol_formula(goal_str, env)
print(f"PC1 holds? {rule_PC1([f_node, e1_node], goal_node)}")
