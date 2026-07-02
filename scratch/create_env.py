from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from StorageManager import save_environment_state

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

theorem_str = "∃y ∀x x∈y"
theorem_node = parse_fol_formula(theorem_str, env)
env.local_formulae["theorem_1"] = theorem_node
env.add_theorem("theorem_1")

save_environment_state(env, "games/basics of ITP/level16_env.md")
