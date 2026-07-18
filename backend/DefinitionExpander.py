from typing import List, Dict, Set, Optional, Type, Any, Union
from backend.AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, 
    Node, TermNode, FormulaNode, Variable, DummyVariable, 
     Connective, Quantifier, Bracket, Whitespace, Iota, Epsilon
)
from backend.SubstitutionManager import (
    clone_ast, substitute_term, substitute_free, collect_all_occurrences,
    is_substitutable_free, get_free, in_place_replace, get_term_vars
)
from backend.Environment import Environment

class VariableCaptureError(Exception):
    def __init__(self, message, capturing_vars, expanded_ast):
        super().__init__(message)
        self.capturing_vars = capturing_vars
        self.expanded_ast = expanded_ast

def find_smallest_enclosing_formula(root: Node, target: Node) -> Optional[FormulaNode]:
    def dfs(n):
        if n is target: return True
        
        if hasattr(n, "arguments"):
            for arg in n.arguments:
                res = dfs(arg)
                if res is True: return n if isinstance(n, FormulaNode) else True
                if isinstance(res, FormulaNode): return res
                
        if hasattr(n, "formula"):
            res = dfs(n.formula)
            if res is True: return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
            
        if hasattr(n, "base_set") and n.base_set is not None:
            res = dfs(n.base_set)
            if res is True: return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
            
        if hasattr(n, "children"):
            for c in n.children:
                res = dfs(c)
                if res is True: return n if isinstance(n, FormulaNode) else True
                if isinstance(res, FormulaNode): return res
                
        if hasattr(n, "left"):
            res = dfs(n.left)
            if res is True: return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
        if hasattr(n, "right"):
            res = dfs(n.right)
            if res is True: return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
            
        return False
        
    res = dfs(root)
    return res if isinstance(res, FormulaNode) else None

def collect_occurrences(node: Node, target_type: Type, name: str, occurrences: List[Node]):
    """Collects all occurrences of matching nodes in-order (left-to-right)."""
    if isinstance(node, target_type) and node.name == name:
        occurrences.append(node)
    
    if hasattr(node, 'arguments'):
        for arg in node.arguments:
            collect_occurrences(arg, target_type, name, occurrences)
    elif isinstance(node, Quantifier):
        collect_occurrences(node.variable, target_type, name, occurrences)
        collect_occurrences(node.formula, target_type, name, occurrences)

def in_place_replace_node(root: Node, target_node: Node, replacement_node: Node) -> Node:
    """
    Recursively replaces target_node with replacement_node in-place in root.
    Returns the root (which may be replacement_node if root is the target).
    """
    if id(root) == id(target_node):
        return replacement_node
    
    if hasattr(root, 'arguments'):
        for i, arg in enumerate(root.arguments):
            if id(arg) == id(target_node):
                root.arguments[i] = replacement_node
            else:
                in_place_replace_node(arg, target_node, replacement_node)
                
    if isinstance(root, Quantifier):
        if id(root.variable) == id(target_node):
            root.variable = replacement_node
        else:
            in_place_replace_node(root.variable, target_node, replacement_node)
            
        if id(root.formula) == id(target_node):
            root.formula = replacement_node
        else:
            in_place_replace_node(root.formula, target_node, replacement_node)
            
    return root

def substitute_dummy_in_formula(formula: FormulaNode, dummy_name: str, term: TermNode) -> FormulaNode:
    """Substitutes dummy_name with term in formula in-place."""
    replacements = {}
    
    def collect_and_map(node):
        if isinstance(node, DummyVariable) and node.name == dummy_name:
            replacements[id(node)] = clone_ast(term)
        
        if hasattr(node, 'arguments'):
            for arg in node.arguments:
                collect_and_map(arg)
        elif isinstance(node, Quantifier):
            collect_and_map(node.variable)
            collect_and_map(node.formula)
            
    collect_and_map(formula)
    if id(formula) in replacements:
        return replacements[id(formula)]
    in_place_replace(formula, replacements)
    return formula

