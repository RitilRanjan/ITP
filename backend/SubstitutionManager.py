from typing import Set, List, Dict, Optional, Any, Union
from backend.AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, 
    PropositionalVariable,  Connective, Quantifier, MetaVariable,
    LongTerm, LongFormula, TermPlaceholder, VariablePlaceholder, FormulaPlaceholder, Constant, Bracket, Whitespace, Iota, Epsilon
)

def matches_occurrence(occurrence_idx: Union[int, List[int], None], current_count: int) -> bool:
    if occurrence_idx is None:
        return True
    if isinstance(occurrence_idx, int):
        return occurrence_idx == current_count
    return current_count in occurrence_idx

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
    elif isinstance(node, Iota):
        c = Iota(
            variable=clone_ast(node.variable), # type: ignore
            formula=clone_ast(node.formula) # type: ignore
        )
    elif isinstance(node, Epsilon):
        c = Epsilon(
            variable=clone_ast(node.variable), # type: ignore
            formula=clone_ast(node.formula) # type: ignore
        )
    elif isinstance(node, Constant):
        c = Constant(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    elif isinstance(node, TermPlaceholder):
        c = TermPlaceholder(index=node.index, allowed_capture=set(node.allowed_capture))
    elif isinstance(node, FormulaPlaceholder):
        c = FormulaPlaceholder(index=node.index, allowed_capture=set(node.allowed_capture))
    elif isinstance(node, VariablePlaceholder):
        c = VariablePlaceholder(index=node.index)
    elif isinstance(node, LongTerm):
        c = LongTerm(
            definition_name=node.definition_name,
            term_placeholders={k: [clone_ast(i) for i in v] if isinstance(v, list) else clone_ast(v) for k, v in node.term_placeholders.items()},
            var_placeholders={k: [clone_ast(i) for i in v] if isinstance(v, list) else clone_ast(v) for k, v in node.var_placeholders.items()},
            formula_placeholders={k: [clone_ast(i) for i in v] if isinstance(v, list) else clone_ast(v) for k, v in getattr(node, 'formula_placeholders', {}).items()},
            repetition_counts=dict(node.repetition_counts)
        )
        c.pattern = list(node.pattern) if hasattr(node, 'pattern') else []
    elif isinstance(node, LongFormula):
        c = LongFormula(
            definition_name=node.definition_name,
            term_placeholders={k: [clone_ast(i) for i in v] if isinstance(v, list) else clone_ast(v) for k, v in node.term_placeholders.items()},
            var_placeholders={k: [clone_ast(i) for i in v] if isinstance(v, list) else clone_ast(v) for k, v in node.var_placeholders.items()},
            formula_placeholders={k: [clone_ast(i) for i in v] if isinstance(v, list) else clone_ast(v) for k, v in node.formula_placeholders.items()},
            repetition_counts=dict(node.repetition_counts)
        )
        c.pattern = list(node.pattern) if hasattr(node, 'pattern') else []
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
        
    if isinstance(node, (Variable, DummyVariable, Constant, PropositionalVariable, MetaVariable)):
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
        
    elif hasattr(node, 'arguments'):
        for arg in node.arguments:
            collect_all_occurrences(arg, bound_scopes, enclosing_quantifiers, occurrences)
            
    elif isinstance(node, (Quantifier, Iota, Epsilon)):
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
        
    elif isinstance(node, (LongTerm, LongFormula)):
        for p_val in node.term_placeholders.values():
            collect_all_occurrences(p_val, bound_scopes, enclosing_quantifiers, occurrences)
        for p_val in node.formula_placeholders.values():
            collect_all_occurrences(p_val, bound_scopes, enclosing_quantifiers, occurrences)
            
    return occurrences

def get_free(formula: FormulaNode) -> Set[str]:
    """Returns the set of names of all free standard variables in the formula."""
    occs = collect_all_occurrences(formula)
    return {o["node"].name for o in occs if o["is_free"] and isinstance(o["node"], Variable)}

def get_bound(formula: FormulaNode) -> Set[str]:
    """Returns the set of names of all bound standard variables in the formula."""
    occs = collect_all_occurrences(formula)
    return {o["node"].name for o in occs if not o["is_free"] and isinstance(o["node"], Variable)}

def check_free(formula: FormulaNode, variable: Any, env: 'Environment' = None) -> bool:
    """Returns True if the variable is free in the formula."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    if env is not None:
        return var_name in compute_free_variables(formula, env)
    return var_name in get_free(formula)

def check_bound(formula: FormulaNode, variable: Any) -> bool:
    """Returns True if the variable is bound in the formula."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    return var_name in get_bound(formula)

def get_term_vars(node: Node) -> Set[str]:
    """Helper to collect all variable names in a term."""
    if isinstance(node, Variable):
        return {node.name}
        return s
    return set()

def is_substitutable_free(variable: Any, term: TermNode, formula: FormulaNode, occurrence_idx: Optional[int] = None) -> bool:
    """Checks if replacing free occurrences of a variable with a term causes variable capture."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    occs = collect_all_occurrences(formula)
    from backend.AST import Constant
    free_occs = [o for o in occs if o["node"].name == var_name and o["is_free"] and isinstance(o["node"], (Variable, Constant))]
    
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

def is_valid_renaming(binder_node: Node, target_name: str, formula: FormulaNode) -> bool:
    """Checks if renaming bound variable in binder_node scope to target_name changes meaning."""
    free_in_scope = get_free(binder_node.formula)
    if target_name in free_in_scope:
        return False
        
    occs_in_scope = collect_all_occurrences(binder_node.formula)
    for o in occs_in_scope:
        if o["node"].name == binder_node.variable.name and o["binding_quantifier"] is binder_node:
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
                
    if isinstance(node, (Quantifier, Iota, Epsilon)):
        if id(node.variable) in replacements_map:
            node.variable = replacements_map[id(node.variable)]
        else:
            in_place_replace(node.variable, replacements_map)
            
        if id(node.formula) in replacements_map:
            node.formula = replacements_map[id(node.formula)]
        else:
            in_place_replace(node.formula, replacements_map)
            
    elif isinstance(node, (LongTerm, LongFormula)):
        for k, v in node.term_placeholders.items():
            if id(v) in replacements_map: node.term_placeholders[k] = replacements_map[id(v)]
            else: in_place_replace(v, replacements_map)
        for k, v in node.formula_placeholders.items():
            if id(v) in replacements_map: node.formula_placeholders[k] = replacements_map[id(v)]
            else: in_place_replace(v, replacements_map)

def substitute_free(formula: FormulaNode, variable: Any, term: TermNode, occurrence_idx: Optional[int] = None) -> FormulaNode:
    """Substitutes free occurrences of variable with term in formula in-place."""
    var_name = variable.name if hasattr(variable, 'name') else variable
    occs = collect_all_occurrences(formula)
    from backend.AST import Constant
    free_occs = [o for o in occs if o["node"].name == var_name and o["is_free"] and isinstance(o["node"], (Variable, Constant))]
    
    if occurrence_idx is not None:
        if isinstance(occurrence_idx, list):
            replacements_map = {id(free_occs[i-1]["node"]): term for i in occurrence_idx if 1 <= i <= len(free_occs)}
        elif 1 <= occurrence_idx <= len(free_occs):
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
    if isinstance(node, (Variable, DummyVariable, Constant)):
        if node.name == var_name:
            occurrences.append(node)
    elif type(node).__name__ in ("Iota", "Epsilon"):
        occs = collect_all_occurrences(node)
        for occ in occs:
            if occ["node"].name == var_name and occ["is_free"]:
                occurrences.append(occ["node"])
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
    occurrences: Optional[List[int]] = None
) -> FormulaNode:
    """Substitutes occurrences of propositional variable with replacement_formula in-place."""
    var_name = prop_variable.name if hasattr(prop_variable, 'name') else prop_variable
    all_occurrences = collect_prop_vars_list(prop_formula, var_name)
    
    if occurrences is not None:
        replacements_map = {}
        for idx in occurrences:
            if 1 <= idx <= len(all_occurrences):
                target = all_occurrences[idx - 1]
                replacements_map[id(target)] = replacement_formula
    else:
        replacements_map = {id(o): replacement_formula for o in all_occurrences}
        
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
    from backend.AST import is_structurally_equal
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
                
            if isinstance(n1, (Connective)):
                if len(n1.arguments) != len(n2.arguments):
                    match_result["valid"] = False
                    return
                for a1, a2 in zip(n1.arguments, n2.arguments):
                    match_nodes(a1, a2)
            elif isinstance(n1, (Quantifier, Iota, Epsilon)):
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
    occurrence_idx: Union[int, List[int], None] = None,
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
        if matches_occurrence(occurrence_idx, current_count[0]):
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
    elif isinstance(node, Iota):
        c = Iota(
            variable=replace_structurally(node.variable, target, replacement, occurrence_idx, current_count), # type: ignore
            formula=replace_structurally(node.formula, target, replacement, occurrence_idx, current_count) # type: ignore
        )
    elif isinstance(node, Epsilon):
        c = Epsilon(
            variable=replace_structurally(node.variable, target, replacement, occurrence_idx, current_count), # type: ignore
            formula=replace_structurally(node.formula, target, replacement, occurrence_idx, current_count) # type: ignore
        )

    elif isinstance(node, Constant):
        c = Constant(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
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
    occurrence_idx: Union[int, List[int], None] = None,
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
        if matches_occurrence(occurrence_idx, current_count[0]):
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
    elif isinstance(node, Iota):
        c = Iota(
            variable=clone_ast(node.variable),  # type: ignore
            formula=remove_double_neg(node.formula, occurrence_idx, current_count)  # type: ignore
        )
    elif isinstance(node, Epsilon):
        c = Epsilon(
            variable=clone_ast(node.variable),  # type: ignore
            formula=remove_double_neg(node.formula, occurrence_idx, current_count)  # type: ignore
        )

    elif isinstance(node, Constant):
        c = Constant(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")

    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c


def add_double_neg(
    node: Node,
    occurrence_idx: Union[int, List[int], None] = None,
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
        if matches_occurrence(occurrence_idx, current_count[0]):
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
    elif isinstance(node, Iota):
        c = Iota(
            variable=clone_ast(node.variable),  # type: ignore
            formula=recurse_fn(node.formula, occurrence_idx, current_count)  # type: ignore
        )
    elif isinstance(node, Epsilon):
        c = Epsilon(
            variable=clone_ast(node.variable),  # type: ignore
            formula=recurse_fn(node.formula, occurrence_idx, current_count)  # type: ignore
        )

    elif isinstance(node, Constant):
        c = Constant(name=node.name)
    elif isinstance(node, PropositionalVariable):
        c = PropositionalVariable(name=node.name)
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c

def swap_ast_nodes(
    node: Node, 
    target_symbol: str, 
    is_relation: bool, 
    occurrence_idx: Union[int, List[int], None] = None, 
    current_count: Optional[List[int]] = None
) -> Node:
    if current_count is None:
        current_count = [0]
        
    if (is_relation and isinstance(node, LongFormula) and node.definition_name == target_symbol) or \
       (not is_relation and isinstance(node, Connective) and node.name == target_symbol):
        current_count[0] += 1
        if matches_occurrence(occurrence_idx, current_count[0]):
            c = clone_ast(node)
            if is_relation:
                c.term_placeholders["t1"], c.term_placeholders["t2"] = c.term_placeholders["t2"], c.term_placeholders["t1"]
                c.term_placeholders["t1"] = swap_ast_nodes(c.term_placeholders["t1"], target_symbol, is_relation, occurrence_idx, current_count)
                c.term_placeholders["t2"] = swap_ast_nodes(c.term_placeholders["t2"], target_symbol, is_relation, occurrence_idx, current_count)
            else:
                c.arguments[0], c.arguments[1] = c.arguments[1], c.arguments[0]
                c.arguments[0] = swap_ast_nodes(c.arguments[0], target_symbol, is_relation, occurrence_idx, current_count)
                c.arguments[1] = swap_ast_nodes(c.arguments[1], target_symbol, is_relation, occurrence_idx, current_count)
            return c

    if isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable, Constant)):
        c = clone_ast(node)
    elif isinstance(node, Quantifier):
        c = Quantifier(
            name=node.name,
            variable=clone_ast(node.variable),
            formula=swap_ast_nodes(node.formula, target_symbol, is_relation, occurrence_idx, current_count)
        )
    elif isinstance(node, Iota):
        c = Iota(
            variable=clone_ast(node.variable),
            formula=swap_ast_nodes(node.formula, target_symbol, is_relation, occurrence_idx, current_count)
        )
    elif isinstance(node, Epsilon):
        c = Epsilon(
            variable=clone_ast(node.variable),
            formula=swap_ast_nodes(node.formula, target_symbol, is_relation, occurrence_idx, current_count)
        )
    elif isinstance(node, Connective):
        c_args = [swap_ast_nodes(arg, target_symbol, is_relation, occurrence_idx, current_count) for arg in node.arguments]
        c = Connective(name=node.name, arity=node.arity, arguments=c_args)

    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
        
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c

def get_placeholders(node: Node) -> Set[str]:
    """Returns a set of placeholder names (e.g., '?t1', '?v1') used in the AST."""
    from backend.AST import TermPlaceholder, VariablePlaceholder, FormulaPlaceholder, Connective, Quantifier, Iota, Epsilon, LongTerm, LongFormula
    placeholders = set()
    if isinstance(node, (TermPlaceholder, VariablePlaceholder)):
        placeholders.add(node.name)
    elif isinstance(node, (Connective)):
        for arg in node.arguments:
            placeholders.update(get_placeholders(arg))
    elif isinstance(node, Quantifier):
        placeholders.update(get_placeholders(node.variable))
        placeholders.update(get_placeholders(node.formula))
    elif isinstance(node, (Iota, Epsilon)):
        placeholders.update(get_placeholders(node.variable))
        placeholders.update(get_placeholders(node.formula))
    elif isinstance(node, (LongTerm, LongFormula)):
        for v in node.term_placeholders.values(): placeholders.update(get_placeholders(v))
        for v in node.var_placeholders.values(): placeholders.update(get_placeholders(v))
    return placeholders

def instantiate_long_definition(node: Node, term_args: Dict[str, TermNode], var_args: Dict[str, Variable], formula_args: Dict[str, FormulaNode]) -> Node:
    """Recursively replaces TermPlaceholder, VariablePlaceholder, and FormulaPlaceholder with provided arguments."""
    from backend.AST import TermPlaceholder, VariablePlaceholder, FormulaPlaceholder, Connective, Quantifier, Iota, Epsilon, LongTerm, LongFormula, Bracket, Whitespace
    if isinstance(node, TermPlaceholder):
        if node.name in term_args:
            return clone_ast(term_args[node.name])
        raise ValueError(f"Missing term argument for placeholder '{node.name}'")
    elif isinstance(node, FormulaPlaceholder):
        if node.name in formula_args:
            return clone_ast(formula_args[node.name])
        raise ValueError(f"Missing formula argument for placeholder '{node.name}'")
    elif isinstance(node, VariablePlaceholder):
        if node.name in var_args:
            return clone_ast(var_args[node.name])
        raise ValueError(f"Missing variable argument for placeholder '{node.name}'")
        
    c = clone_ast(node)
    
    if isinstance(c, (Connective)):
        c.arguments = [instantiate_long_definition(arg, term_args, var_args, formula_args) for arg in c.arguments]
    elif isinstance(c, Quantifier):
        c.variable = instantiate_long_definition(c.variable, term_args, var_args, formula_args)
        c.formula = instantiate_long_definition(c.formula, term_args, var_args, formula_args)
    elif isinstance(c, (Iota, Epsilon)):
        c.variable = instantiate_long_definition(c.variable, term_args, var_args, formula_args)
        c.formula = instantiate_long_definition(c.formula, term_args, var_args, formula_args)
    elif isinstance(c, (LongTerm, LongFormula)):
        c.term_placeholders = {k: instantiate_long_definition(v, term_args, var_args, formula_args) for k, v in c.term_placeholders.items()}
        c.var_placeholders = {k: instantiate_long_definition(v, term_args, var_args, formula_args) for k, v in c.var_placeholders.items()}
        c.formula_placeholders = {k: instantiate_long_definition(v, term_args, var_args, formula_args) for k, v in c.formula_placeholders.items()}
        
    return c

def compute_free_variables(node: Node, env: 'Environment', bound_vars: Optional[Set[str]] = None) -> Set[str]:
    if bound_vars is None:
        bound_vars = set()
    free_vars = set()
    
    if isinstance(node, Variable):
        if node.name not in bound_vars:
            free_vars.add(node.name)
            
    elif isinstance(node, (Constant, )):
        if hasattr(node, 'arguments'):
            for arg in node.arguments:
                free_vars.update(compute_free_variables(arg, env, bound_vars))
                
    elif isinstance(node, Connective):
        for arg in node.arguments:
            free_vars.update(compute_free_variables(arg, env, bound_vars))
            
    elif isinstance(node, Quantifier):
        new_bound = bound_vars | {node.variable.name}
        free_vars.update(compute_free_variables(node.formula, env, new_bound))
        

    elif isinstance(node, (LongTerm, LongFormula)):
        if node.definition_name in env.free_vars_cache:
            free_vars.update(env.free_vars_cache[node.definition_name] - bound_vars)
        for ph_node in node.term_placeholders.values():
            free_vars.update(compute_free_variables(ph_node, env, bound_vars))
        for ph_var in node.var_placeholders.values():
            free_vars.update(compute_free_variables(ph_var, env, bound_vars))
            
    return free_vars

def find_hidden_variable(node: Node, env: 'Environment', target_var: str, bound_vars: Optional[Set[str]] = None) -> Optional[str]:
    """
    Searches for a hidden variable capture risk. Returns the name of the unexpanded term/formula 
    that hides the target_var, or None if it's safe.
    """
    if bound_vars is None:
        bound_vars = set()
        
    if isinstance(node, (Constant, )):
        if hasattr(node, 'arguments'):
            for arg in node.arguments:
                res = find_hidden_variable(arg, env, target_var, bound_vars)
                if res: return res
                
    elif isinstance(node, Connective):
        for arg in node.arguments:
            res = find_hidden_variable(arg, env, target_var, bound_vars)
            if res: return res
            
    elif isinstance(node, Quantifier):
        new_bound = bound_vars | {node.variable.name}
        return find_hidden_variable(node.formula, env, target_var, new_bound)
        

    elif isinstance(node, (LongTerm, LongFormula)):
        if node.definition_name in env.free_vars_cache and target_var in env.free_vars_cache[node.definition_name] and target_var not in bound_vars:
            return node.definition_name
        for ph_node in node.term_placeholders.values():
            res = find_hidden_variable(ph_node, env, target_var, bound_vars)
            if res: return res
        for ph_var in node.var_placeholders.values():
            res = find_hidden_variable(ph_var, env, target_var, bound_vars)
            if res: return res
            
    return None


def instantiate_macro_tokens(def_tokens: List[str], term_args, var_args, formula_args, rep_counts, env, target: str) -> Node:
    from backend.MacroExpander import expand_macro_tokens
    from backend.Parser import Parser
    expanded_tokens = expand_macro_tokens(def_tokens, term_args, var_args, formula_args, rep_counts)
    parser = Parser(env)
    parser.tokens = expanded_tokens
    parser.pos = 0
    ast = parser.parse_expr(0, target)
    if parser.pos < len(parser.tokens):
        raise Exception("Unexpected trailing tokens when instantiating macro.")
    return ast

def extract_flat_nodes(pattern: list, term_placeholders: dict, var_placeholders: dict, formula_placeholders: dict, repetition_counts: dict) -> list:
    from backend.MacroExpander import parse_pattern_structure
    struct = parse_pattern_structure(pattern)
    
    def get_placeholders_from_struct(st):
        ph = []
        for el in st:
            if isinstance(el, tuple) and el[0] == 'rep':
                ph.append(('rep', get_placeholders_from_struct(el[1]), el[2]))
            elif el.startswith('?'):
                ph.append(el)
        return ph
        
    ph_struct = get_placeholders_from_struct(struct)
    flat_nodes = []
    
    def process_ph_list(ph_list, is_rep=False, rep_count=1, rep_idx=None):
        for i in range(rep_count):
            for ph in ph_list:
                if isinstance(ph, tuple) and ph[0] == 'rep':
                    count = repetition_counts.get(ph[2], 0)
                    process_ph_list(ph[1], is_rep=True, rep_count=count, rep_idx=ph[2])
                else:
                    val = None
                    if ph.startswith('?t') or ph.startswith('?u'): val = term_placeholders.get(ph)
                    elif ph.startswith('?v'): val = var_placeholders.get(ph)
                    elif ph.startswith('?f'): val = formula_placeholders.get(ph)
                    
                    if is_rep: flat_nodes.append(val[i])
                    else: flat_nodes.append(val)
                        
    process_ph_list(ph_struct)
    return flat_nodes

def map_flat_nodes_to_pattern(flat_nodes: list, f1_pattern: list):
    from backend.MacroExpander import parse_pattern_structure
    struct = parse_pattern_structure(f1_pattern)
    
    def get_placeholders_from_struct(st):
        ph = []
        for el in st:
            if isinstance(el, tuple) and el[0] == 'rep':
                ph.append(('rep', get_placeholders_from_struct(el[1]), el[2]))
            elif el.startswith('?'):
                ph.append(el)
        return ph
        
    ph_struct = get_placeholders_from_struct(struct)
    reps = [p for p in ph_struct if isinstance(p, tuple) and p[0] == 'rep']
    if len(reps) > 1:
        raise ValueError("Cannot map to a replacement pattern with more than 1 repetition block.")
        
    term_placeholders = {}
    var_placeholders = {}
    formula_placeholders = {}
    repetition_counts = {}
    
    node_idx = 0
    
    def process_ph_list(ph_list, is_rep=False, rep_count=1, rep_idx=None):
        nonlocal node_idx
        for i in range(rep_count):
            for ph in ph_list:
                if isinstance(ph, tuple) and ph[0] == 'rep':
                    scope_size = len(ph[1])
                    if scope_size == 0: continue
                    nodes_left = len(flat_nodes) - node_idx
                    after_ph = get_placeholders_from_struct(ph_list[ph_list.index(ph)+1:])
                    after_size = len(after_ph)
                    if (nodes_left - after_size) % scope_size != 0:
                        raise ValueError("Placeholder count mismatch!")
                    count = (nodes_left - after_size) // scope_size
                    if count < 0: raise ValueError("Not enough nodes for replacement.")
                    repetition_counts[ph[2]] = count
                    process_ph_list(ph[1], is_rep=True, rep_count=count, rep_idx=ph[2])
                else:
                    node = flat_nodes[node_idx]
                    node_idx += 1
                    if ph.startswith('?t') or ph.startswith('?u'): d = term_placeholders
                    elif ph.startswith('?v'): d = var_placeholders
                    elif ph.startswith('?f'): d = formula_placeholders
                    else: raise ValueError(f"Unknown placeholder {ph}")
                        
                    if is_rep:
                        if ph not in d: d[ph] = []
                        d[ph].append(node)
                    else:
                        d[ph] = node
                        
    process_ph_list(ph_struct)
    if node_idx != len(flat_nodes):
        raise ValueError("Not all nodes were consumed.")
        
    return term_placeholders, var_placeholders, formula_placeholders, repetition_counts
