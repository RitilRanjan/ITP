from main import get_default_env
from CommandHandlers.CommandRegistry import registry
from Frontend import reconstruct_string

env = get_default_env()
registry.dispatch("ct", env, "1 S 0")
registry.dispatch("cf", env, "goal 1 = S 0")

if "goal" in env.formulae:
    print("Parsed goal:", reconstruct_string(env.formulae["goal"]))
else:
    print("Failed to parse goal")
