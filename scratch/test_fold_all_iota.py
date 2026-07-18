import os
import sys

from backend.Environment import Environment
from backend.CommandHandlers.CommandRegistry import registry
from main import get_default_env

import backend.CommandHandlers.env_handlers
import backend.CommandHandlers.logic_handlers
import backend.CommandHandlers.mission_handlers
import backend.CommandHandlers.state_handlers
import backend.CommandHandlers.definition_handlers
import backend.CommandHandlers.transformation_handlers
import backend.CommandHandlers.terminal_handlers

env = Environment()

commands = [
    "cv x y z",
    "def_f 1 P x ι y S y = x",
    "cf goal ∀x P S x = x",
    "mission goal",
    "intro u",
    "fold all"
]

for cmd in commands:
    print(f"\n> {cmd}")
    parts = cmd.split(maxsplit=1)
    c = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    res = registry.dispatch(c, env, args, command_queue=[], inputs_collected=[])
    if res is not None:
        env = res

print("\nFinal goal:")
if getattr(env, "goal_formula_name", None):
    from backend.Parser import reconstruct_string
    print(reconstruct_string(env.formulae[env.goal_formula_name]))
