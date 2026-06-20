import sys
import os

sys.path.append(os.path.abspath("/Users/ritilranjan/ITP"))

from Environment import Environment
from Frontend import Parser, lex
from AST import *
from DefinitionExpander import expand_user_defined_function_in_formula, VariableCaptureError

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))
env.add_variable(Variable("a"))

# Add + as a function symbol manually just so it parses, though its definition is x+y which is fine
env.terms["+"] = Function("+", 2, FunctionType.PRE_DEFINED, [Variable("x"), Variable("y")])

parser = Parser(env)
ast = parser.parse("+(x, y)", "term") # standard function application
env.add_user_function("f", 2, ast) # f is defined as f(_1, _2) = _1 + _2

parser2 = Parser(env)
# The formula is ∀y(f(y, z) = a)
formula = parser2.parse("∀y(=(f(y, z), a))", "formula")

print("Before unfolding:")
print(formula)

try:
    expanded = expand_user_defined_function_in_formula(env, formula, "f", 1)
    print("\nAfter unfolding:")
    print(expanded)
except VariableCaptureError as e:
    print(f"\nCaught VariableCaptureError!")
    print(f"Capturing variables: {e.capturing_vars}")
except Exception as e:
    print(f"\nError: {e}")
