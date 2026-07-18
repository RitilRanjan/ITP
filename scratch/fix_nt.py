with open('backend/NT_Rules.py', 'r') as f:
    c = f.read()

# Imports
c = c.replace('Function, Constant', 'LongTerm, LongFormula, Constant')
c = c.replace('Relation, ', '')

# =
c = c.replace('isinstance(lhs, Relation) or lhs.name != "="', 'isinstance(lhs, LongFormula) or lhs.definition_name != "="')
c = c.replace('isinstance(rhs, Relation) or rhs.name != "="', 'isinstance(rhs, LongFormula) or rhs.definition_name != "="')
c = c.replace('isinstance(body, Relation) or body.name != "="', 'isinstance(body, LongFormula) or body.definition_name != "="')
c = c.replace('isinstance(formula, Relation) or formula.name != "="', 'isinstance(formula, LongFormula) or formula.definition_name != "="')

# = arguments
c = c.replace('l_arg1, l_arg2 = lhs.arguments', 'l_arg1, l_arg2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]')
c = c.replace('r_arg1, r_arg2 = rhs.arguments', 'r_arg1, r_arg2 = rhs.term_placeholders["t1"], rhs.term_placeholders["t2"]')
c = c.replace('lhs, rhs = body.arguments', 'lhs, rhs = body.term_placeholders["t1"], body.term_placeholders["t2"]')
c = c.replace('lhs, rhs = formula.arguments', 'lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]')

# S
c = c.replace('isinstance(l_arg1, Function) or l_arg1.name != "S"', 'isinstance(l_arg1, LongTerm) or l_arg1.definition_name != "S"')
c = c.replace('isinstance(l_arg2, Function) or l_arg2.name != "S"', 'isinstance(l_arg2, LongTerm) or l_arg2.definition_name != "S"')
c = c.replace('isinstance(lhs, Function) or lhs.name != "S"', 'isinstance(lhs, LongTerm) or lhs.definition_name != "S"')
c = c.replace('isinstance(rhs, Function) or rhs.name != "S"', 'isinstance(rhs, LongTerm) or rhs.definition_name != "S"')
c = c.replace('isinstance(l2, Function) or l2.name != "S"', 'isinstance(l2, LongTerm) or l2.definition_name != "S"')

# S arguments
c = c.replace('l_arg1.arguments[0]', 'l_arg1.term_placeholders["t1"]')
c = c.replace('l_arg2.arguments[0]', 'l_arg2.term_placeholders["t1"]')
c = c.replace('lhs.arguments[0]', 'lhs.term_placeholders["t1"]')
c = c.replace('rhs.arguments[0]', 'rhs.term_placeholders["t1"]')
c = c.replace('l2.arguments[0]', 'l2.term_placeholders["t1"]')

# +
c = c.replace('isinstance(lhs, Function) or lhs.name != "+"', 'isinstance(lhs, LongTerm) or lhs.definition_name != "+"')
c = c.replace('isinstance(r_arg, Function) or r_arg.name != "+"', 'isinstance(r_arg, LongTerm) or r_arg.definition_name != "+"')
c = c.replace('isinstance(rhs, Function) or rhs.name != "+"', 'isinstance(rhs, LongTerm) or rhs.definition_name != "+"')
c = c.replace('l1, l2 = lhs.arguments', 'l1, l2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]')
c = c.replace('r1, r2 = r_arg.arguments', 'r1, r2 = r_arg.term_placeholders["t1"], r_arg.term_placeholders["t2"]')

# *
c = c.replace('isinstance(lhs, Function) or lhs.name != "*"', 'isinstance(lhs, LongTerm) or lhs.definition_name != "*"')
c = c.replace('isinstance(r1, Function) or r1.name != "*"', 'isinstance(r1, LongTerm) or r1.definition_name != "*"')
c = c.replace('r1.arguments', 'r1.term_placeholders["t1"], r1.term_placeholders["t2"]')

# ^
c = c.replace('isinstance(lhs, Function) or lhs.name != "^"', 'isinstance(lhs, LongTerm) or lhs.definition_name != "^"')
c = c.replace('isinstance(r1, Function) or r1.name != "^"', 'isinstance(r1, LongTerm) or r1.definition_name != "^"')

# Induction schema Function creation
# substitute_all(psi_Sx_expected, x_var.name, Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[Variable(x_var.name)]), None)
c = c.replace('from backend.AST import FunctionType', '')
c = c.replace('Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[Variable(x_var.name)])', 'LongTerm(definition_name="S", term_placeholders={"t1": Variable(x_var.name)}, var_placeholders={}, formula_placeholders={}, repetition_counts={})')

with open('backend/NT_Rules.py', 'w') as f:
    f.write(c)

