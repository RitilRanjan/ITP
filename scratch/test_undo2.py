import os
import sys

from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_cf
from backend.RecycleBinManager import RecycleBinManager
from backend.Parser import show_environment

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
