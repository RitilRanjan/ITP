def handle_intro2(env, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    from backend.AST import FormulaNode, TermNode, LongTerm, LongFormula, DefinitionType
    from backend.SubstitutionManager import matches_occurrence, extract_flat_nodes, map_flat_nodes_to_pattern
    from backend.CommandHandlers.utils import parse_universal_args, validate_new_name
    from backend.Parser import lex, reconstruct_string
    
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    parsed = parse_universal_args(env, "intro2", cmd_args, 2, validate_new_name, supports_equiv=True, namespace=None)
    if not parsed: return
    
    fixed_args, occurrence_idx, target_name, out_name, equiv_name = parsed
    schema_name = fixed_args[0]
    f1_name = fixed_args[1]
    
    if target_name not in env.formulae and target_name not in env.terms:
        print(f"Error: Target '{target_name}' not found.")
        return
        
    target_node = env.formulae[target_name] if target_name in env.formulae else env.terms[target_name]
    is_formula_target = isinstance(target_node, FormulaNode)
    
    if schema_name not in env.long_formulae and schema_name not in env.long_terms:
        print(f"Error: Schema '{schema_name}' not found.")
        return
        
    schema_def = env.long_formulae[schema_name] if schema_name in env.long_formulae else env.long_terms[schema_name]
    if schema_def.def_type != DefinitionType.SCHEMA:
        print(f"Error: '{schema_name}' is not a schema.")
        return
        
    if f1_name not in env.long_formulae and f1_name not in env.long_terms:
        print(f"Error: Replacement '{f1_name}' not found.")
        return
        
    f1_def = env.long_formulae[f1_name] if f1_name in env.long_formulae else env.long_terms[f1_name]
    
    from backend.AST import clone_ast
    
    def replace_schema_recursive(node, current_count):
        if current_count is None:
            current_count = [0]
            
        if isinstance(node, (LongTerm, LongFormula)) and node.definition_name == schema_name:
            current_count[0] += 1
            if matches_occurrence(occurrence_idx, current_count[0]):
                flat_nodes = extract_flat_nodes(schema_def.pattern, node.term_placeholders, node.var_placeholders, node.formula_placeholders, node.repetition_counts)
                flat_clones = [clone_ast(n) for n in flat_nodes]
                
                try:
                    tp, vp, fp, rc = map_flat_nodes_to_pattern(flat_clones, f1_def.pattern)
                except ValueError as e:
                    raise Exception(f"Failed to match schema placeholders: {e}")
                    
                if f1_name in env.long_formulae:
                    new_node = LongFormula(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type)
                else:
                    new_node = LongTerm(definition_name=f1_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=rc, def_type=f1_def.def_type)
                    
                new_node.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
                new_node.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
                return new_node
                
        # Recursion for LongTerm/LongFormula
        if isinstance(node, (LongTerm, LongFormula)):
            tp = {k: (replace_schema_recursive(v, current_count) if not isinstance(v, list) else [replace_schema_recursive(x, current_count) for x in v]) for k, v in node.term_placeholders.items()}
            vp = {k: (replace_schema_recursive(v, current_count) if not isinstance(v, list) else [replace_schema_recursive(x, current_count) for x in v]) for k, v in node.var_placeholders.items()}
            fp = {k: (replace_schema_recursive(v, current_count) if not isinstance(v, list) else [replace_schema_recursive(x, current_count) for x in v]) for k, v in node.formula_placeholders.items()}
            
            if isinstance(node, LongFormula):
                c = LongFormula(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type)
            else:
                c = LongTerm(definition_name=node.definition_name, term_placeholders=tp, var_placeholders=vp, formula_placeholders=fp, repetition_counts=node.repetition_counts, def_type=node.def_type)
            c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
            c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
            return c
            
        from backend.AST import Variable, DummyVariable, PropositionalVariable, MetaVariable, Bracket, Whitespace, Connective, Quantifier, Constant, Iota, Epsilon
        if isinstance(node, Variable): c = Variable(name=node.name)
        elif isinstance(node, DummyVariable): c = DummyVariable(name=node.name)
        elif isinstance(node, PropositionalVariable): c = PropositionalVariable(name=node.name)
        elif isinstance(node, MetaVariable): c = MetaVariable(name=node.name)
        elif isinstance(node, Bracket): c = Bracket(name=node.name)
        elif isinstance(node, Whitespace): c = Whitespace(name=node.name)
        elif isinstance(node, Constant): c = Constant(name=node.name)
        elif isinstance(node, Connective):
            c = Connective(name=node.name, arity=node.arity, arguments=[replace_schema_recursive(arg, current_count) for arg in node.arguments])
        elif isinstance(node, Quantifier):
            c = Quantifier(name=node.name, variable=clone_ast(node.variable), formula=replace_schema_recursive(node.formula, current_count))
        elif isinstance(node, Iota):
            c = Iota(variable=clone_ast(node.variable), formula=replace_schema_recursive(node.formula, current_count))
        elif isinstance(node, Epsilon):
            c = Epsilon(variable=clone_ast(node.variable), formula=replace_schema_recursive(node.formula, current_count))
        else:
            c = clone_ast(node)
            
        if not isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable, Bracket, Whitespace, Constant)):
            c.prefix_formatting = [clone_ast(f) for f in getattr(node, 'prefix_formatting', [])]
            c.postfix_formatting = [clone_ast(f) for f in getattr(node, 'postfix_formatting', [])]
        return c

    original_ast = target_node
    try:
        f_clone = replace_schema_recursive(target_node, [0])
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"Error during intro2 replacement: {e}")
        return

    if original_ast.is_structurally_equal(f_clone):
        print("Notice: No matching occurrences were found to substitute.")
        return
        
    from backend.CommandHandlers.transformation_handlers import proof_logger
    if is_formula_target:
        env.formulae[out_name] = f_clone
        if target_name == env.goal_formula_name:
            env.goal_formula_name = out_name
        print(f"Expanded '{schema_name}' to '{reconstruct_string(f_clone)}'")
        
        if target_name in env.theorems:
            env.add_theorem(out_name)
            print(f"Registered theorem '{out_name}'")
            proof_logger.log([(target_name, original_ast)], out_name, f_clone, f"intro2: {schema_name}")
            
        if equiv_name is not None:
            from backend.AST import Connective
            f3_node = Connective(name="⇔", arity=2, arguments=[clone_ast(original_ast), clone_ast(f_clone)])
            env.formulae[equiv_name] = f3_node
            env.add_theorem(equiv_name)
            print(f"Registered theorem '{equiv_name}' = '{reconstruct_string(f3_node)}'")
            proof_logger.log([(target_name, clone_ast(original_ast))], equiv_name, f3_node, f"intro2: {schema_name}-equiv")
    else:
        env.terms[out_name] = f_clone
        print(f"Expanded term '{schema_name}' to '{reconstruct_string(f_clone)}'")

