from main import get_default_env
from CommandHandlers.CommandRegistry import registry
env = get_default_env()
registry.dispatch("ct", env, "1 S 0")
print("keys in env.terms:", list(env.terms.keys()))
