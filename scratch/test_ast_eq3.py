from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from CommandHandlers.transformation_handlers import handle_fold

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

env.local_formulae["f1"] = parse_fol_formula("∀x x=x", env)
handle_fold(env, "∀ f1 f2 f3")
f3_node = env.formulae["f3"]

goal_str = "(∀x x=x) ⇔ ¬∃x ¬(x=x)"
goal_node = parse_fol_formula(goal_str, env)
print(f"Goal matches f3? {goal_node.is_structurally_equal(f3_node)}")

