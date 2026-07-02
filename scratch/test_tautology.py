from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import rule_PC1

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

goal_str = "(∀x x=x) ⇔ ¬∃x ¬(x=x)"
goal_node = parse_fol_formula(goal_str, env)
print(f"PC1 holds directly? {rule_PC1([], goal_node)}")

