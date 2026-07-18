import re

with open('backend/AST.py', 'r') as f:
    c = f.read()

c = c.replace('class LongTerm(TermNode):\n    """Represents a custom-defined long term with placeholders."""\n    definition_name: str', 'class LongTerm(TermNode):\n    """Represents a custom-defined long term with placeholders."""\n    definition_name: str\n    pattern: List[str] = field(default_factory=list)')

c = c.replace('class LongFormula(FormulaNode):\n    """Represents a custom-defined long formula with placeholders."""\n    definition_name: str', 'class LongFormula(FormulaNode):\n    """Represents a custom-defined long formula with placeholders."""\n    definition_name: str\n    pattern: List[str] = field(default_factory=list)')

with open('backend/AST.py', 'w') as f:
    f.write(c)
