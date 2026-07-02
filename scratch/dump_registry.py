import sys
sys.path.append('.')
from CommandHandlers.registry import registry
from CommandHandlers import *

for cmd, info in registry.commands.items():
    print(f"Command: {cmd}")
    print(f"Category: {info.category}")
    print(f"Help: {info.help_text}")
    print("---")
