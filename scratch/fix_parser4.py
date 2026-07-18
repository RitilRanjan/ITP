with open('backend/Parser.py', 'r') as f:
    c = f.read()

c = c.replace('if target == "term": raise ParserError(f"Relation \'{op}\' not allowed in terms.")', 'if target == "term": break')

with open('backend/Parser.py', 'w') as f:
    f.write(c)
