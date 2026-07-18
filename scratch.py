from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct, handle_cf
from backend.CommandHandlers.terminal_handlers import handle_show
from backend.CommandHandlers.transformation_handlers import handle_rw

env = Environment(theory="ZFC")
env.variables = {"x", "y", "z", "w", "v", "a", "b", "c", "d", "e"}
from backend.AST import RelationType, FunctionType, DummyVariable, Relation, Function
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.add_formula(Relation(name="⇔", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
env.add_formula(Relation(name="∨", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

handle_ct(env, 'fin_set "{?t1 ?(, ?t2_)r2}" ε ?v1 ∀?v2 ?v2 ∈ ?v1 ⇔ (?v2 = ?t1 ?(∨ ?v2 = ?t2_)r2)')
handle_ct(env, 'ordered_pair "(?t1, ?t2)" {{?t1}, {?t1, ?t2}}')
handle_ct(env, 'n_tuple "(?(?t1_, )r1 ?t2, ?t3)" ((?(?t1_, )r1 ?t2), ?t3)')

handle_cf(env, 'test_form (a, b, c, d, e) = x')
env.target_goal = env.local_formulae["test_form"]
env.goal_formula_name = "test_form"

print("1. Original:")
handle_show(env, "")

handle_rw(env, "n_tuple test_form test_form")
print("2. After 1st n_tuple rw:")
handle_show(env, "")

handle_rw(env, "n_tuple test_form test_form")
print("3. After 2nd n_tuple rw:")
handle_show(env, "")

handle_rw(env, "n_tuple test_form test_form")
print("4. After 3rd n_tuple rw:")
handle_show(env, "")

# Now ALL n_tuples are reduced to size 2. We can now remove n_tuple from long_terms to allow ordered_pair to match!
del env.long_terms["n_tuple"]

handle_rw(env, "ordered_pair test_form test_form")
print("5. After ordered_pair rw:")
handle_show(env, "")

handle_rw(env, "ordered_pair test_form test_form")
print("6. After ordered_pair rw (x4):")
handle_rw(env, "ordered_pair test_form test_form")
handle_rw(env, "ordered_pair test_form test_form")
handle_rw(env, "ordered_pair test_form test_form")
handle_show(env, "")

handle_rw(env, "fin_set test_form test_form")
print("7. After fin_set rw:")
handle_show(env, "")

