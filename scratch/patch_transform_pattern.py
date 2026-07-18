import re
with open('backend/CommandHandlers/transformation_handlers.py', 'r') as f:
    c = f.read()

c = c.replace('new_node = LongTerm(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type)', 'new_node = LongTerm(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type, pattern=f1_def.pattern)')
c = c.replace('new_node = LongFormula(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type)', 'new_node = LongFormula(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type, pattern=f1_def.pattern)')
c = c.replace('c = LongTerm(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type)', 'c = LongTerm(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type, pattern=node.pattern)')
c = c.replace('c = LongFormula(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type)', 'c = LongFormula(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type, pattern=node.pattern)')

with open('backend/CommandHandlers/transformation_handlers.py', 'w') as f:
    f.write(c)

with open('backend/SubstitutionManager.py', 'r') as f:
    c = f.read()

c = c.replace('c = LongTerm(\n            definition_name=node.definition_name,\n            term_placeholders=t_args,\n            var_placeholders=v_args,\n            formula_placeholders=f_args,\n            repetition_counts=dict(node.repetition_counts)\n        )', 'c = LongTerm(\n            definition_name=node.definition_name,\n            term_placeholders=t_args,\n            var_placeholders=v_args,\n            formula_placeholders=f_args,\n            repetition_counts=dict(node.repetition_counts),\n            pattern=node.pattern\n        )')

c = c.replace('c = LongFormula(\n            definition_name=node.definition_name,\n            term_placeholders=t_args,\n            var_placeholders=v_args,\n            formula_placeholders=f_args,\n            repetition_counts=dict(node.repetition_counts)\n        )', 'c = LongFormula(\n            definition_name=node.definition_name,\n            term_placeholders=t_args,\n            var_placeholders=v_args,\n            formula_placeholders=f_args,\n            repetition_counts=dict(node.repetition_counts),\n            pattern=node.pattern\n        )')

with open('backend/SubstitutionManager.py', 'w') as f:
    f.write(c)

with open('backend/DefinitionReplacer.py', 'r') as f:
    c = f.read()

c = c.replace('c = LongTerm(definition_name=node.definition_name, term_placeholders=t_args, var_placeholders=v_args, formula_placeholders=f_args, repetition_counts=dict(node.repetition_counts))', 'c = LongTerm(definition_name=node.definition_name, term_placeholders=t_args, var_placeholders=v_args, formula_placeholders=f_args, repetition_counts=dict(node.repetition_counts), pattern=node.pattern)')

c = c.replace('c = LongFormula(definition_name=node.definition_name, term_placeholders=t_args, var_placeholders=v_args, formula_placeholders=f_args, repetition_counts=dict(node.repetition_counts))', 'c = LongFormula(definition_name=node.definition_name, term_placeholders=t_args, var_placeholders=v_args, formula_placeholders=f_args, repetition_counts=dict(node.repetition_counts), pattern=node.pattern)')

with open('backend/DefinitionReplacer.py', 'w') as f:
    f.write(c)

