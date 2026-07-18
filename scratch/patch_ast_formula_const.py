import re
with open('backend/AST.py', 'r') as f:
    c = f.read()

c = c.replace('class Connective(FormulaNode):', 'class FormulaConstant(FormulaNode):\n    """Represents a formula macro."""\n    name: str\n    priority: int = 0\n\n@dataclass\nclass Connective(FormulaNode):')

with open('backend/AST.py', 'w') as f:
    f.write(c)
