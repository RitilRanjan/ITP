from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_r
from CommandHandlers.transformation_handlers import handle_fold

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

handle_def_r(env, "1 is_zero x x=x")
env.local_formulae["f1"] = parse_fol_formula("is_zero x", env)
handle_fold(env, "is_zero f1 f2 goal")

goal_str = "is_zero x ⇔ x = x"
goal_node = parse_fol_formula(goal_str, env)
print(f"Matches? {goal_node.is_structurally_equal(env.formulae['goal'])}")
