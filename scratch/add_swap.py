import os

with open("SubstitutionManager.py", "r") as f:
    content = f.read()

# Add swap_ast_nodes at the end of the file
swap_fn = """
def swap_ast_nodes(
    node: Node, 
    target_symbol: str, 
    is_relation: bool, 
    occurrence_idx: Union[int, List[int], None] = None, 
    current_count: Optional[List[int]] = None
) -> Node:
    if current_count is None:
        current_count = [0]
        
    if (is_relation and isinstance(node, Relation) and node.name == target_symbol) or \\
       (not is_relation and isinstance(node, Connective) and node.name == target_symbol):
        current_count[0] += 1
        if matches_occurrence(occurrence_idx, current_count[0]):
            c = clone_ast(node)
            # Swap left and right
            c.arguments[0], c.arguments[1] = c.arguments[1], c.arguments[0]
            # Recursively traverse inside
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
    elif isinstance(node, Function):
        c_args = [swap_ast_nodes(arg, target_symbol, is_relation, occurrence_idx, current_count) for arg in node.arguments]
        c = Function(name=node.name, arity=node.arity, func_type=node.func_type, arguments=c_args)
    elif isinstance(node, Relation):
        c_args = [swap_ast_nodes(arg, target_symbol, is_relation, occurrence_idx, current_count) for arg in node.arguments]
        c = Relation(name=node.name, arity=node.arity, rel_type=node.rel_type, arguments=c_args)
    elif isinstance(node, Connective):
        c_args = [swap_ast_nodes(arg, target_symbol, is_relation, occurrence_idx, current_count) for arg in node.arguments]
        c = Connective(name=node.name, arity=node.arity, arguments=c_args)
    elif isinstance(node, SetBuilder):
        c = SetBuilder(
            variable=clone_ast(node.variable),
            base_set=swap_ast_nodes(node.base_set, target_symbol, is_relation, occurrence_idx, current_count),
            formula=swap_ast_nodes(node.formula, target_symbol, is_relation, occurrence_idx, current_count)
        )
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
        
    c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
    c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
    return c
"""

with open("SubstitutionManager.py", "a") as f:
    f.write(swap_fn)

print("Added swap_ast_nodes to SubstitutionManager.py")
