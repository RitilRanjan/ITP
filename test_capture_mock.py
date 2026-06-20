import sys
import os
sys.path.append(os.path.abspath("/Users/ritilranjan/ITP"))

from Environment import Environment
from Frontend import Parser
from AST import Variable
from DefinitionExpander import VariableCaptureError
import main
from unittest.mock import patch
import io

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))

parser = Parser(env)

# We define f(x) = ∀y(x ∈ y)
# Wait, user_functions are for terms. A term cannot be ∀y(x ∈ y) because that's a formula.
# So we must define a user relation R(x) = ∀y(x ∈ y).
ast_def = parser.parse("∀y(x ∈ y)", "formula")
from SubstitutionManager import substitute_free, substitute_bound, clone_ast, get_free
from AST import DummyVariable
ast_def = substitute_free(ast_def, "x", DummyVariable("_1"))
env.user_relations["R"] = (1, ast_def)

# Parent formula: R(y)
formula = parser.parse("R(y)", "formula")
env.formulae["f_input"] = formula

from Frontend import reconstruct_string
print("Original formula:", reconstruct_string(formula))

f_clone = clone_ast(formula)
symbol = "R"
occurrence_idx = 1
output_name = "f_output"

def mock_input(prompt):
    print(prompt, end="")
    return "z"

main.input = mock_input

print("Running mock fold loop...")
from DefinitionExpander import expand_user_defined_relation_in_formula

while True:
    try:
        expanded = expand_user_defined_relation_in_formula(env, f_clone, symbol, occurrence_idx)
        env.formulae[output_name] = expanded
        print(f"Expanded relation '{symbol}' at occurrence {occurrence_idx} to '{reconstruct_string(expanded)}'")
        break
    except VariableCaptureError as e:
        f_clone = main.handle_variable_capture_interactive(env, e, f_clone, symbol)
    except Exception as e:
        print(f"Error: {e}")
        break

print("Testing complete. Output formula:", reconstruct_string(env.formulae["f_output"]))
