from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_f
from CommandHandlers.transformation_handlers import handle_fold
from StorageManager import load_environment_state
import builtins

def get_clean_env():
    env = Environment()
    dummy = DummyVariable("x")
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

env = load_environment_state("games/basics of ITP/level19_env.md", get_clean_env)

handle_def_f(env, "1 add_2 x S S x")
env.local_formulae["f1"] = parse_fol_formula("add_2 x = S S x", env)
handle_fold(env, "add_2 f1 f2 goal")

goal_str = "add_2 x = S S x ⇔ S S x = S S x"
goal_node = parse_fol_formula(goal_str, env)
print(f"Matches? {goal_node.is_structurally_equal(env.formulae['goal'])}")
