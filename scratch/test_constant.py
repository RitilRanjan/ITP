import sys
sys.path.append('.')
from backend.AST import Variable, Constant
print(issubclass(Constant, Variable))
