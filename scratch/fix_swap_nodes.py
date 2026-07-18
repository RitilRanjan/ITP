import sys
with open('backend/SubstitutionManager.py', 'r') as f:
    content = f.read()

import re

old_swap_nodes = re.search(r'def swap_ast_nodes\([\s\S]*?if isinstance\(node, Iota\):', content).group(0)

new_swap_nodes = """def swap_ast_nodes(
    node: Node, 
    target_symbol: str, 
    is_relation: bool, 
    occurrence_idx: Union[int, List[int], None] = None, 
    current_count: Optional[List[int]] = None
) -> Node:
    if current_count is None:
        current_count = [0]
        
    if (is_relation and isinstance(node, LongFormula) and node.definition_name == target_symbol) or \\
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
    elif isinstance(node, Iota):"""

content = content.replace(old_swap_nodes, new_swap_nodes)

with open('backend/SubstitutionManager.py', 'w') as f:
    f.write(content)
