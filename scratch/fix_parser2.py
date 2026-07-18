with open('backend/Parser.py', 'r') as f:
    c = f.read()

c = c.replace('elif op in ("=", "∈") or (op in self.env.long_formulae):\n                \n                if not isinstance(left, TermNode):', 'elif op in ("=", "∈") or (op in self.env.long_formulae):\n                if target == "term": raise ParserError(f"Relation \'{op}\' not allowed in terms.")\n                if not isinstance(left, TermNode):')

with open('backend/Parser.py', 'w') as f:
    f.write(c)

