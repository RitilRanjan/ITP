from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

ast = parse_fol_formula("∀x ¬x∈x ∨ x∈x", env)
print(repr(ast))
