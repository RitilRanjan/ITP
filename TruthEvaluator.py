from typing import Set, Dict
from itertools import product
from AST import FormulaNode, PropositionalVariable, Connective

def get_prop_variables(node: FormulaNode, vars_set: Set[str] = None) -> Set[str]:
    """Recursively collects all unique propositional variable names from the formula AST."""
    if vars_set is None:
        vars_set = set()
    if isinstance(node, PropositionalVariable):
        vars_set.add(node.name)
    elif isinstance(node, Connective):
        for arg in node.arguments:
            get_prop_variables(arg, vars_set)
    return vars_set

def evaluate_prop(node: FormulaNode, valuation: Dict[str, bool]) -> bool:
    """Evaluates a propositional formula AST node recursively under the given valuation mapping."""
    if isinstance(node, PropositionalVariable):
        if node.name not in valuation:
            raise ValueError(f"Propositional variable '{node.name}' not defined in valuation mapping.")
        return valuation[node.name]
    elif isinstance(node, Connective):
        if node.name == "¬":
            return not evaluate_prop(node.arguments[0], valuation)
        elif node.name == "∧":
            return evaluate_prop(node.arguments[0], valuation) and evaluate_prop(node.arguments[1], valuation)
        elif node.name == "∨":
            return evaluate_prop(node.arguments[0], valuation) or evaluate_prop(node.arguments[1], valuation)
        elif node.name == "⇒":
            return (not evaluate_prop(node.arguments[0], valuation)) or evaluate_prop(node.arguments[1], valuation)
        elif node.name == "⇔":
            return evaluate_prop(node.arguments[0], valuation) == evaluate_prop(node.arguments[1], valuation)
        else:
            raise ValueError(f"Unknown logical connective in propositional formula: '{node.name}'")
    else:
        raise ValueError(f"Invalid node type inside propositional formula evaluation: {type(node)}")

def is_tautology(formula: FormulaNode) -> bool:
    """
    Returns True iff the given propositional formula is a tautology.
    Raises ValueError if the number of unique propositional variables exceeds 16.
    """
    vars_list = sorted(list(get_prop_variables(formula)))
    if len(vars_list) > 16:
        raise ValueError(f"Too many propositional variables (found {len(vars_list)}, max allowed is 16).")
        
    if not vars_list:
        return evaluate_prop(formula, {})
        
    for values in product([True, False], repeat=len(vars_list)):
        valuation = dict(zip(vars_list, values))
        if not evaluate_prop(formula, valuation):
            return False
            
    return True
