from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import axiom_Q1, rule_PC1, rule_QR1

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("H"))
env.add_variable(Variable("A"))
env.add_variable(Variable("L"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# Premise: P = (∀x x∈H ⇒ x∈A) ∧ (∀x x∈A ⇒ x∈L)
# Conclusion: C = ∀x x∈H ⇒ x∈L

P_str = "(∀x x∈H ⇒ x∈A) ∧ (∀x x∈A ⇒ x∈L)"
P = parse_fol_formula(P_str, env)

# 1. Q1: (∀x x∈H ⇒ x∈A) ⇒ (x∈H ⇒ x∈A)
q1_1_str = "(∀x x∈H ⇒ x∈A) ⇒ (x∈H ⇒ x∈A)"
q1_1 = parse_fol_formula(q1_1_str, env)
print(f"Q1 1 holds? {axiom_Q1(q1_1)}")

# 2. Q1: (∀x x∈A ⇒ x∈L) ⇒ (x∈A ⇒ x∈L)
q1_2_str = "(∀x x∈A ⇒ x∈L) ⇒ (x∈A ⇒ x∈L)"
q1_2 = parse_fol_formula(q1_2_str, env)
print(f"Q1 2 holds? {axiom_Q1(q1_2)}")

# 3. PC1: P => (x∈H ⇒ x∈L)
# We can do this in one PC1 step since q1_1 and q1_2 implies this.
pc_str = "((∀x x∈H ⇒ x∈A) ∧ (∀x x∈A ⇒ x∈L)) ⇒ (x∈H ⇒ x∈L)"
pc_node = parse_fol_formula(pc_str, env)
print(f"PC1 holds? {rule_PC1([q1_1, q1_2], pc_node)}")

# 4. QR1: P => ∀x (x∈H ⇒ x∈L)
goal_str = "((∀x x∈H ⇒ x∈A) ∧ (∀x x∈A ⇒ x∈L)) ⇒ (∀x x∈H ⇒ x∈L)"
goal_node = parse_fol_formula(goal_str, env)
print(f"QR1 holds? {rule_QR1([pc_node], goal_node)}")
