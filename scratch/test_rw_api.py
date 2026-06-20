import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from AST import Variable
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.transformation_handlers import handle_rw

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))
env.add_variable(Variable("c"))

t1 = parse_term("x + y", env)
env.terms["my_term"] = t1

from AST import Relation, RelationType
env.formulae["P"] = Relation("P", 1, RelationType.PRE_DEFINED, [])

f1 = parse_fol_formula("∀x ∃y (P(c) ∧ x = y)", env)
env.formulae["f1"] = f1

print("Before rw:", reconstruct_string(f1))
handle_rw(env, "my_term f1 f2", "rw")
print("After rw:", reconstruct_string(env.formulae["f2"]))
