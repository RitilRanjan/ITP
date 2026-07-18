import re

# Fix StorageManager.py
with open('backend/StorageManager.py', 'r') as f:
    c = f.read()
c = re.sub(r'Function, FunctionType, Relation, RelationType, ', '', c)
with open('backend/StorageManager.py', 'w') as f:
    f.write(c)

# Fix DefinitionExpander.py
with open('backend/DefinitionExpander.py', 'r') as f:
    c = f.read()

# Delete expand_user_defined_* functions entirely
c = re.sub(r'def expand_user_defined_function_in_term[\s\S]*?def expand_iota_in_term', 'def expand_iota_in_term', c)
c = re.sub(r'def expand_user_defined_relation_in_formula[\s\S]*?def expand_iota_in_formula', 'def expand_iota_in_formula', c)

# Fix Relation("=")
c = c.replace('Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable(y), x])', 'LongFormula(definition_name="=", term_placeholders={"t1": Variable(y), "t2": x}, var_placeholders={}, formula_placeholders={}, repetition_counts={})')
c = c.replace('Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable(u), Variable(v)])', 'LongFormula(definition_name="=", term_placeholders={"t1": Variable(u), "t2": Variable(v)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})')

# Fix Relation("∈")
c = c.replace('Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable(x), clone_ast(target_node.base_set)])', 'LongFormula(definition_name="in", term_placeholders={"t1": Variable(x), "t2": clone_ast(target_node.base_set)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})')
c = c.replace('Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable(x), Variable(u)])', 'LongFormula(definition_name="in", term_placeholders={"t1": Variable(x), "t2": Variable(u)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})')

# Remove imports
c = re.sub(r'Function, FunctionType,', '', c)
c = re.sub(r'Relation, RelationType,', '', c)
c = c.replace('from backend.AST import LongTerm, LongFormula\n', '')
c = c.replace('from backend.AST import Node', 'from backend.AST import Node, LongTerm, LongFormula')

with open('backend/DefinitionExpander.py', 'w') as f:
    f.write(c)

