from typing import Set, List, Dict, Optional, Any
from AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, Function, FunctionType,
    PropositionalVariable, Relation, RelationType, Connective, Quantifier, MetaVariable,
    Bracket, Whitespace
)

def clone_ast(node: Node) -> Node:
    """Creates a deep copy of the AST node, preserving formatting fields."""
    if isinstance(node, Variable):
        c = Variable(name=node.name)
    elif isinstance(node, DummyVariable):
        c = DummyVariable(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    elif isinstance(node, MetaVariable):
        c = MetaVariable(name=node.name)
    elif isinstance(node, Bracket):
        c = Bracket(name=node.name)
    elif isinstance(node, Whitespace):
        c = Whitespace(name=node.name)
    elif isinstance(node, Function):
        c = Function(
            name=node.name,
            arity=node.arity,
            func_type=node.func_type,
            arguments=[clone_ast(arg) for arg in node.arguments]
        )
    elif isinstance(node, Relation):
        c = Relation(
            name=node.name,
            arity=node.arity,
            rel_type=node.rel_type,
            arguments=[clone_ast(arg) for arg in node.arguments]
        )
    elif isinstance(node, Connective):
        c = Connective(
            name=node.name,
            arity=node.arity,
            arguments=[clone_ast(arg) for arg in node.arguments]
        )
    elif isinstance(node, Quantifier):
        c = Quantifier(
            name=node.name,
            variable=clone_ast(node.variable),
            formula=clone_ast(node.formula)
        )
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
        
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c

def collect_all_occurrences(
    node: Node,
    bound_scopes: Optional[Dict[str, List[Quantifier]]] = None,
    enclosing_quantifiers: Optional[List[Quantifier]] = None,
    occurrences: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """Traverses the AST in-order to find all variable occurrences and classify them as free/bound."""
    if bound_scopes is None:
        bound_scopes = {}
    if enclosing_quantifiers is None:
        enclosing_quantifiers = []
    if occurrences is None:
        occurrences = []
        
    if isinstance(node, (Variable, DummyVariable)):
        is_free = True
        binding_q = None
        if node.name in bound_scopes and bound_scopes[node.name]:
            is_free = False
            binding_q = bound_scopes[node.name][-1]
        occurrences.append({
            "node": node,
            "is_free": is_free,
            "binding_quantifier": binding_q,
            "enclosing_quantifiers": list(enclosing_quantifiers)
        })
        
    elif isinstance(node, (Function, Relation, Connective)):
        for arg in node.arguments:
            collect_all_occurrences(arg, bound_scopes, enclosing_quantifiers, occurrences)
            
    elif isinstance(node, Quantifier):
        new_enclosing = enclosing_quantifiers + [node]
        q_var = node.variable
        occurrences.append({
            "node": q_var,
            "is_free": False,
            "binding_quantifier": node,
            "enclosing_quantifiers": list(enclosing_quantifiers)
        })
        
        v_name = q_var.name
        if v_name not in bound_scopes:
            bound_scopes[v_name] = []
        bound_scopes[v_name].append(node)
        
        collect_all_occurrences(node.formula, bound_scopes, new_enclosing, occurrences)
        
        bound_scopes[v_name].pop()
        
    return occurrences

def get_free(formula: FormulaNode) -> Set[str]:
    """Returns the set of names of all free standard variables in the formula."""
    occs = collect_all_occurrences(formula)
    return {o["node"].name for o in occs if o["is_free"] and isinstance(o["node"], Variable)}

def get_bound(formula: FormulaNode) -> Set[str]:
    """Returns the set of names of all bound standard variables in the formula."""
    occs = collect_all_occurrences(formula)
    return {o["node"].name for o in occs if not o["is_free"] and isinstance(o["node"], Variable)}

def check_free(formula: FormulaNode, variable: Any) -> bool:
    """Returns True if the variable is free in the formula."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    return var_name in get_free(formula)

def check_bound(formula: FormulaNode, variable: Any) -> bool:
    """Returns True if the variable is bound in the formula."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    return var_name in get_bound(formula)

def get_term_vars(node: Node) -> Set[str]:
    """Helper to collect all variable names in a term."""
    if isinstance(node, Variable):
        return {node.name}
    elif isinstance(node, Function):
        s = set()
        for arg in node.arguments:
            s.update(get_term_vars(arg))
        return s
    return set()

def is_substitutable_free(variable: Any, term: TermNode, formula: FormulaNode, occurrence_idx: Optional[int] = None) -> bool:
    """Checks if replacing free occurrences of a variable with a term causes variable capture."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    occs = collect_all_occurrences(formula)
    free_occs = [o for o in occs if o["node"].name == var_name and o["is_free"] and isinstance(o["node"], Variable)]
    
    term_vars = get_term_vars(term)
    
    if occurrence_idx is not None:
        if not (1 <= occurrence_idx <= len(free_occs)):
            return True
        occ = free_occs[occurrence_idx - 1]
        enclosing_bound = {q.variable.name for q in occ["enclosing_quantifiers"]}
        return len(term_vars.intersection(enclosing_bound)) == 0
    else:
        for occ in free_occs:
            enclosing_bound = {q.variable.name for q in occ["enclosing_quantifiers"]}
            if term_vars.intersection(enclosing_bound):
                return False
        return True

def is_valid_renaming(quantifier_node: Quantifier, target_name: str, formula: FormulaNode) -> bool:
    """Checks if renaming bound variable in quantifier_node scope to target_name changes meaning."""
    free_in_scope = get_free(quantifier_node.formula)
    if target_name in free_in_scope:
        return False
        
    occs_in_scope = collect_all_occurrences(quantifier_node.formula)
    for o in occs_in_scope:
        if o["node"].name == quantifier_node.variable.name and o["binding_quantifier"] is quantifier_node:
            for eq in o["enclosing_quantifiers"]:
                if eq.variable.name == target_name:
                    return False
    return True

def is_substitutable_bound(variable: Any, target_variable: Any, formula: FormulaNode, occurrence_idx: Optional[int] = None) -> bool:
    """Checks if renaming bound occurrences of a variable with another target variable preserves meaning."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    target_name = target_variable.name if hasattr(target_variable, 'name') else target_variable
    
    occs = collect_all_occurrences(formula)
    bound_occs = [o for o in occs if o["node"].name == var_name and not o["is_free"] and isinstance(o["node"], Variable)]
    
    if occurrence_idx is not None:
        if not (1 <= occurrence_idx <= len(bound_occs)):
            return True
        occ = bound_occs[occurrence_idx - 1]
        q_x = occ["binding_quantifier"]
        if q_x is None:
            return False
        return is_valid_renaming(q_x, target_name, formula)
    else:
        quantifiers_to_check = []
        for occ in bound_occs:
            q = occ["binding_quantifier"]
            if q and q not in quantifiers_to_check:
                quantifiers_to_check.append(q)
        for q in quantifiers_to_check:
            if not is_valid_renaming(q, target_name, formula):
                return False
        return True

def in_place_replace(node: Node, replacements_map: Dict[int, Node]):
    """Recursively replaces child nodes in-place using object identity comparison."""
    if hasattr(node, 'arguments'):
        for i, arg in enumerate(node.arguments):
            if id(arg) in replacements_map:
                node.arguments[i] = replacements_map[id(arg)]
            else:
                in_place_replace(arg, replacements_map)
                
    if isinstance(node, Quantifier):
        if id(node.variable) in replacements_map:
            node.variable = replacements_map[id(node.variable)]
        else:
            in_place_replace(node.variable, replacements_map)
            
        if id(node.formula) in replacements_map:
            node.formula = replacements_map[id(node.formula)]
        else:
            in_place_replace(node.formula, replacements_map)

def substitute_free(formula: FormulaNode, variable: Any, term: TermNode, occurrence_idx: Optional[int] = None) -> FormulaNode:
    """Substitutes free occurrences of variable with term in formula in-place."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    occs = collect_all_occurrences(formula)
    free_occs = [o for o in occs if o["node"].name == var_name and o["is_free"] and isinstance(o["node"], Variable)]
    
    if occurrence_idx is not None:
        if 1 <= occurrence_idx <= len(free_occs):
            target = free_occs[occurrence_idx - 1]["node"]
            replacements_map = {id(target): term}
        else:
            replacements_map = {}
    else:
        replacements_map = {id(o["node"]): term for o in free_occs}
        
    if id(formula) in replacements_map:
        return replacements_map[id(formula)]
        
    in_place_replace(formula, replacements_map)
    return formula

def substitute_bound(formula: FormulaNode, variable: Any, target_variable: Any, occurrence_idx: Optional[int] = None) -> FormulaNode:
    """Substitutes bound occurrences of variable with target_variable in-place."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    if isinstance(target_variable, str):
        target_node = Variable(target_variable)
    else:
        target_node = target_variable
        
    occs = collect_all_occurrences(formula)
    bound_occs = [o for o in occs if o["node"].name == var_name and not o["is_free"] and isinstance(o["node"], Variable)]
    
    if occurrence_idx is not None:
        if 1 <= occurrence_idx <= len(bound_occs):
            target = bound_occs[occurrence_idx - 1]["node"]
            replacements_map = {id(target): target_node}
        else:
            replacements_map = {}
    else:
        replacements_map = {id(o["node"]): target_node for o in bound_occs}
        
    if id(formula) in replacements_map:
        return replacements_map[id(formula)]
        
    in_place_replace(formula, replacements_map)
    return formula

def substitute_all(formula: FormulaNode, variable: Any, term: TermNode, occurrence_idx: Optional[int] = None) -> FormulaNode:
    """Substitutes all (free and bound) occurrences of variable with term in-place."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    occs = collect_all_occurrences(formula)
    var_occs = [o for o in occs if o["node"].name == var_name and isinstance(o["node"], Variable)]
    
    if occurrence_idx is not None:
        if 1 <= occurrence_idx <= len(var_occs):
            target = var_occs[occurrence_idx - 1]["node"]
            replacements_map = {id(target): term}
        else:
            replacements_map = {}
    else:
        replacements_map = {id(o["node"]): term for o in var_occs}
        
    if id(formula) in replacements_map:
        return replacements_map[id(formula)]
        
    in_place_replace(formula, replacements_map)
    return formula

def collect_term_vars_list(node: Node, var_name: str, occurrences: Optional[List[Node]] = None) -> List[Node]:
    """Helper to collect all matching variable nodes inside a term."""
    if occurrences is None:
        occurrences = []
    if isinstance(node, (Variable, DummyVariable)):
        if node.name == var_name:
            occurrences.append(node)
    elif isinstance(node, Function):
        for arg in node.arguments:
            collect_term_vars_list(arg, var_name, occurrences)
    return occurrences

def substitute_term(term: TermNode, variable: Any, replacement_term: TermNode, occurrence_idx: Optional[int] = None) -> TermNode:
    """Substitutes occurrences of variable in term with replacement_term in-place."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    occurrences = collect_term_vars_list(term, var_name)
    
    if occurrence_idx is not None:
        if 1 <= occurrence_idx <= len(occurrences):
            target = occurrences[occurrence_idx - 1]
            replacements_map = {id(target): replacement_term}
        else:
            replacements_map = {}
    else:
        replacements_map = {id(o): replacement_term for o in occurrences}
        
    if id(term) in replacements_map:
        return replacements_map[id(term)]
        
    in_place_replace(term, replacements_map)
    return term

def collect_prop_vars_list(node: Node, var_name: str, occurrences: Optional[List[Node]] = None) -> List[Node]:
    """Helper to collect all matching propositional variables inside a propositional formula."""
    if occurrences is None:
        occurrences = []
    if isinstance(node, PropositionalVariable):
        if node.name == var_name:
            occurrences.append(node)
    elif isinstance(node, Connective):
        for arg in node.arguments:
            collect_prop_vars_list(arg, var_name, occurrences)
    return occurrences

def substitute_proposition(
    prop_formula: FormulaNode,
    prop_variable: Any,
    replacement_formula: FormulaNode,
    occurrence_idx: Optional[int] = None
) -> FormulaNode:
    """Substitutes occurrences of propositional variable with replacement_formula in-place."""
    var_name = prop_variable.name if hasattr(prop_variable, 'name') else prop_variable
    occurrences = collect_prop_vars_list(prop_formula, var_name)
    
    if occurrence_idx is not None:
        if 1 <= occurrence_idx <= len(occurrences):
            target = occurrences[occurrence_idx - 1]
            replacements_map = {id(target): replacement_formula}
        else:
            replacements_map = {}
    else:
        replacements_map = {id(o): replacement_formula for o in occurrences}
        
    if id(prop_formula) in replacements_map:
        return replacements_map[id(prop_formula)]
        
    in_place_replace(prop_formula, replacements_map)
    return prop_formula

def find_substituted(formula1: FormulaNode, formula2: FormulaNode, target_variable: Optional[str] = None) -> Optional[Any]:
    """
    Checks if formula2 can be obtained from formula1 by substituting all occurrences
    of a single variable (or target_variable if specified) with a term.
    Returns a new copy of that term, or True if identical, or None if not possible.
    """
    from AST import is_structurally_equal
    if is_structurally_equal(formula1, formula2):
        return True
        
    occs1 = collect_all_occurrences(formula1)
    vars1 = {o["node"].name for o in occs1 if isinstance(o["node"], Variable)}
    
    if target_variable is not None:
        if target_variable not in vars1:
            return None
        vars_to_check = [target_variable]
    else:
        vars_to_check = list(vars1)
        
    for v_name in vars_to_check:
        match_result = {"term": None, "valid": True}
        
        def match_nodes(n1, n2):
            if not match_result["valid"]:
                return
                
            if isinstance(n1, Variable) and n1.name == v_name:
                if not isinstance(n2, TermNode):
                    match_result["valid"] = False
                    return
                if match_result["term"] is None:
                    match_result["term"] = n2
                else:
                    if not is_structurally_equal(match_result["term"], n2):
                        match_result["valid"] = False
                return
                
            if type(n1) != type(n2) or n1.name != n2.name:
                match_result["valid"] = False
                return
                
            if isinstance(n1, (Function, Relation, Connective)):
                if len(n1.arguments) != len(n2.arguments):
                    match_result["valid"] = False
                    return
                for a1, a2 in zip(n1.arguments, n2.arguments):
                    match_nodes(a1, a2)
            elif isinstance(n1, Quantifier):
                if n1.variable.name == v_name:
                    if not is_structurally_equal(n1.formula, n2.formula):
                        match_result["valid"] = False
                else:
                    match_nodes(n1.variable, n2.variable)
                    match_nodes(n1.formula, n2.formula)
            elif isinstance(n1, (Variable, DummyVariable, PropositionalVariable, MetaVariable)):
                pass
                
        match_nodes(formula1, formula2)
        
        if match_result["valid"] and match_result["term"] is not None:
            return clone_ast(match_result["term"])
            
    return None

def replace_structurally(
    node: Node, 
    target: Node, 
    replacement: Node, 
    occurrence_idx: Optional[int] = None,
    current_count: Optional[List[int]] = None
) -> Node:
    """
    Replaces occurrences of 'target' with 'replacement' inside 'node'.
    If occurrence_idx is specified, only that specific (1-based) occurrence is replaced.
    Traversal is pre-order (left-to-right textually).
    """
    if current_count is None:
        current_count = [0]
        
    if node.is_structurally_equal(target):
        current_count[0] += 1
        if occurrence_idx is None or occurrence_idx == current_count[0]:
            cloned_repl = clone_ast(replacement)
            cloned_repl.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
            cloned_repl.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
            return cloned_repl
            
    if isinstance(node, Variable):
        c = Variable(name=node.name)
    elif isinstance(node, DummyVariable):
        c = DummyVariable(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    elif isinstance(node, MetaVariable):
        c = MetaVariable(name=node.name)
    elif isinstance(node, Bracket):
        c = Bracket(name=node.name)
    elif isinstance(node, Whitespace):
        c = Whitespace(name=node.name)
    elif isinstance(node, Function):
        c = Function(
            name=node.name,
            arity=node.arity,
            func_type=node.func_type,
            arguments=[replace_structurally(arg, target, replacement, occurrence_idx, current_count) for arg in node.arguments]
        )
    elif isinstance(node, Relation):
        c = Relation(
            name=node.name,
            arity=node.arity,
            rel_type=node.rel_type,
            arguments=[replace_structurally(arg, target, replacement, occurrence_idx, current_count) for arg in node.arguments]
        )
    elif isinstance(node, Connective):
        c = Connective(
            name=node.name,
            arity=node.arity,
            arguments=[replace_structurally(arg, target, replacement, occurrence_idx, current_count) for arg in node.arguments]
        )
    elif isinstance(node, Quantifier):
        c = Quantifier(
            name=node.name,
            variable=replace_structurally(node.variable, target, replacement, occurrence_idx, current_count), # type: ignore
            formula=replace_structurally(node.formula, target, replacement, occurrence_idx, current_count) # type: ignore
        )
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
        
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c


def _is_double_neg(node: Node) -> bool:
    """Return True iff node is ¬(¬Ψ) for some formula Ψ."""
    return (
        isinstance(node, Connective) and node.name == "¬" and len(node.arguments) == 1
        and isinstance(node.arguments[0], Connective) and node.arguments[0].name == "¬"
        and len(node.arguments[0].arguments) == 1
    )


def remove_double_neg(
    node: Node,
    occurrence_idx: Optional[int] = None,
    current_count: Optional[List[int]] = None
) -> Node:
    """
    Remove double negations (¬¬Ψ → Ψ) inside *node*.
    If occurrence_idx is given (1-based), only that occurrence is simplified.
    Traversal is pre-order (left-to-right).
    Returns a new node; the original is not mutated.
    """
    if current_count is None:
        current_count = [0]

    if _is_double_neg(node):
        current_count[0] += 1
        if occurrence_idx is None or occurrence_idx == current_count[0]:
            # Strip two layers of ¬ and keep inner formula's formatting
            inner = node.arguments[0].arguments[0]  # type: ignore
            cloned = clone_ast(inner)
            # Preserve outer bracket/whitespace context
            cloned.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
            cloned.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
            return cloned

    # Recurse structurally
    if isinstance(node, Variable):
        c: Node = Variable(name=node.name)
    elif isinstance(node, DummyVariable):
        c = DummyVariable(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    elif isinstance(node, MetaVariable):
        c = MetaVariable(name=node.name)
    elif isinstance(node, Bracket):
        c = Bracket(name=node.name)
    elif isinstance(node, Whitespace):
        c = Whitespace(name=node.name)
    elif isinstance(node, Function):
        c = Function(
            name=node.name,
            arity=node.arity,
            func_type=node.func_type,
            arguments=[remove_double_neg(arg, occurrence_idx, current_count) for arg in node.arguments]
        )
    elif isinstance(node, Relation):
        c = Relation(
            name=node.name,
            arity=node.arity,
            rel_type=node.rel_type,
            arguments=[remove_double_neg(arg, occurrence_idx, current_count) for arg in node.arguments]  # type: ignore
        )
    elif isinstance(node, Connective):
        c = Connective(
            name=node.name,
            arity=node.arity,
            arguments=[remove_double_neg(arg, occurrence_idx, current_count) for arg in node.arguments]  # type: ignore
        )
    elif isinstance(node, Quantifier):
        c = Quantifier(
            name=node.name,
            variable=clone_ast(node.variable),  # type: ignore
            formula=remove_double_neg(node.formula, occurrence_idx, current_count)  # type: ignore
        )
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")

    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c


def add_double_neg(
    node: Node,
    occurrence_idx: Optional[int] = None,
    current_count: Optional[List[int]] = None
) -> Node:
    """
    Wrap a formula subnode with ¬¬ at the given (1-based) occurrence.
    If occurrence_idx is None, wraps ALL formula subnodes.
    Non-formula nodes (Variable, Function, Bracket, Whitespace …) are
    cloned unchanged; only FormulaNode instances are counted as candidates.
    Traversal is pre-order (left-to-right).
    Returns a new node; the original is not mutated.
    """
    if current_count is None:
        current_count = [0]

    # Only formula nodes are candidates for wrapping
    if isinstance(node, FormulaNode):
        current_count[0] += 1
        if occurrence_idx is None or occurrence_idx == current_count[0]:
            inner = _rebuild_node(node, occurrence_idx, current_count, recurse_fn=add_double_neg)
            wrapped = Connective(name="¬", arity=1, arguments=[
                Connective(name="¬", arity=1, arguments=[inner])
            ])
            wrapped.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
            wrapped.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
            return wrapped
        # Didn't match this node – still recurse into children
        return _rebuild_node(node, occurrence_idx, current_count, recurse_fn=add_double_neg)

    # Non-formula: just clone
    return _rebuild_non_formula(node)


def _rebuild_non_formula(node: Node) -> Node:
    """Clone a non-formula node (Variable, Function, Bracket, Whitespace …)."""
    if isinstance(node, Variable):
        c: Node = Variable(name=node.name)
    elif isinstance(node, DummyVariable):
        c = DummyVariable(name=node.name)
    elif isinstance(node, Bracket):
        c = Bracket(name=node.name)
    elif isinstance(node, Whitespace):
        c = Whitespace(name=node.name)
    elif isinstance(node, Function):
        c = Function(
            name=node.name,
            arity=node.arity,
            func_type=node.func_type,
            arguments=[_rebuild_non_formula(a) for a in node.arguments]
        )
    else:
        c = clone_ast(node)
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c


def _rebuild_node(
    node: Node,
    occurrence_idx: Optional[int],
    current_count: List[int],
    recurse_fn
) -> Node:
    """Rebuild node by recursing into children with recurse_fn."""
    if isinstance(node, Variable):
        c: Node = Variable(name=node.name)
    elif isinstance(node, DummyVariable):
        c = DummyVariable(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    elif isinstance(node, MetaVariable):
        c = MetaVariable(name=node.name)
    elif isinstance(node, Bracket):
        c = Bracket(name=node.name)
    elif isinstance(node, Whitespace):
        c = Whitespace(name=node.name)
    elif isinstance(node, Function):
        c = Function(
            name=node.name,
            arity=node.arity,
            func_type=node.func_type,
            arguments=[recurse_fn(arg, occurrence_idx, current_count) for arg in node.arguments]
        )
    elif isinstance(node, Relation):
        c = Relation(
            name=node.name,
            arity=node.arity,
            rel_type=node.rel_type,
            arguments=[recurse_fn(arg, occurrence_idx, current_count) for arg in node.arguments]  # type: ignore
        )
    elif isinstance(node, Connective):
        c = Connective(
            name=node.name,
            arity=node.arity,
            arguments=[recurse_fn(arg, occurrence_idx, current_count) for arg in node.arguments]  # type: ignore
        )
    elif isinstance(node, Quantifier):
        c = Quantifier(
            name=node.name,
            variable=clone_ast(node.variable),  # type: ignore
            formula=recurse_fn(node.formula, occurrence_idx, current_count)  # type: ignore
        )
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c
