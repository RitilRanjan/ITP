import os
import sys

from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from backend.Parser import show_environment
from main import get_default_env

env = get_default_env("NT")

registry.dispatch("cv", env, "x")
registry.dispatch("cv", env, "y")
registry.dispatch("cv", env, "z")
print("Defining P...")
registry.dispatch("def_f", env, "1 P y ι z S z = y")

print("Creating goal...")
registry.dispatch("cf", env, "goal ∀x P S x = x")

print("Starting mission...")
registry.dispatch("mission", env, "goal")

print("Applying intro2 to strip forall...")
registry.dispatch("intro2", env, "goal_sub1")
show_environment(env)

print("Rewriting P...")
registry.dispatch("rw", env, "P (1)")
show_environment(env)

# Now we need to fold iota!
# How does fold iota work inside an equality?
print("Folding iota...")
# fold iota in goal_sub2?
# The command asks for two fresh variables if interactive...
# Wait, let's see how fold iota behaves when run programmatically?
# We can't easily simulate user input for `fold ι`. We'll just define the formula and see what fold generates.

# actually fold ι will prompt! Let's mock input.
class MockInput:
    def __init__(self, inputs):
        self.inputs = inputs
    def __call__(self, prompt):
        return self.inputs.pop(0)

import backend.CommandHandlers.utils
CommandHandlers.utils.input = MockInput(["u", "v"])

registry.dispatch("fold", env, "ι (1)")
show_environment(env)