def get_enclosing_bound_vars(root: Node, target_node: Node, current_bound: Optional[Set[str]] = None) -> Optional[Set[str]]:
    if current_bound is None:
        current_bound = set()
    if id(root) == id(target_node):
        return current_bound
    if hasattr(root, 'arguments'):
        for arg in root.arguments:
            res = get_enclosing_bound_vars(arg, target_node, current_bound)
            if res is not None:
                return res
    elif isinstance(root, Quantifier):
        new_bound = current_bound | {root.variable.name}
        res = get_enclosing_bound_vars(root.formula, target_node, new_bound)
        if res is not None:
            return res
    return None

def get_internal_captures(dummy_name: str, arg: Node, definition: Node) -> Set[str]:
    occs = collect_all_occurrences(definition)
    dummy_occs = [o for o in occs if isinstance(o["node"], DummyVariable) and o["node"].name == dummy_name]
    arg_vars = get_term_vars(arg)
    captures = set()
    for occ in dummy_occs:
        enclosing_bound = {q.variable.name for q in occ["enclosing_quantifiers"]}
        captures.update(arg_vars.intersection(enclosing_bound))
    return captures

def expand_user_defined_function_in_term(env: Environment, term: TermNode, func_name: str, occurrence_idx: Union[int, list, None] = None) -> TermNode:
    if occurrence_idx is None or isinstance(occurrence_idx, list):
        term_clone = clone_ast(term)
        occurrences = []
        collect_occurrences(term_clone, Function, func_name, occurrences)
        occs = list(range(1, len(occurrences) + 1)) if occurrence_idx is None else occurrence_idx
        res = term_clone
        for occ in sorted(occs, reverse=True):
            res = expand_user_defined_function_in_term(env, res, func_name, occ)
        return res

    if func_name not in env.user_functions:
        raise ValueError(f"Function '{func_name}' is not defined.")
    
    term_clone = clone_ast(term)
    occurrences = []
    collect_occurrences(term_clone, Function, func_name, occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of '{func_name}').")
        
    target_node = occurrences[occurrence_idx - 1]
    arity, definition = env.user_functions[func_name]
    
    expanded = clone_ast(definition)
    internal_captures = set()
    for i, arg in enumerate(target_node.arguments):
        dummy_name = f"_{i+1}"
        internal_captures.update(get_internal_captures(dummy_name, arg, definition))
        expanded = substitute_term(expanded, dummy_name, clone_ast(arg))
        
    # External captures check
    enclosing_bound = get_enclosing_bound_vars(term_clone, target_node)
    if enclosing_bound is None: enclosing_bound = set()
    
    definition_free = get_term_vars(definition)
    actual_free_in_def = {v for v in definition_free if not v.startswith("_")}
    external_captures = actual_free_in_def.intersection(enclosing_bound)
    
    all_captures = internal_captures | external_captures
    if all_captures:
        raise VariableCaptureError("Variable capture detected during unfolding", all_captures, expanded)
        
    res = in_place_replace_node(term_clone, target_node, expanded)
    return res

def expand_user_defined_function_in_formula(env: Environment, formula: FormulaNode, func_name: str, occurrence_idx: Union[int, list, None] = None) -> FormulaNode:
    if occurrence_idx is None or isinstance(occurrence_idx, list):
        formula_clone = clone_ast(formula)
        occurrences = []
        collect_occurrences(formula_clone, Function, func_name, occurrences)
        occs = list(range(1, len(occurrences) + 1)) if occurrence_idx is None else occurrence_idx
        res = formula_clone
        for occ in sorted(occs, reverse=True):
            res = expand_user_defined_function_in_formula(env, res, func_name, occ)
        return res

    if func_name not in env.user_functions:
        raise ValueError(f"Function '{func_name}' is not defined.")
        
    formula_clone = clone_ast(formula)
    occurrences = []
    collect_occurrences(formula_clone, Function, func_name, occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of '{func_name}').")
        
    target_node = occurrences[occurrence_idx - 1]
    arity, definition = env.user_functions[func_name]
    
    expanded = clone_ast(definition)
    internal_captures = set()
    for i, arg in enumerate(target_node.arguments):
        dummy_name = f"_{i+1}"
        internal_captures.update(get_internal_captures(dummy_name, arg, definition))
        expanded = substitute_term(expanded, dummy_name, clone_ast(arg))
        
    # External captures check
    enclosing_bound = get_enclosing_bound_vars(formula_clone, target_node)
    if enclosing_bound is None: enclosing_bound = set()
    
    from backend.SubstitutionManager import get_free
    definition_free = get_free(definition)
    actual_free_in_def = {v for v in definition_free if not v.startswith("_")}
    external_captures = actual_free_in_def.intersection(enclosing_bound)
    
    all_captures = internal_captures | external_captures
    if all_captures:
        raise VariableCaptureError("Variable capture detected during unfolding", all_captures, expanded)
        
    res = in_place_replace_node(formula_clone, target_node, expanded)
    return res

