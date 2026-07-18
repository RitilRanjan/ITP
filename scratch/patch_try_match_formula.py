import re
with open('backend/Parser.py', 'r') as f:
    c = f.read()

old_block = '''        elif expected_target == "formula_short":
            from backend.AST import PropositionalVariable
            if name in self.env.propositional_variables:
                return PropositionalVariable(name=name)
            raise ParserError(f"Formula short macro {name} matched but not implemented as AST node properly.")'''

new_block = '''        elif expected_target == "formula_short":
            from backend.AST import PropositionalVariable, FormulaConstant
            if name in self.env.propositional_variables:
                return PropositionalVariable(name=name)
            return FormulaConstant(name=name)'''

c = c.replace(old_block, new_block)
with open('backend/Parser.py', 'w') as f:
    f.write(c)
