import sys
sys.path.append('.')
from CommandHandlers.CommandRegistry import registry
import CommandHandlers.logic_handlers
import CommandHandlers.transformation_handlers
import CommandHandlers.definition_handlers
import CommandHandlers.env_handlers

for cmd, info in registry.metadata.items():
    print(f"Command: {cmd}")
    print(f"Category: {info['category']}")
    print(f"Help: {info['help']}")
    print("---")
