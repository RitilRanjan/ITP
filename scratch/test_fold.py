from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from DeductiveSystem import rule_PC1
from CommandHandlers.transformation_handlers import handle_fold

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# Create target formula
f1_str = "∀x x=x"
env.local_formulae["f1"] = parse_fol_formula(f1_str, env)

# Apply fold
handle_fold(env, "∀ f1 f2 f3")

print(f"f2 generated? {'f2' in env.local_formulae}")
if 'f2' in env.local_formulae:
    print(f"f2: {env.local_formulae['f2']}")

print(f"f3 generated? {'f3' in env.local_formulae}")
if 'f3' in env.local_formulae:
    print(f"f3: {env.local_formulae['f3']}")

print(f"Is f3 a theorem? {'f3' in env.theorems}")

# PC1 on f3 to prove (∀x x=x) ⇒ ¬∃x ¬(x=x)
goal_str = "(∀x x=x) ⇒ ¬∃x ¬(x=x)"
goal_node = parse_fol_formula(goal_str, env)
print(f"PC1 holds? {rule_PC1([env.local_formulae['f3']], goal_node)}")