def expand_iota_in_formula(env: Environment, formula: FormulaNode, occurrence_idx: Union[int, list, None] = None, u: str = "", v: str = "") -> FormulaNode:
    if occurrence_idx is None or isinstance(occurrence_idx, list):
        formula_clone = clone_ast(formula)
        occurrences = []
        collect_occurrences(formula_clone, Iota, "ι", occurrences)
        occs = list(range(1, len(occurrences) + 1)) if occurrence_idx is None else occurrence_idx
        res = formula_clone
        for occ in sorted(occs, reverse=True):
            res = expand_iota_in_formula(env, res, occ, u, v)
        return res

    formula_clone = clone_ast(formula)
    occurrences = []
    collect_occurrences(formula_clone, Iota, "ι", occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of 'ι').")
        
    target_node = occurrences[occurrence_idx - 1]
    
    # Retrieve bound variable name x
    bound_var_name = target_node.variable.name
    
    # Semantic checks
    if u == v:
        raise ValueError(f"Introduced variables u and v must be distinct, got '{u}' and '{v}'.")
        
    # Free variables in Ψ (except the bound variable)
    free_in_Ψ = get_free(target_node.formula)
    if u in free_in_Ψ - {bound_var_name}:
        raise ValueError(f"Introduced variable '{u}' already occurs free in the body formula.")
    if v in free_in_Ψ - {bound_var_name}:
        raise ValueError(f"Introduced variable '{v}' already occurs free in the body formula.")
        
    # Free variables in parent formula Φ
    free_in_Φ = get_free(formula)
    if u in free_in_Φ:
        raise ValueError(f"Introduced variable '{u}' already occurs free in the parent formula.")
    if v in free_in_Φ:
        raise ValueError(f"Introduced variable '{v}' already occurs free in the parent formula.")
        
    # Bound quantifiers check (enclosing bound variables of target_node in formula)
    target_enclosing_bound = get_enclosing_bound_vars(formula_clone, target_node)
    if target_enclosing_bound is None:
        target_enclosing_bound = set()
    if u in target_enclosing_bound:
        raise ValueError(f"Introduced variable '{u}' is bound by an enclosing quantifier at the target position.")
    if v in target_enclosing_bound:
        raise ValueError(f"Introduced variable '{v}' is bound by an enclosing quantifier at the target position.")
        
    # Substitutability of v inside Ψ
    if not is_substitutable_free(bound_var_name, Variable(v), target_node.formula):
        raise ValueError(f"Variable '{v}' is not substitutable inside Ψ due to variable capture.")
        
    # Construct expanded parts
    # Ψ(v)
    Ψ_v = substitute_free(clone_ast(target_node.formula), bound_var_name, Variable(v))
    
    # u = v
    u_eq_v = LongFormula(definition_name="=", term_placeholders={"t1": Variable(u), "t2": Variable(v)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})
    
    # Ψ(v) ⇔ u = v
    inner_eq = Connective("⇔", 2, [Ψ_v, u_eq_v])
    inner_eq.prefix_formatting = [Bracket("("), Whitespace(" ")]
    inner_eq.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # ∀ v ( Ψ(v) ⇔ u = v )
    forall_v = Quantifier("∀", Variable(v), inner_eq)
    
    # Φ(u)
    occurrences_clone = []
    collect_occurrences(formula_clone, Iota, "ι", occurrences_clone)
    target_node_clone = occurrences_clone[occurrence_idx - 1]
    
    enclosing_formula = find_smallest_enclosing_formula(formula_clone, target_node_clone)
    if enclosing_formula is None:
        raise ValueError("Could not find an enclosing formula scope for the expansion.")
        
    in_place_replace_node(formula_clone, target_node_clone, Variable(u))
    Φ_u = clone_ast(enclosing_formula)
    
    # [ ∀ v ( Ψ(v) ⇔ u = v ) ] ∧ Φ(u)
    conj = Connective("∧", 2, [forall_v, Φ_u])
    conj.prefix_formatting = [Bracket("("), Whitespace(" ")]
    conj.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # ∃ u ( [ ∀ v ( Ψ(v) ⇔ u = v ) ] ∧ Φ(u) )
    expanded = Quantifier("∃", Variable(u), conj)
    
    res = in_place_replace_node(formula_clone, enclosing_formula, expanded)
    return res

