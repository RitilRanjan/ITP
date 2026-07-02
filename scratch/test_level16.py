from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import axiom_Q1, axiom_Q2, rule_QR1, rule_QR2, rule_PC1

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# Premise from start_env
theorem_str = "∃y ∀x x∈y"
theorem = parse_fol_formula(theorem_str, env)

# 1. Q1: (∀x x∈y) ⇒ x∈y
q1_str = "(∀x x∈y) ⇒ x∈y"
q1_node = parse_fol_formula(q1_str, env)
print(f"Q1 holds? {axiom_Q1(q1_node)}")

# 2. Q2: x∈y ⇒ ∃y x∈y
q2_str = "x∈y ⇒ ∃y x∈y"
q2_node = parse_fol_formula(q2_str, env)
print(f"Q2 holds? {axiom_Q2(q2_node)}")

# 3. PC1: (∀x x∈y) ⇒ ∃y x∈y
pc1_str = "(∀x x∈y) ⇒ ∃y x∈y"
pc1_node = parse_fol_formula(pc1_str, env)
print(f"PC1 holds? {rule_PC1([q1_node, q2_node], pc1_node)}")

# 4. QR1: (∀x x∈y) ⇒ ∀x ∃y x∈y
qr1_str = "(∀x x∈y) ⇒ ∀x ∃y x∈y"
qr1_node = parse_fol_formula(qr1_str, env)
print(f"QR1 holds? {rule_QR1([pc1_node], qr1_node)}")

# 5. QR2: (∃y ∀x x∈y) ⇒ ∀x ∃y x∈y
qr2_str = "(∃y ∀x x∈y) ⇒ ∀x ∃y x∈y"
qr2_node = parse_fol_formula(qr2_str, env)
print(f"QR2 holds? {rule_QR2([qr1_node], qr2_node)}")

# 6. PC1 to prove goal
goal_str = "∀x ∃y x∈y"
goal_node = parse_fol_formula(goal_str, env)
print(f"PC1 (final) holds? {rule_PC1([theorem, qr2_node], goal_node)}")
