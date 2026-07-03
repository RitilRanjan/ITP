import os
import sys

from Environment import Environment
from CommandHandlers.env_handlers import handle_cf
from RecycleBinManager import RecycleBinManager
from Frontend import show_environment

env = Environment()
rb = RecycleBinManager()

rb.record_command("start", env, env, False, False)

old_env = env
handle_cf(env, "P ⊤")
rb.record_command("cf P ⊤", old_env, env, False, False)

print("History delta:", rb.history_commands[-1][1])

show_environment(env)
print("---")
print("Undo returned:", rb.undo(env))
show_environment(env)
