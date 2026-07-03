import os
import sys

from Environment import Environment
from CommandHandlers.CommandRegistry import registry
from Frontend import show_environment
import CommandHandlers.transformation_handlers
import CommandHandlers.env_handlers

env = Environment()

# Setup test environment
registry.dispatch("def_f", env, "2 f v1 v2 *(v1, v2)")
registry.dispatch("def_f", env, "1 g v3 f(v3, v3)")
registry.dispatch("ct", env, "expr f(g(v1), g(v1))")

print("Before:")
show_environment(env)
print("---")

print("Testing unrolling g (1) ...")
registry.dispatch("fold", env, "g (1) expr expr_unrolled")
print("After fold g (1) ...")
show_environment(env)

print("---")
print("Testing rw (2)...")
registry.dispatch("rw", env, "f (2) expr_unrolled expr_rw")
print("After rw f (2) ...")
show_environment(env)

print("---")
print("Testing st with (1)...")
registry.dispatch("st", env, "v1 g(v1) (1) expr_rw expr_st")
print("After st ...")
show_environment(env)
