from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from CommandHandlers.definition_handlers import handle_def_r
from CommandHandlers.transformation_handlers import handle_neg, handle_fold
from CommandHandlers.mission_handlers import handle_contra
from CommandHandlers.logic_handlers import handle_intro, handle_apply

env = Environment()
handle_cv(env, "A B x y")
handle_def_r(env, "2 x∉y ¬x∈y")
handle_cf(env, "russel ¬∃A ∀B (B∈A ⇔ B∉B)")
env2 = handle_contra(env, "russel f2 f3")
handle_neg(env2, "f2 f4", "neg-")
handle_intro(env2, "f4 A1 f5")
handle_intro(env2, "f5 A1 f6")
handle_fold(env2, "all f6 f7")
print("Before apply PC1, goal:", env2.goal_formula_name)
handle_apply(env2, "f3 PC1 f7")
print("After apply PC1, goal:", env2.goal_formula_name)
