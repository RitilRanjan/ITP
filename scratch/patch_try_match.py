import re
with open('backend/Parser.py', 'r') as f:
    c = f.read()

old_block = '''        from backend.AST import LongTerm, LongFormula
        if expected_target == "term":
            return LongTerm(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern_struct)
        elif expected_target == "formula":
            return LongFormula(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern_struct)
        return None'''

new_block = '''        from backend.AST import LongTerm, LongFormula, Constant, DummyVariable, Variable
        if expected_target == "term":
            return LongTerm(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern_struct)
        elif expected_target == "formula":
            return LongFormula(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern_struct)
        elif expected_target == "term_short":
            if name in self.env.variables:
                return Variable(name=name)
            elif name in self.env.dummy_variables:
                return DummyVariable(name=name)
            return Constant(name=name)
        elif expected_target == "formula_short":
            from backend.AST import PropositionalVariable
            if name in self.env.propositional_variables:
                return PropositionalVariable(name=name)
            raise ParserError(f"Formula short macro {name} matched but not implemented as AST node properly.")
        return None'''

c = c.replace(old_block, new_block)
with open('backend/Parser.py', 'w') as f:
    f.write(c)
