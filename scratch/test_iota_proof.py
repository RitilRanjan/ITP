from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_f
from CommandHandlers.transformation_handlers import handle_fold, handle_apply
from StorageManager import load_environment_state
import builtins

def get_clean_env():
    env = Environment()
    dummy = DummyVariable("x")
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

env = load_environment_state("games/basics of ITP/level22_env.md", get_clean_env)

# Simulate creating variables and S, injection lemma
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))
env.terms["S"] = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])
env.local_formulae["injection"] = parse_fol_formula("∀x ∀y (S x = S y ⇒ x = y)", env)
env.add_theorem("injection")

inputs = ["y", "z"]
def mock_input(prompt):
    return inputs.pop(0)
builtins.input = mock_input

# Step 1: def_f 1 P x ιy S y = x
handle_def_f(env, "1 P x ιy S y = x")

# Step 2: Goal is ∀x P S x = x. Let's try to prove P S x = x, then apply PC2.
# Wait, let's unfold P in P S x = x
env.local_formulae["f1"] = parse_fol_formula("P S x = x", env)
handle_fold(env, "P f1 f2 p_def")
print(f"p_def: {env.local_formulae['p_def']}")

# Now f2 is ιy S y = S x = x
print(f"f2: {env.local_formulae['f2']}")

# Wait! f2 is (ιy S y = S x) = x.
# We want to unfold ι in f2!
inputs = ["u", "v"]
handle_fold(env, "ι f2 f3 i_def")
print(f"i_def: {env.local_formulae['i_def']}")
print(f"f3: {env.local_formulae['f3']}")

# Now f3 is ∃u (∀v (S v = S x ⇔ u = v) ∧ u = x)
# Is this true?
# If we set u = x, we get ∀v (S v = S x ⇔ x = v) ∧ x = x.
# We know S v = S x ⇒ v = x (injection).
# We also know v = x ⇒ S v = S x (equality congruence).
# So S v = S x ⇔ v = x.
# Thus ∀v (S v = S x ⇔ x = v) is true.
# And x = x is true.
