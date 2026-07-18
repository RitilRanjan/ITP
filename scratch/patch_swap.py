with open('scratch/clean_swap.py_out', 'r') as f:
    content = f.read()

import re

# In _handle_swap_base, `target_symbol` is `=` for eq and `⇔` for bi.
# `is_relation` should just be `is_formula` now maybe? Wait, target_symbol is passed.
# For `swap_bi`, it creates `Connective(name="⇔", arity=2, arguments=[...])`. This is fine.
# For `swap_eq`, it creates `Relation(name="=", ...)`. We need to change that.

content = re.sub(
    r'eq = Relation\(name="=", arity=2, rel_type=RelationType\.EQUALITY, arguments=\[clone_ast\(target_node\), clone_ast\(new_target\)\]\)',
    'eq = LongFormula(definition_name="=", term_placeholders={"t1": clone_ast(target_node), "t2": clone_ast(new_target)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})',
    content
)

with open('scratch/clean_swap.py_out', 'w') as f:
    f.write(content)
