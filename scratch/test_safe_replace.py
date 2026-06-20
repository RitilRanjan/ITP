import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from AST import Variable, Quantifier, Relation, RelationType, TermNode, FormulaNode, PropositionalVariable
from SubstitutionManager import clone_ast, get_free, collect_all_occurrences
from Frontend import parse_fol_formula, reconstruct_string

class VariableCaptureError(Exception):
    def __init__(self, message, capturing_vars, expanded_ast):
        super().__init__(message)
        self.capturing_vars = capturing_vars
        self.expanded_ast = expanded_ast

def safe_replace(f_clone, is_prop, search_node, def_ast, occs):
    occs_list = collect_all_occurrences(f_clone)
    if is_prop:
        targets = [o for o in occs_list if o["node"].name == search_node.name and isinstance(o["node"], PropositionalVariable)]
    else:
        targets = [o for o in occs_list if o["node"].name == search_node.name and o["is_free"] and isinstance(o["node"], Variable)]
        
    if occs is not None:
        targets = [targets[i - 1] for i in occs if 1 <= i <= len(targets)]
        
    capturing_vars = set()
    free_in_def = get_free(def_ast)
    for o in targets:
        enclosing_vars = {q.variable.name for q in o["enclosing_quantifiers"]}
        capture = free_in_def.intersection(enclosing_vars)
        capturing_vars.update(capture)
        
    if capturing_vars:
        raise VariableCaptureError("Variable capture detected.", list(capturing_vars), def_ast)
        
    if is_prop:
        from SubstitutionManager import substitute_proposition
        substitute_proposition(f_clone, search_node, def_ast, occs)
    else:
        if isinstance(f_clone, FormulaNode):
            from SubstitutionManager import substitute_free
            substitute_free(f_clone, search_node, def_ast, occs)
        else:
            from SubstitutionManager import substitute_term
            substitute_term(f_clone, search_node, def_ast, occs)

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))
env.add_variable(Variable("c"))

# Let c be a term
from Frontend import parse_term
def_term = parse_term("x ∪ y", env)

# Target: ∀x ∀y P(c)
env.formulae["P"] = Relation("P", 1, RelationType.PRE_DEFINED, [])
formula = parse_fol_formula("∀x ∀y P(c)", env)

try:
    safe_replace(formula, False, Variable("c"), def_term, None)
except VariableCaptureError as e:
    print("Caught captures:", e.capturing_vars)
