with open('backend/Parser.py', 'r') as f:
    c = f.read()

c = c.replace('elif op in ("=", "∈") or (op in self.env.long_formulae):\n                right_target = "term"', 'elif op in ("=", "∈") or (op in self.env.long_formulae):\n                if target == "term": raise ParserError(f"Relation \'{op}\' not allowed in terms.")\n                right_target = "term"')

with open('backend/Parser.py', 'w') as f:
    f.write(c)
