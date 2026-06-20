import sys, os
sys.path.append(os.path.abspath("."))
import copy
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv
from CommandHandlers.mission_handlers import handle_mission
from Frontend import reconstruct_string

env = Environment()
undo_stack = []

def shallow_snapshot(e: Environment):
    chain = []
    curr = e
    while curr is not None:
        snap = {
            "env_id": id(curr),
            "goal": curr.goal_formula_name,
            "orig_goal": curr.original_goal_formula_name,
            "and_right": curr.and_right_formula_name,
            "target": curr.target_proven_formula_name,
            "vars": curr.local_variables.copy(),
            "dummies": curr.local_dummy_variables.copy(),
            "metas": curr.local_meta_variables.copy(),
            "props": curr.local_propositional_variables.copy(),
            "terms": curr.local_terms.copy(),
            "formulae": curr.local_formulae.copy(),
            "theorems": curr.local_theorems.copy(),
            "user_func": curr.local_user_functions.copy(),
            "user_rel": curr.local_user_relations.copy()
        }
        chain.append((curr, snap))
        curr = curr.parent
    return (e, chain)

def restore_snapshot(snapshot):
    active_env, chain = snapshot
    for curr, snap in chain:
        curr.goal_formula_name = snap["goal"]
        curr.original_goal_formula_name = snap["orig_goal"]
        curr.and_right_formula_name = snap["and_right"]
        curr.target_proven_formula_name = snap["target"]
        curr.local_variables.clear()
        curr.local_variables.update(snap["vars"])
        curr.local_dummy_variables.clear()
        curr.local_dummy_variables.update(snap["dummies"])
        curr.local_meta_variables.clear()
        curr.local_meta_variables.update(snap["metas"])
        curr.local_propositional_variables.clear()
        curr.local_propositional_variables.update(snap["props"])
        curr.local_terms.clear()
        curr.local_terms.update(snap["terms"])
        curr.local_formulae.clear()
        curr.local_formulae.update(snap["formulae"])
        curr.local_theorems.clear()
        curr.local_theorems.update(snap["theorems"])
        curr.local_user_functions.clear()
        curr.local_user_functions.update(snap["user_func"])
        curr.local_user_relations.clear()
        curr.local_user_relations.update(snap["user_rel"])
    return active_env

def exec_cmd(func, *args):
    global env
    undo_stack.append(shallow_snapshot(env))
    res = func(*args)
    if isinstance(res, Environment):
        env = res
        
handle_cv(env, "x y")
exec_cmd(handle_cv, env, "z w")
print("Vars:", list(env.variables.keys()))
env = restore_snapshot(undo_stack.pop())
print("Vars after undo:", list(env.variables.keys()))

# test mission
from CommandHandlers.env_handlers import handle_cf
handle_cf(env, "goal x ∈ y")
exec_cmd(handle_mission, env, "goal")
print("Goal in child:", env.goal_formula_name)
env = restore_snapshot(undo_stack.pop())
print("Goal after undo:", env.goal_formula_name)

