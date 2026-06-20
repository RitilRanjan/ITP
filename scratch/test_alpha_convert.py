import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from AST import Variable, Quantifier, Relation, RelationType
from Frontend import parse_fol_formula, reconstruct_string
from SubstitutionManager import clone_ast, get_free, substitute_free, is_substitutable_free, collect_all_occurrences

def alpha_convert(q_node: Quantifier, new_name: str):
    old_name = q_node.variable.name
    if new_name in get_free(q_node.formula):
        raise ValueError(f"'{new_name}' is already free in the quantifier's scope.")
    if not is_substitutable_free(old_name, Variable(new_name), q_node.formula):
        raise ValueError(f"Renaming to '{new_name}' causes variable capture inside the quantifier's scope.")
        
    q_node.variable.name = new_name
    q_node.formula = substitute_free(q_node.formula, old_name, Variable(new_name))

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))
env.formulae["P"] = Relation("P", 2, RelationType.PRE_DEFINED, [])
env.formulae["Q"] = Relation("Q", 1, RelationType.PRE_DEFINED, [])

formula = parse_fol_formula("∀x ∃y (P(x, y) ∧ Q(z))", env)
print("Before:", reconstruct_string(formula))

# Find the ∃y quantifier
occs = []
collect_all_occurrences(formula, {}, [], occs)
q_y = None
for occ in occs:
    if isinstance(occ["node"], Quantifier) and occ["node"].variable.name == "y":
        q_y = occ["node"]
        break

try:
    alpha_convert(q_y, "x")
except Exception as e:
    print("Expected error:", e)

alpha_convert(q_y, "w")
print("After alpha convert y -> w:", reconstruct_string(formula))

