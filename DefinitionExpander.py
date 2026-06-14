from typing import List, Dict, Set, Optional, Type, Any
from AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, Function, FunctionType,
    Relation, RelationType, Connective, Quantifier, Bracket, Whitespace
)
from SubstitutionManager import (
    clone_ast, substitute_term, substitute_free, collect_all_occurrences,
    is_substitutable_free, get_free, in_place_replace
)
from Environment import Environment

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

def expand_user_defined_function_in_term(env: Environment, term: TermNode, func_name: str, occurrence_idx: int) -> TermNode:
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
    for i, arg in enumerate(target_node.arguments):
        dummy_name = f"_{i+1}"
        expanded = substitute_term(expanded, dummy_name, clone_ast(arg))
        
    res = in_place_replace_node(term_clone, target_node, expanded)
    return res

def expand_user_defined_function_in_formula(env: Environment, formula: FormulaNode, func_name: str, occurrence_idx: int) -> FormulaNode:
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
    for i, arg in enumerate(target_node.arguments):
        dummy_name = f"_{i+1}"
        expanded = substitute_term(expanded, dummy_name, clone_ast(arg))
        
    res = in_place_replace_node(formula_clone, target_node, expanded)
    return res

def expand_user_defined_relation_in_formula(env: Environment, formula: FormulaNode, rel_name: str, occurrence_idx: int) -> FormulaNode:
    if rel_name not in env.user_relations:
        raise ValueError(f"Relation '{rel_name}' is not defined.")
        
    formula_clone = clone_ast(formula)
    occurrences = []
    collect_occurrences(formula_clone, Relation, rel_name, occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of '{rel_name}').")
        
    target_node = occurrences[occurrence_idx - 1]
    arity, definition = env.user_relations[rel_name]
    
    expanded = clone_ast(definition)
    for i, arg in enumerate(target_node.arguments):
        dummy_name = f"_{i+1}"
        expanded = substitute_dummy_in_formula(expanded, dummy_name, clone_ast(arg))
        
    res = in_place_replace_node(formula_clone, target_node, expanded)
    return res

def expand_existential_in_formula(formula: FormulaNode, occurrence_idx: int) -> FormulaNode:
    formula_clone = clone_ast(formula)
    occurrences = []
    collect_occurrences(formula_clone, Quantifier, "∃", occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of '∃').")
        
    target_node = occurrences[occurrence_idx - 1]
    
    # ∃ x Ψ -> ¬ ∀ x ¬ Ψ
    inner_neg = Connective("¬", 1, [clone_ast(target_node.formula)])
    forall = Quantifier("∀", target_node.variable, inner_neg)
    outer_neg = Connective("¬", 1, [forall])
    
    res = in_place_replace_node(formula_clone, target_node, outer_neg)
    return res

def expand_unique_existential_in_formula(formula: FormulaNode, occurrence_idx: int, y: str) -> FormulaNode:
    formula_clone = clone_ast(formula)
    occurrences = []
    collect_occurrences(formula_clone, Quantifier, "∃!", occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of '∃!').")
        
    target_node = occurrences[occurrence_idx - 1]
    x = target_node.variable
    Ψ = target_node.formula
    
    if y == x.name:
        raise ValueError(f"Introduced variable '{y}' must be different from the bound variable '{x.name}'.")
    
    free_in_Ψ = get_free(Ψ)
    if y in free_in_Ψ:
        raise ValueError(f"Introduced variable '{y}' is already free in the body of the quantifier.")
        
    if not is_substitutable_free(x.name, Variable(y), Ψ):
        raise ValueError(f"Variable '{y}' is not substitutable for '{x.name}' due to variable capture.")
        
    # Replace x with y in Ψ to get Ψ(y)
    Ψ_y = substitute_free(clone_ast(Ψ), x.name, Variable(y))
    
    # Ψ(y) ⇔ y = x
    y_eq_x = Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable(y), x])
    inner_eq = Connective("⇔", 2, [Ψ_y, y_eq_x])
    inner_eq.prefix_formatting = [Bracket("("), Whitespace(" ")]
    inner_eq.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # ∀ y (Ψ(y) ⇔ y = x)
    forall = Quantifier("∀", Variable(y), inner_eq)
    
    # ∃ x ∀ y (Ψ(y) ⇔ y = x)
    exists = Quantifier("∃", x, forall)
    
    res = in_place_replace_node(formula_clone, target_node, exists)
    return res

