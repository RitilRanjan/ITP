from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from TruthEvaluator import check_implication
import builtins

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("u"))
env.add_variable(Variable("v"))

dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.terms["S"] = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])

inj = parse_fol_formula("∀x ∀y (S x = S y ⇒ x = y)", env)
target = parse_fol_formula("∃u (∀v (S v = S x ⇔ u = v) ∧ u = x)", env)

print(f"Check implication: {check_implication([inj], target)}")
