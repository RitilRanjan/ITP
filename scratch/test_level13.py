from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import axiom_Q1, axiom_Q2, rule_PC1

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("H"))
env.add_variable(Variable("L"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# A => B
f1_str = "(∀y y∈H ⇒ y∈L) ⇒ (x∈H ⇒ x∈L)"
f1_node = parse_fol_formula(f1_str, env)
print(f"Q1 holds? {axiom_Q1(f1_node)}")

# B => C
f2_str = "(x∈H ⇒ x∈L) ⇒ (∃x x∈H ⇒ x∈L)"
f2_node = parse_fol_formula(f2_str, env)
print(f"Q2 holds? {axiom_Q2(f2_node)}")

# A => C
goal_str = "(∀y y∈H ⇒ y∈L) ⇒ (∃x x∈H ⇒ x∈L)"
goal_node = parse_fol_formula(goal_str, env)
print(f"PC1 holds? {rule_PC1([f1_node, f2_node], goal_node)}")
