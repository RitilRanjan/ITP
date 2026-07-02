from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from StorageManager import save_environment_state

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))

dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

env.local_formulae["is_zero"] = Relation(name="is_zero", arity=1, rel_type=RelationType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])

save_environment_state(env, "games/basics of ITP/level20_env.md")
