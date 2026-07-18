import re
with open('backend/Parser.py', 'r') as f:
    c = f.read()

c = c.replace('return LongTerm(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts)', 'return LongTerm(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern)')

c = c.replace('return LongFormula(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts)', 'return LongFormula(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern)')

c = c.replace('left = LongFormula(definition_name=op_name, term_placeholders={"?t1": left, "?t2": right}, def_type=lf_def.def_type)', 'left = LongFormula(definition_name=op_name, term_placeholders={"?t1": left, "?t2": right}, def_type=lf_def.def_type, pattern=lf_def.pattern)')

c = c.replace('left = LongTerm(definition_name=op, term_placeholders={"?t1": left, "?t2": right}, def_type=lt_def.def_type)', 'left = LongTerm(definition_name=op, term_placeholders={"?t1": left, "?t2": right}, def_type=lt_def.def_type, pattern=lt_def.pattern)')

# And update reconstruct_string_raw to use node.pattern instead of lex(node.definition_name)
c = c.replace('pat_tokens = [t for t in lex(node.definition_name) if not t.isspace()]', 'pat_tokens = node.pattern')

with open('backend/Parser.py', 'w') as f:
    f.write(c)
