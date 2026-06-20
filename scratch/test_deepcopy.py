import sys, os
sys.path.append(os.path.abspath("."))
import copy
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv
from Frontend import reconstruct_string

env = Environment()
handle_cv(env, "x y")

child = Environment(parent=env)
handle_cv(child, "z")

print("Deepcopying child...")
child_copy = copy.deepcopy(child)
print("Success!")

print("Original child parent vars:", list(child.parent.variables.keys()))
print("Copied child parent vars:", list(child_copy.parent.variables.keys()))

handle_cv(env, "w")
print("Original child parent vars after add w:", list(child.parent.variables.keys()))
print("Copied child parent vars after add w:", list(child_copy.parent.variables.keys()))
