import os
import sys

from Environment import Environment
from CommandHandlers.env_handlers import handle_cv
from RecycleBinManager import RecycleBinManager, snapshot_env_keys

env = Environment()
rb = RecycleBinManager()

rb.record_command("start", snapshot_env_keys(env), env, env, False, False)

# cv v1
old_env = env
before_snap = snapshot_env_keys(env)
handle_cv(env, "v1")
rb.record_command("cv v1", before_snap, old_env, env, False, False)

print("Vars in env:", env.local_variables)

# mission P
old_env = env
before_snap = snapshot_env_keys(env)
new_env = Environment(parent=env)
new_env.goal_formula_name = "goal"
# just simulate mission dispatch
rb.record_command("mission P", before_snap, old_env, new_env, True, False)

print("History delta for mission:", rb.history_commands[-1][1])
