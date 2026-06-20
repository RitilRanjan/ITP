import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from CommandHandlers.env_handlers import handle_cv, handle_cf
from Frontend import reconstruct_string, parse_fol_formula

env = Environment()
handle_cv(env, "x y A B")
handle_cf(env, "test_parse ¬∀x (x ∈ A)")
print("Parsed correctly!")
handle_cf(env, "test_parse2 ¬∀x (x ∈ A) ⇒ (x ∈ B)")
print("Parsed test_parse2 correctly!")
ast2 = env.formulae["test_parse2"]
print("AST test_parse2:", ast2.name, ast2.arguments if hasattr(ast2, "arguments") else "")

