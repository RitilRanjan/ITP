import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf, handle_crs, handle_ct
from CommandHandlers.mission_handlers import handle_mission
from CommandHandlers.logic_handlers import handle_intro, handle_imply, handle_apply
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "x y u v")
handle_crs(env, "Ψ 2")
handle_cf(env, "target (∃x ∀y (x Ψ y)) ⇒ (∀y ∃x (x Ψ y))")

# Start mission
env = handle_mission(env, "target")

# 1. imply p1
print("Target before imply:", reconstruct_string(env.formulae[env.goal_formula_name]))
handle_imply(env, "p1")
print("Target after imply:", reconstruct_string(env.formulae[env.goal_formula_name]))
print("Premise p1:", reconstruct_string(env.formulae["p1"]))

# 2. intro p1 (∃-elimination on premise: creates fresh variable u)
print("\nintro p1 u p2")
handle_intro(env, "p1 u p2")
print("Premise p2:", reconstruct_string(env.formulae["p2"]))

# 3. intro v (∀-introduction on goal: creates fresh variable v)
print("\nintro v")
handle_intro(env, "v")
print("Target after intro v:", reconstruct_string(env.formulae[env.goal_formula_name]))

# 4. We need to instantiate ∀y (u Ψ y) [which is p2] with term v.
# Wait, v is a variable, we need it as a term!
handle_ct(env, "v_term v")
print("\nintro p2 v_term p3")
handle_intro(env, "p2 v_term p3")
print("Premise p3:", reconstruct_string(env.formulae["p3"]))

# 5. Now goal is ∃x (x Ψ v)
# We want to instantiate ∃-introduction on goal with term u.
handle_ct(env, "u_term u")
print("\nintro u_term")
handle_intro(env, "u_term")
print("Target after intro u_term:", reconstruct_string(env.formulae[env.goal_formula_name]))

# 6. Now goal is (u Ψ v) and we have premise p3 (u Ψ v)
# apply p3
from CommandHandlers.state_handlers import handle_auto
print("\nauto target")
handle_auto(env, "target")
if "target" in env.theorems or env.goal_formula_name is None:
    print("\nProof complete!")
else:
    print("\nProof failed!")
    print("Goal:", reconstruct_string(env.formulae[env.goal_formula_name]))