def expand_iota_function_in_formula(env: Environment, formula: FormulaNode, func_name: str, occurrence_idx: int, u: str, v: str) -> FormulaNode:
    if func_name not in env.user_functions:
        raise ValueError(f"Function '{func_name}' is not defined.")
        
    arity, definition = env.user_functions[func_name]
    
    decl_node = env.terms[func_name]
    if not (isinstance(decl_node, Function) and decl_node.func_type == FunctionType.IOTA_DEFINED):
        raise ValueError(f"'{func_name}' is not an iota function.")
        
    formula_clone = clone_ast(formula)
    occurrences = []
    collect_occurrences(formula_clone, Function, func_name, occurrences)
    
    if not (1 <= occurrence_idx <= len(occurrences)):
        raise ValueError(f"Occurrence index {occurrence_idx} out of range (found {len(occurrences)} occurrences of '{func_name}').")
        
    target_node = occurrences[occurrence_idx - 1]
    
    # Retrieve bound variable name x
    free_vars = get_free(definition)
    if len(free_vars) != 1:
        raise ValueError("Could not uniquely determine the bound variable from the iota function definition.")
    bound_var_name = list(free_vars)[0]
    
    # Instantiate arguments in definition
    Ψ_instantiated = clone_ast(definition)
    for i, arg in enumerate(target_node.arguments):
        dummy_name = f"_{i+1}"
        Ψ_instantiated = substitute_dummy_in_formula(Ψ_instantiated, dummy_name, clone_ast(arg))
        
    # Semantic checks
    if u == v:
        raise ValueError(f"Introduced variables u and v must be distinct, got '{u}' and '{v}'.")
        
    from main import validate_new_name
    if not validate_new_name(env, u, "variable") or not validate_new_name(env, v, "variable"):
        raise ValueError(f"Invalid standard variable names '{u}' or '{v}'.")
        
    # Free variables in Ψ_instantiated (except the bound variable)
    free_in_Ψ = get_free(Ψ_instantiated)
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
        
    # Substitutability of v inside Ψ_instantiated
    if not is_substitutable_free(bound_var_name, Variable(v), Ψ_instantiated):
        raise ValueError(f"Variable '{v}' is not substitutable inside Ψ due to variable capture.")
        
    # Construct expanded parts
    # Ψ(v)
    Ψ_v = substitute_free(clone_ast(Ψ_instantiated), bound_var_name, Variable(v))
    
    # u = v
    u_eq_v = Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable(u), Variable(v)])
    
    # Ψ(v) ⇔ u = v
    inner_eq = Connective("⇔", 2, [Ψ_v, u_eq_v])
    inner_eq.prefix_formatting = [Bracket("("), Whitespace(" ")]
    inner_eq.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # ∀ v ( Ψ(v) ⇔ u = v )
    forall = Quantifier("∀", Variable(v), inner_eq)
    forall.prefix_formatting = [Bracket("("), Whitespace(" ")]
    forall.postfix_formatting = [Whitespace(" "), Bracket(")")]
    
    # Φ(u) (target occurrences in clone)
    occurrences_clone = []
    collect_occurrences(formula_clone, Function, func_name, occurrences_clone)
    target_node_clone = occurrences_clone[occurrence_idx - 1]
    Φ_u = in_place_replace_node(formula_clone, target_node_clone, Variable(u))
    
    # ( ∀ v ( Ψ(v) ⇔ u = v ) ) ∧ Φ(u)
    conj = Connective("∧", 2, [forall, Φ_u])
    
    # ∃ u ( ... )
    expanded = Quantifier("∃", Variable(u), conj)
    return expanded
