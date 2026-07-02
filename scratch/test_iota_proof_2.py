from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_f
from CommandHandlers.transformation_handlers import handle_fold
from TruthEvaluator import check_implication
import builtins

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))

dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.terms["S"] = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])

env.local_formulae["injection"] = parse_fol_formula("∀x ∀y (S x = S y ⇒ x = y)", env)
env.add_theorem("injection")

# We provide lemma1 to make it possible
env.local_formulae["lemma1"] = parse_fol_formula("∀z (S z = S x ⇔ x = z) ∧ x = x", env)
env.add_theorem("lemma1")

inputs = ["y", "z"]
def mock_input(prompt):
    return inputs.pop(0)
builtins.input = mock_input

handle_def_f(env, "1 P x ιy S y = x")

env.local_formulae["f1"] = parse_fol_formula("P S x = x", env)
handle_fold(env, "P f1 f2 p_def")
handle_fold(env, "ι f2 f3 i_def")

# f3 is ∃y (∀z (S z = S x ⇔ y = z) ∧ y = x)
# Q2 provides: (∀z (S z = S x ⇔ x = z) ∧ x = x) ⇒ ∃y (∀z (S z = S x ⇔ y = z) ∧ y = x)
# So with PC1/PC2, we can derive f3 from lemma1 and Q2. Wait, the engine checks PC2.
# Can TruthEvaluator evaluate PC2 on Q2 instance?
