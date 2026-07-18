import sys
sys.path.append('.')
from backend.CommandHandlers.transformation_handlers import handle_rw
print("Args:", handle_rw.__code__.co_varnames)
