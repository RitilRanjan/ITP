from typing import List, Dict, Any, Union, Optional
from backend.AST import Node, TermNode, Variable, FormulaNode, TermPlaceholder, VariablePlaceholder, FormulaPlaceholder
from backend.Environment import Environment

def parse_pattern_structure(pattern: List[str]) -> List[Any]:
    import re
    res = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '?(':
            scope = []
            i += 1
            while i < len(pattern) and not re.match(r'^\)r\d+$', pattern[i]):
                scope.append(pattern[i])
                i += 1
            if i < len(pattern):
                index = int(pattern[i][2:])
                res.append(('rep', scope, index))
            i += 1
        else:
            res.append(pattern[i])
            i += 1
    return res

def expand_macro_tokens(
    def_tokens: List[str], 
    term_args: Dict[str, Union[TermNode, List[TermNode]]], 
    var_args: Dict[str, Union[Variable, List[Variable]]], 
    formula_args: Dict[str, Union[FormulaNode, List[FormulaNode]]], 
    rep_counts: Dict[int, int]
) -> List[Union[str, Node]]:
    
    res = []
    
    # We parse the def_tokens structure to find ?( ... )rN blocks
    struct = parse_pattern_structure(def_tokens)
    
    def process_struct(st, iteration_indices: Dict[str, int]):
        for el in st:
            if isinstance(el, tuple) and el[0] == 'rep':
                _, scope, rep_idx = el
                count = rep_counts.get(rep_idx, 0)
                for i in range(count):
                    new_indices = iteration_indices.copy()
                    # any variable like ?t3_ inside this scope will get index `i` (0-indexed)
                    # wait, how do we know which variables are iterated?
                    # Any placeholder ending with `_` gets the `i`th element.
                    # We can just store `rep_idx: i` in iteration_indices?
                    # No, a placeholder `?t3_` refers to `term_args['?t3_'][i]`.
                    # So we just pass `i` for this `rep_idx`.
                    new_indices[rep_idx] = i
                    process_struct(scope, new_indices)
            else:
                # it's a string token
                # Check if it's a placeholder
                if el.startswith('?'):
                    # is it an iterated placeholder?
                    if el.endswith('_'):
                        # e.g., ?t3_
                        # We need to find which rep_idx this belongs to.
                        # Wait, the user said the number corresponds to the repetition!
                        # `?t3_` has index 3. So it corresponds to rep_idx = 3.
                        # Wait, the user said `?t3_` means it's an iterated variable!
                        # But what if there is `?t3_` inside `r2`? The user example: `?(∨ ?v2 = ?t3_)r3`. Here the rep_idx is 3, and the variable is `t3_`.
                        # Let's extract the number from `el`: e.g., `?t3_` -> `3`.
                        import re
                        m = re.match(r'\?[tuvf]\(?([\w,]+)\)?(\d+)_', el) or re.match(r'\?[tuvf](\d+)_', el)
                        if m:
                            idx = int(m.group(1) if len(m.groups()) == 1 else m.group(2))
                            if idx in iteration_indices:
                                iter_i = iteration_indices[idx]
                                # get the item
                                if (el.startswith('?t') or el.startswith('?u')) and el in term_args:
                                    res.append(term_args[el][iter_i])
                                elif el.startswith('?v') and el in var_args:
                                    res.append(var_args[el][iter_i])
                                elif el.startswith('?f') and el in formula_args:
                                    res.append(formula_args[el][iter_i])
                                else:
                                    res.append(el)
                                continue
                    # normal placeholder or not iterated
                    if (el.startswith('?t') or el.startswith('?u')) and el in term_args:
                        val = term_args[el]
                        if isinstance(val, list): res.append(val[0] if val else el) # shouldn't happen for normal placeholders unless misused
                        else: res.append(val)
                    elif el.startswith('?v') and el in var_args:
                        val = var_args[el]
                        if isinstance(val, list): res.append(val[0] if val else el)
                        else: res.append(val)
                    elif el.startswith('?f') and el in formula_args:
                        val = formula_args[el]
                        if isinstance(val, list): res.append(val[0] if val else el)
                        else: res.append(val)
                    else:
                        res.append(el)
                else:
                    res.append(el)
                    
    process_struct(struct, {})
    return res


def compute_macro_free_variables(pattern: List[str], def_tokens: List[str], env: Environment, target: str) -> set:
    from backend.AST import DummyVariable
    from backend.Parser import Parser
    from backend.SubstitutionManager import compute_free_variables
    
    term_args = {}
    var_args = {}
    formula_args = {}
    rep_counts = {}
    
    struct = parse_pattern_structure(pattern)
    
    # We recursively find placeholders in struct
    def collect(st):
        for el in st:
            if isinstance(el, tuple) and el[0] == 'rep':
                rep_counts[el[2]] = 1
                collect(el[1])
            else:
                if el.startswith('?'):
                    import re
                    m = re.match(r'\?[tuvf]\(?([\w,]+)\)?(\d+)_', el) or re.match(r'\?[tuvf](\d+)_', el)
                    is_iter = m is not None
                    
                    if el.startswith('?t') or el.startswith('?u'):
                        if is_iter: term_args[el] = [DummyVariable(el)]
                        else: term_args[el] = DummyVariable(el)
                    elif el.startswith('?v'):
                        if is_iter: var_args[el] = [DummyVariable(el.replace('_', ''))]
                        else: var_args[el] = DummyVariable(el)
                    elif el.startswith('?f'):
                        from backend.AST import PropositionalVariable
                        if is_iter: formula_args[el] = [PropositionalVariable('p')] # dummy formula
                        else: formula_args[el] = PropositionalVariable('p')
                        
    collect(struct)
    
    expanded_tokens = expand_macro_tokens(def_tokens, term_args, var_args, formula_args, rep_counts)
    
    # parse the tokens!
    parser = Parser(env)
    parser.tokens = expanded_tokens
    parser.pos = 0
    ast = parser.parse_expr(0, target)
    if parser.pos < len(parser.tokens):
        raise Exception(f"Unexpected trailing tokens in macro definition: {parser.tokens[parser.pos]}")
    
    free_vars = compute_free_variables(ast, env)
    
    # remove any dummy variables
    dummy_names = set()
    for el in term_args.keys(): dummy_names.add(el)
    for el in var_args.keys(): dummy_names.add(el.replace('_', ''))
    
    return free_vars - dummy_names