def expand_set_builder_in_formula(env: Environment, formula: FormulaNode, occurrence_idx: Union[int, list, None] = None, u: str = "") -> FormulaNode:
    if occurrence_idx is None or isinstance(occurrence_idx, list):
        formula_clone = clone_ast(formula)
        occurrences = []

        occs = list(range(1, len(occurrences) + 1)) if occurrence_idx is None else occurrence_idx
        res = formula_clone
        for occ in sorted(occs, reverse=True):
            res = expand_set_builder_in_formula(env, res, occ, u)
        return res

    formula_clone = clone_ast(formula)
    occurrences = []

    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of set builder).")
        
    target_node = occurrences[occurrence_idx - 1]
    x = target_node.variable.name
    
    # Semantic checks
    from main import validate_new_name
    if not validate_new_name(env, u, "variable"):
        raise ValueError(f"Invalid standard variable name '{u}'.")
        
    free_in_target = get_free(target_node) # type: ignore
    if u in free_in_target:
        raise ValueError(f"Introduced variable '{u}' already occurs free in the set builder term.")
        
    free_in_Φ = get_free(formula)
    if u in free_in_Φ:
        raise ValueError(f"Introduced variable '{u}' already occurs free in the parent formula.")
        
    target_enclosing_bound = get_enclosing_bound_vars(formula_clone, target_node)
    if target_enclosing_bound is None:
        target_enclosing_bound = set()
    if u in target_enclosing_bound:
        raise ValueError(f"Introduced variable '{u}' is bound by an enclosing quantifier at the target position.")
        
    if not is_substitutable_free(x, Variable(u), target_node.formula):
        raise ValueError(f"Variable '{u}' is not substitutable inside the set builder formula due to variable capture.")
        
    # Construct expanded parts
    # x ∈ A
    x_in_A = LongFormula(definition_name="∈", term_placeholders={"t1": Variable(x), "t2": clone_ast(target_node.base_set)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})
    
    # x ∈ A ∧ Ψ(x)
    rhs = Connective("∧", 2, [x_in_A, clone_ast(target_node.formula)])
    rhs.prefix_formatting = [Bracket("("), Whitespace(" ")]
    rhs.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # x ∈ u
    x_in_u = LongFormula(definition_name="∈", term_placeholders={"t1": Variable(x), "t2": Variable(u)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})
    
    # x ∈ u ⇔ (x ∈ A ∧ Ψ(x))
    inner_eq = Connective("⇔", 2, [x_in_u, rhs])
    inner_eq.prefix_formatting = [Bracket("("), Whitespace(" ")]
    inner_eq.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # ∀ x ( x ∈ u ⇔ (x ∈ A ∧ Ψ(x)) )
    forall = Quantifier("∀", Variable(x), inner_eq)
    forall.prefix_formatting = [Bracket("("), Whitespace(" ")]
    forall.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    occurrences_clone = []

    target_node_clone = occurrences_clone[occurrence_idx - 1]
    
    enclosing_formula = find_smallest_enclosing_formula(formula_clone, target_node_clone)
    if enclosing_formula is None:
        raise ValueError("Could not find an enclosing formula scope for the expansion.")
        
    in_place_replace_node(formula_clone, target_node_clone, Variable(u))
    Φ_u = clone_ast(enclosing_formula)
    
    # ∀ x (...) ∧ Φ(u)
    conj = Connective("∧", 2, [forall, Φ_u])
    conj.prefix_formatting = [Bracket("("), Whitespace(" ")]
    conj.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # ∃ u ( ∀ x (...) ∧ Φ(u) )
    expanded = Quantifier("∃", Variable(u), conj)
    
    res = in_place_replace_node(formula_clone, enclosing_formula, expanded)
    return res

