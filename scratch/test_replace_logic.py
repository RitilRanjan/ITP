import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from AST import Relation, FormulaNode, TermNode, Quantifier, SetBuilder, Variable, Connective
from Frontend import parse_fol_formula, reconstruct_string
from DefinitionExpander import collect_occurrences, find_smallest_enclosing_formula, in_place_replace_node, clone_ast

env = Environment()
env.add_variable(Variable("C"))
env.add_variable(Variable("A"))
env.add_variable(Variable("x"))
f1 = parse_fol_formula("∀C (¬¬ {x∈C | ¬ x∈x} ∈ C)", env)

occurrences = []
collect_occurrences(f1, SetBuilder, "{", occurrences)
target = occurrences[0]

formula_clone = clone_ast(f1)
occurrences_clone = []
collect_occurrences(formula_clone, SetBuilder, "{", occurrences_clone)
target_node_clone = occurrences_clone[0]

enclosing = find_smallest_enclosing_formula(formula_clone, target_node_clone)

u = "y"
in_place_replace_node(formula_clone, target_node_clone, Variable(u))
Phi_u = clone_ast(enclosing)

expanded = Quantifier("∃", Variable(u), Connective("∧", 2, [Variable("Ψ(y)"), Phi_u]))

res = in_place_replace_node(formula_clone, enclosing, expanded)

print(reconstruct_string(res))
