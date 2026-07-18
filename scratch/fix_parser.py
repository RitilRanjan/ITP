import re

with open('backend/Parser.py', 'r') as f:
    c = f.read()

# Fix imports
c = re.sub(r'Function, FunctionType,', '', c)
c = re.sub(r'Relation, RelationType,', '', c)
c = re.sub(r'Function,', '', c)
c = re.sub(r'Relation,', '', c)

c = c.replace('if target == "term": raise ParserError(f"Relation \'{op}\' not allowed in terms.")', '')
c = c.replace('elif isinstance(node, (Function, Relation, Connective)):', 'elif isinstance(node, Connective):')
c = c.replace('if isinstance(node.arguments[0], Relation) and node.arguments[0].arity == 2:', 'if isinstance(node.arguments[0], Connective) and node.arguments[0].arity == 2:')

# Fix consolidate symbols comment
c = c.replace('2. Consolidated Symbols (Variables, Dummy, Prop, Functions, Relations)', '2. Consolidated Symbols (Variables, Dummy, Prop)')

with open('backend/Parser.py', 'w') as f:
    f.write(c)

