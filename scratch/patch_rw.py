import re

with open('backend/CommandHandlers/transformation_handlers.py', 'r') as f:
    content = f.read()

# Edit 1: For long definitions
pattern1 = r"""def_ast = parse_term\(definition_expr, env\) if name in env\.long_terms else parse_fol_formula\(definition_expr, env\)"""
replacement1 = """def_ast = parse_term(definition_expr, env) if name in env.long_terms else parse_fol_formula(definition_expr, env)
        from backend.AST import Bracket
        def_ast.prefix_formatting.insert(0, Bracket(name="RW_MARKER"))"""
content = re.sub(pattern1, replacement1, content)

# Edit 2: For regular definitions
pattern2 = r"""        if name in env\.terms:
            def_ast = env\.terms\[name\]
            from backend\.AST import Constant, Variable
            if name in env\.variables or name in env\.local_variables:
                search_node = Variable\(name\)
            else:
                search_node = Constant\(name\)
            is_prop = False
        else:
            def_ast = env\.formulae\[name\]
            from backend\.AST import PropositionalVariable
            search_node = PropositionalVariable\(name\)
            is_prop = True"""

replacement2 = """        if name in env.terms:
            def_ast = clone_ast(env.terms[name])
            from backend.AST import Constant, Variable
            if name in env.variables or name in env.local_variables:
                search_node = Variable(name)
            else:
                search_node = Constant(name)
            is_prop = False
        else:
            def_ast = clone_ast(env.formulae[name])
            from backend.AST import PropositionalVariable
            search_node = PropositionalVariable(name)
            is_prop = True
            
        from backend.AST import Bracket
        def_ast.prefix_formatting.insert(0, Bracket(name="RW_MARKER"))"""
content = content.replace(
"""        if name in env.terms:
            def_ast = env.terms[name]
            from backend.AST import Constant, Variable
            if name in env.variables or name in env.local_variables:
                search_node = Variable(name)
            else:
                search_node = Constant(name)
            is_prop = False
        else:
            def_ast = env.formulae[name]
            from backend.AST import PropositionalVariable
            search_node = PropositionalVariable(name)
            is_prop = True""", replacement2)

# Edit 3: Check for precedence issues
pattern3 = r"""    if original_ast\.is_structurally_equal\(f_clone\):
        print\("Notice: No matching occurrences were found to substitute\."\)
        return"""

replacement3 = """    if original_ast.is_structurally_equal(f_clone):
        print("Notice: No matching occurrences were found to substitute.")
        return
        
    from backend.AST import Bracket
    expanded_nodes = []
    
    def find_and_remove_marker(node):
        if hasattr(node, "prefix_formatting"):
            if any(isinstance(f, Bracket) and f.name == "RW_MARKER" for f in node.prefix_formatting):
                node.prefix_formatting = [f for f in node.prefix_formatting if not (isinstance(f, Bracket) and f.name == "RW_MARKER")]
                expanded_nodes.append(node)
        # Recurse safely
        if hasattr(node, "arguments"):
            for arg in node.arguments:
                find_and_remove_marker(arg)
        elif hasattr(node, "term_placeholders"):
            for arg in node.term_placeholders.values():
                find_and_remove_marker(arg)
        elif hasattr(node, "formula_placeholders"):
            for arg in node.formula_placeholders.values():
                find_and_remove_marker(arg)
        elif hasattr(node, "variable"):
            find_and_remove_marker(node.variable)
        elif hasattr(node, "formula"):
            find_and_remove_marker(node.formula)
        elif hasattr(node, "quantifiers"):
            for q in node.quantifiers:
                find_and_remove_marker(q)
            find_and_remove_marker(node.formula)
        elif hasattr(node, "condition"):
            find_and_remove_marker(node.condition)
            find_and_remove_marker(node.term)
            
    find_and_remove_marker(f_clone)
    
    try:
        from backend.Parser import parse_term, parse_fol_formula
        from backend.AST import is_structurally_equal, reconstruct_string
        f_clone_str = reconstruct_string(f_clone)
        if is_formula_target:
            re_parsed = parse_fol_formula(f_clone_str, env)
        else:
            re_parsed = parse_term(f_clone_str, env)
            
        if not is_structurally_equal(re_parsed, f_clone):
            raise Exception("Mismatch")
    except Exception:
        # Precedence issue! Add brackets to all expanded nodes.
        for n in expanded_nodes:
            has_brackets = False
            if n.prefix_formatting and isinstance(n.prefix_formatting[0], Bracket) and n.prefix_formatting[0].name == "(":
                has_brackets = True
            if not has_brackets:
                n.prefix_formatting.insert(0, Bracket(name="("))
                n.postfix_formatting.append(Bracket(name=")"))"""

content = content.replace(
"""    if original_ast.is_structurally_equal(f_clone):
        print("Notice: No matching occurrences were found to substitute.")
        return""", replacement3)

with open('backend/CommandHandlers/transformation_handlers.py', 'w') as f:
    f.write(content)
