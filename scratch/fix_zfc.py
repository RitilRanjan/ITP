import re

with open('backend/ZFC_Rules.py', 'r') as f:
    content = f.read()

# Fix imports
content = re.sub(r'Function, FunctionType, Relation, RelationType,', 'LongTerm, LongFormula,', content)

# Fix are_isomorphic
old_match = """        elif isinstance(p1, (Function, Relation, Connective)):
            if p1.name != p2.name or len(p1.arguments) != len(p2.arguments):
                return False
            for a1, a2 in zip(p1.arguments, p2.arguments):
                if not match(a1, a2):
                    return False
            return True"""
new_match = """        elif isinstance(p1, Connective):
            if p1.name != p2.name or len(p1.arguments) != len(p2.arguments):
                return False
            for a1, a2 in zip(p1.arguments, p2.arguments):
                if not match(a1, a2):
                    return False
            return True
            
        elif isinstance(p1, (LongTerm, LongFormula)):
            if p1.definition_name != p2.definition_name:
                return False
            for key in p1.term_placeholders:
                if key not in p2.term_placeholders or not match(p1.term_placeholders[key], p2.term_placeholders[key]):
                    return False
            for key in p1.var_placeholders:
                if key not in p2.var_placeholders or not match(p1.var_placeholders[key], p2.var_placeholders[key]):
                    return False
            for key in p1.formula_placeholders:
                if key not in p2.formula_placeholders or not match(p1.formula_placeholders[key], p2.formula_placeholders[key]):
                    return False
            return True"""
content = content.replace(old_match, new_match)

# Remove env setup dummy
env_setup_old = """    env = Environment()
    dummy = Variable("x")
    env.add_term(Function("S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_formula(Relation("=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation("∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env"""
env_setup_new = """    env = Environment()
    return env"""
content = content.replace(env_setup_old, env_setup_new)

# Fix match_union
content = content.replace('isinstance(left, Relation) or left.name != "∈"', 'isinstance(left, LongFormula) or left.definition_name != "in"')
content = content.replace('len(left.arguments) != 2', '"t1" not in left.term_placeholders')
content = content.replace('left.arguments[0]', 'left.term_placeholders["t1"]')
content = content.replace('left.arguments[1]', 'left.term_placeholders["t2"]')

content = content.replace('isinstance(c1, Relation) or c1.name != "∈"', 'isinstance(c1, LongFormula) or c1.definition_name != "in"')
content = content.replace('len(c1.arguments) != 2', '"t1" not in c1.term_placeholders')
content = content.replace('c1.arguments[0]', 'c1.term_placeholders["t1"]')
content = content.replace('c1.arguments[1]', 'c1.term_placeholders["t2"]')

content = content.replace('isinstance(ant_right, Relation) or ant_right.name != "="', 'isinstance(ant_right, LongFormula) or ant_right.definition_name != "="')
content = content.replace('len(ant_right.arguments) != 2', '"t1" not in ant_right.term_placeholders')
content = content.replace('ant_right.arguments[0]', 'ant_right.term_placeholders["t1"]')
content = content.replace('ant_right.arguments[1]', 'ant_right.term_placeholders["t2"]')

with open('backend/ZFC_Rules.py', 'w') as f:
    f.write(content)

