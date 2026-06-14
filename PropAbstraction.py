from typing import List, Tuple, Dict
from AST import (
    Node, FormulaNode, Connective, Quantifier, Relation, PropositionalVariable,
    Whitespace, Bracket, is_structurally_equal
)
from SubstitutionManager import clone_ast

def clone_ast_list(nodes: List[Node]) -> List[Node]:
    return [clone_ast(n) for n in nodes]

def collect_total_prefix(node: Node, is_root: bool = True) -> List[Node]:
    """Recursively collects all prefix formatting at the leftmost edge of the subtree, filtering out internal brackets."""
    raw_prefix = node.prefix_formatting
    if not is_root:
        prefix = [f for f in raw_prefix if not isinstance(f, Bracket)]
    else:
        prefix = list(raw_prefix)
        
    prefix = clone_ast_list(prefix)
    
    if isinstance(node, (Relation, Connective)) and node.arguments:
        prefix += collect_total_prefix(node.arguments[0], is_root=False)
    return prefix

def collect_total_postfix(node: Node, is_root: bool = True) -> List[Node]:
    """Recursively collects all postfix formatting at the rightmost edge of the subtree, filtering out internal brackets."""
    postfix = []
    if isinstance(node, (Relation, Connective)) and node.arguments:
        postfix += collect_total_postfix(node.arguments[-1], is_root=False)
        
    raw_postfix = node.postfix_formatting
    if not is_root:
        node_postfix = [f for f in raw_postfix if not isinstance(f, Bracket)]
    else:
        node_postfix = list(raw_postfix)
        
    postfix += clone_ast_list(node_postfix)
    return postfix

def clear_left_prefix_formatting(node: Node, is_root: bool = True):
    """Recursively clears only the leftmost prefix formatting of the subtree."""
    if is_root:
        node.prefix_formatting = []
    else:
        node.prefix_formatting = [f for f in node.prefix_formatting if not isinstance(f, Whitespace)]
        
    if isinstance(node, (Relation, Connective)) and node.arguments:
        clear_left_prefix_formatting(node.arguments[0], is_root=False)

def clear_right_postfix_formatting(node: Node, is_root: bool = True):
    """Recursively clears only the rightmost postfix formatting of the subtree."""
    if is_root:
        node.postfix_formatting = []
    else:
        node.postfix_formatting = [f for f in node.postfix_formatting if not isinstance(f, Whitespace)]
        
    if isinstance(node, (Relation, Connective)) and node.arguments:
        clear_right_postfix_formatting(node.arguments[-1], is_root=False)

def abstract_to_propositional_with_mapping(
    formula: FormulaNode
) -> Tuple[FormulaNode, List[Tuple[FormulaNode, PropositionalVariable]]]:
    """
    Abstracts a first-order logic formula into its corresponding propositional logic formula.
    Every atomic subformula (Relation) or quantifier subformula (Quantifier) is replaced by a
    PropositionalVariable in a way that matching subformulae (ignoring formatting/whitespace/brackets)
    get the same PropositionalVariable.
    
    Returns a tuple: (abstracted_formula, mappings_list)
    where mappings_list is a list of tuples (cleaned_first_order_subformula, propositional_variable).
    """
    mappings: List[Tuple[FormulaNode, PropositionalVariable]] = []

    def get_or_create_prop_var(sub_formula: FormulaNode) -> PropositionalVariable:
        # Collect the total prefix and postfix formatting of the entire sub_formula subtree
        total_prefix = collect_total_prefix(sub_formula)
        total_postfix = collect_total_postfix(sub_formula)

        # Search for a matching subformula in mappings (ignoring formatting)
        for stored_node, prop_var in mappings:
            if is_structurally_equal(sub_formula, stored_node):
                res = clone_ast(prop_var)
                res.prefix_formatting = total_prefix
                res.postfix_formatting = total_postfix
                return res

        # Generate a new propositional variable
        var_name = f"p{len(mappings)}"
        prop_var = PropositionalVariable(name=var_name)
        
        # Store a clone of the sub_formula with cleared boundary formatting to keep mapping clean
        sf_clean = clone_ast(sub_formula)
        clear_left_prefix_formatting(sf_clean, is_root=True)
        clear_right_postfix_formatting(sf_clean, is_root=True)
        mappings.append((sf_clean, prop_var))

        # Copy the collected total formatting to the returned variable node
        res = clone_ast(prop_var)
        res.prefix_formatting = total_prefix
        res.postfix_formatting = total_postfix
        return res

    def recurse(node: FormulaNode) -> FormulaNode:
        if isinstance(node, Connective):
            # Connective formula: recursively process the arguments
            abstracted_args = [recurse(arg) for arg in node.arguments]
            new_conn = Connective(name=node.name, arity=node.arity, arguments=abstracted_args)
            new_conn.prefix_formatting = clone_ast_list(node.prefix_formatting)
            new_conn.postfix_formatting = clone_ast_list(node.postfix_formatting)
            return new_conn
        elif isinstance(node, (Relation, Quantifier)):
            # Boundary: Atomic relations or Quantifiers are replaced by propositional variables
            return get_or_create_prop_var(node)
        elif isinstance(node, PropositionalVariable):
            # Already a propositional variable: keep it as-is
            res = clone_ast(node)
            return res
        else:
            # Treat any other node type at this level as atomic
            return get_or_create_prop_var(node)

    abstracted_formula = recurse(formula)
    return abstracted_formula, mappings


def abstract_to_propositional(formula: FormulaNode) -> FormulaNode:
    """
    Abstracts a first-order logic formula into its corresponding propositional logic formula.
    Every atomic subformula (Relation) or quantifier subformula (Quantifier) is replaced by a
    PropositionalVariable in a way that matching subformulae (ignoring formatting/whitespace/brackets)
    get the same PropositionalVariable.
    """
    abstracted_formula, _ = abstract_to_propositional_with_mapping(formula)
    return abstracted_formula
