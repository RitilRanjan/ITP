import sys, os
sys.path.append(os.path.abspath("."))
import copy
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv
from CommandHandlers.mission_handlers import handle_mission
from Frontend import reconstruct_string

env = Environment()
undo_stack = []
redo_stack = []

def exec_cmd(func, *args):
    global env
    undo_stack.append(copy.deepcopy(env))
    redo_stack.clear()
    res = func(*args)
    if isinstance(res, Environment):
        env = res

def undo():
    global env
    if undo_stack:
        redo_stack.append(env)
        env = undo_stack.pop()
        print("Undid")
    else:
        print("Nothing to undo")

def redo():
    global env
    if redo_stack:
        undo_stack.append(env)
        env = redo_stack.pop()
        print("Redid")

exec_cmd(handle_cv, env, "x y")
print("Vars:", list(env.variables.keys()))
exec_cmd(handle_mission, env, "goal") # wait, handle_mission takes args_str
print("Parent vars:", list(env.parent.variables.keys()) if env.parent else None)
undo()
print("Vars after undo:", list(env.variables.keys()))
print("Parent vars after undo:", list(env.parent.variables.keys()) if getattr(env, "parent", None) else None)
redo()
print("Parent vars after redo:", list(env.parent.variables.keys()) if env.parent else None)
