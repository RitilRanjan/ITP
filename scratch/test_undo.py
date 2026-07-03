import os
import sys

from Environment import Environment
from CommandHandlers.definition_handlers import handle_def_f
from CommandHandlers.env_handlers import handle_cv
from RecycleBinManager import RecycleBinManager, snapshot_env_keys
from Frontend import show_environment

env = Environment()
rb = RecycleBinManager()

# Mock what main.py does
rb.record_command("start", snapshot_env_keys(env), env, env, False, False)

old_env = env
before_snap = snapshot_env_keys(env)
handle_cv(env, "v1")
rb.record_command("cv v1", before_snap, old_env, env, False, False)

# def_f 1 F1 v1 S v1
old_env = env
before_snap = snapshot_env_keys(env)
handle_def_f(env, "1 F1 v1 S v1")
rb.record_command("def_f 1 F1 v1 S v1", before_snap, old_env, env, False, False)

print("History delta:", rb.history_commands[-1][1])
show_environment(env)
print("---")

print("Undo returned:", rb.undo(env))

show_environment(env)

print("---")
print("Trying def_f again...")
handle_def_f(env, "1 F1 v1 S v1")
print("Done.")
