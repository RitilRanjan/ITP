import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cf, handle_cv
from DeductiveSystem import rule_PC3
from AST import Relation, RelationType

env = Environment()
handle_cv(env, "x")
handle_cv(env, "y")
from AST import Variable
env.add_formula(Relation(name="Ψ", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[Variable(name="x")]))
env.add_formula(Relation(name="Φ", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[Variable(name="x")]))
env.add_formula(Relation(name="A", arity=2, rel_type=RelationType.USER_DEFINED, arguments=[Variable(name="x"), Variable(name="y")]))
env.add_formula(Relation(name="B", arity=2, rel_type=RelationType.USER_DEFINED, arguments=[Variable(name="x"), Variable(name="y")]))

# Premise: ∀x (¬Ψ(x) ∨ Φ(x))
handle_cf(env, "p1 ∀x (¬Ψ(x) ∨ Φ(x))")
# Conclusion: ∀x (Ψ(x) ⇒ Φ(x))
handle_cf(env, "c1 ∀x (Ψ(x) ⇒ Φ(x))")

res = rule_PC3([env.formulae["p1"]], env.formulae["c1"])
print("Test 1 Result (expected True):", res)

# Premise: ∀x (Ψ(x) ∧ Φ(x))
handle_cf(env, "p2 ∀x (Ψ(x) ∧ Φ(x))")
# Conclusion: ∀x (Ψ(x))
handle_cf(env, "c2 ∀x Ψ(x)")
res2 = rule_PC3([env.formulae["p2"]], env.formulae["c2"])
print("Test 2 Result (expected False because inner bodies are not equivalent):", res2)

# Multiple quantifiers test
handle_cf(env, "p3 ∀x ∃y (x A y ⇔ x B y)")
handle_cf(env, "c3 ∀x ∃y ((x A y ⇒ x B y) ∧ (x B y ⇒ x A y))")
res3 = rule_PC3([env.formulae["p3"]], env.formulae["c3"])
print("Test 3 Result (expected True):", res3)
