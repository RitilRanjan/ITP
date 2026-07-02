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
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# Tautology to prove
phi_str = "¬x∈x ∨ x∈x"

# 1. Prove y=y
f1_str = "y=y"
f1_node = parse_fol_formula(f1_str, env)
print(f"E1 holds for y=y? {axiom_E1(f1_node)}")

# 2. Prove y=y => (¬x∈x ∨ x∈x)
f2_str = "y=y ⇒ ¬x∈x ∨ x∈x"
f2_node = parse_fol_formula(f2_str, env)
print(f"PC1 holds for f2? {rule_PC1([], f2_node)}")

# 3. QR1 to get y=y => ∀x(¬x∈x ∨ x∈x)
# Wait! Does parse_fol_formula of "∀x ¬x∈x ∨ x∈x" mean "∀x (¬x∈x ∨ x∈x)" or "(∀x ¬x∈x) ∨ x∈x"?
f3_str = "y=y ⇒ (∀x ¬x∈x ∨ x∈x)"
try:
    f3_node = parse_fol_formula(f3_str, env)
    print(f"QR1 holds for f3? {rule_QR1([f2_node], f3_node)}")
except Exception as e:
    print(f"Error parsing f3: {e}")

# 4. PC1 to get ∀x (¬x∈x ∨ x∈x)
goal_str = "∀x ¬x∈x ∨ x∈x"
goal_node = parse_fol_formula(goal_str, env)
print(f"PC1 holds for goal? {rule_PC1([f1_node, f3_node], goal_node)}")
