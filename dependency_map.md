# Granular Dependency Map
This graph shows dependencies between individual classes and functions across the codebase.\n
```mermaid
graph TD
  subgraph rewrite_main
    rewrite_main_rewrite(rewrite):::funcNode
  end
  subgraph GraphSearch
    GraphSearch_SearchLimitExceeded[SearchLimitExceeded]:::classNode
    GraphSearch_SearchLimits[SearchLimits]:::classNode
    GraphSearch_Vocabulary[Vocabulary]:::classNode
    GraphSearch_generate_terms(generate_terms):::funcNode
    GraphSearch_apply_qr_rules(apply_qr_rules):::funcNode
    GraphSearch_generate_formulas(generate_formulas):::funcNode
    GraphSearch_check_time(check_time):::funcNode
    GraphSearch_apply_modus_ponens(apply_modus_ponens):::funcNode
    GraphSearch_traverse(traverse):::funcNode
    GraphSearch_extract_v(extract_v):::funcNode
    GraphSearch_extract_vocabulary(extract_vocabulary):::funcNode
    GraphSearch_forward_search(forward_search):::funcNode
    GraphSearch_check_axioms(check_axioms):::funcNode
    GraphSearch_check_space(check_space):::funcNode
  end
  subgraph ProofLogger
    ProofLogger_ProofLogger[ProofLogger]:::classNode
    ProofLogger_log_rule(log_rule):::funcNode
    ProofLogger_open(open):::funcNode
    ProofLogger_log(log):::funcNode
    ProofLogger_log_axiom(log_axiom):::funcNode
    ProofLogger_log_summary(log_summary):::funcNode
    ProofLogger_close(close):::funcNode
  end
  subgraph extract_deps
    extract_deps_get_local_imports(get_local_imports):::funcNode
  end
  subgraph extract_transformations
    extract_transformations_extract(extract):::funcNode
    extract_transformations_clean_lines(clean_lines):::funcNode
    extract_transformations_replace_continue(replace_continue):::funcNode
  end
  subgraph TruthEvaluator
    TruthEvaluator_get_prop_variables(get_prop_variables):::funcNode
    TruthEvaluator_evaluate_prop(evaluate_prop):::funcNode
    TruthEvaluator_is_tautology(is_tautology):::funcNode
  end
  subgraph SequentEvaluator
    SequentEvaluator_prove_sequent(prove_sequent):::funcNode
    SequentEvaluator_is_tautology_sequent(is_tautology_sequent):::funcNode
  end
  subgraph AutoProver
    AutoProver_collect_leaf_sequents(collect_leaf_sequents):::funcNode
    AutoProver_auto_prove(auto_prove):::funcNode
    AutoProver_make_sequent_formula(make_sequent_formula):::funcNode
    AutoProver_decode_propositional_to_fol(decode_propositional_to_fol):::funcNode
  end
  subgraph ProofGenerator
    ProofGenerator_ProofGenerator[ProofGenerator]:::classNode
    ProofGenerator_dfs(dfs):::funcNode
    ProofGenerator_clause_to_string(clause_to_string):::funcNode
    ProofGenerator_generate_proof(generate_proof):::funcNode
  end
  subgraph Frontend
    Frontend_UnrecognizedSymbolError[UnrecognizedSymbolError]:::classNode
    Frontend_ParserError[ParserError]:::classNode
    Frontend_Parser[Parser]:::classNode
    Frontend_peek(peek):::funcNode
    Frontend_get_precedence(get_precedence):::funcNode
    Frontend_parse(parse):::funcNode
    Frontend_reconstruct_string(reconstruct_string):::funcNode
    Frontend__green(_green):::funcNode
    Frontend_parse_quantifier(parse_quantifier):::funcNode
    Frontend_consume_formatting(consume_formatting):::funcNode
    Frontend_parse_fol_formula(parse_fol_formula):::funcNode
    Frontend_parse_term(parse_term):::funcNode
    Frontend_colorize_formula(colorize_formula):::funcNode
    Frontend_lex(lex):::funcNode
    Frontend__bold(_bold):::funcNode
    Frontend_reconstruct_string_raw(reconstruct_string_raw):::funcNode
    Frontend_parse_prop_formula(parse_prop_formula):::funcNode
    Frontend_strip_ansi(strip_ansi):::funcNode
    Frontend_parse_expr(parse_expr):::funcNode
    Frontend_consume(consume):::funcNode
    Frontend_parse_prefix(parse_prefix):::funcNode
    Frontend__cyan(_cyan):::funcNode
    Frontend__yellow(_yellow):::funcNode
    Frontend_show_environment(show_environment):::funcNode
  end
  subgraph StorageManager
    StorageManager_load_environment_state(load_environment_state):::funcNode
    StorageManager_save_history(save_history):::funcNode
    StorageManager_load_history(load_history):::funcNode
    StorageManager_save_environment_state(save_environment_state):::funcNode
    StorageManager_get_env_chain(get_env_chain):::funcNode
  end
  subgraph DefinitionExpander
    DefinitionExpander_VariableCaptureError[VariableCaptureError]:::classNode
    DefinitionExpander_expand_epsilon_function_in_formula(expand_epsilon_function_in_formula):::funcNode
    DefinitionExpander_get_enclosing_bound_vars(get_enclosing_bound_vars):::funcNode
    DefinitionExpander_substitute_dummy_in_formula(substitute_dummy_in_formula):::funcNode
    DefinitionExpander_expand_user_defined_function_in_term(expand_user_defined_function_in_term):::funcNode
    DefinitionExpander_collect_and_map(collect_and_map):::funcNode
    DefinitionExpander_expand_user_defined_function_in_formula(expand_user_defined_function_in_formula):::funcNode
    DefinitionExpander_expand_unique_existential_in_formula(expand_unique_existential_in_formula):::funcNode
    DefinitionExpander_get_internal_captures(get_internal_captures):::funcNode
    DefinitionExpander_in_place_replace_node(in_place_replace_node):::funcNode
    DefinitionExpander_expand_iota_function_in_formula(expand_iota_function_in_formula):::funcNode
    DefinitionExpander_expand_user_defined_relation_in_formula(expand_user_defined_relation_in_formula):::funcNode
    DefinitionExpander_collect_occurrences(collect_occurrences):::funcNode
    DefinitionExpander_expand_set_builder_in_formula(expand_set_builder_in_formula):::funcNode
    DefinitionExpander_expand_existential_in_formula(expand_existential_in_formula):::funcNode
  end
  subgraph DeductiveSystem
    DeductiveSystem_axiom_E3(axiom_E3):::funcNode
    DeductiveSystem_rule_PC1(rule_PC1):::funcNode
    DeductiveSystem_axiom_Q1(axiom_Q1):::funcNode
    DeductiveSystem_axiom_E1(axiom_E1):::funcNode
    DeductiveSystem_build_implication_formula(build_implication_formula):::funcNode
    DeductiveSystem_axiom_Q2(axiom_Q2):::funcNode
    DeductiveSystem_axiom_E2(axiom_E2):::funcNode
    DeductiveSystem_rule_QR1(rule_QR1):::funcNode
    DeductiveSystem_rule_PC2(rule_PC2):::funcNode
    DeductiveSystem_get_conjuncts(get_conjuncts):::funcNode
    DeductiveSystem_rule_QR2(rule_QR2):::funcNode
  end
  subgraph Environment
    Environment_ASTEncoder[ASTEncoder]:::classNode
    Environment_Environment[Environment]:::classNode
    Environment_add_propositional_variable(add_propositional_variable):::funcNode
    Environment_add_formula(add_formula):::funcNode
    Environment_from_json(from_json):::funcNode
    Environment_add_dummy_variable(add_dummy_variable):::funcNode
    Environment_to_json(to_json):::funcNode
    Environment_add_term(add_term):::funcNode
    Environment_add_theorem(add_theorem):::funcNode
    Environment_add_variable(add_variable):::funcNode
    Environment_remove_theorem(remove_theorem):::funcNode
    Environment_add_meta_variable(add_meta_variable):::funcNode
    Environment_default(default):::funcNode
  end
  subgraph app
    app_get_dummy_env(get_dummy_env):::funcNode
    app_main(main):::funcNode
    app_print_header(print_header):::funcNode
  end
  subgraph AST
    AST_MetaVariable[MetaVariable]:::classNode
    AST_Relation[Relation]:::classNode
    AST_RelationType[RelationType]:::classNode
    AST_PropositionalVariable[PropositionalVariable]:::classNode
    AST_Function[Function]:::classNode
    AST_TermNode[TermNode]:::classNode
    AST_Connective[Connective]:::classNode
    AST_Node[Node]:::classNode
    AST_FunctionType[FunctionType]:::classNode
    AST_DummyVariable[DummyVariable]:::classNode
    AST_Bracket[Bracket]:::classNode
    AST_Whitespace[Whitespace]:::classNode
    AST_SetBuilder[SetBuilder]:::classNode
    AST_Quantifier[Quantifier]:::classNode
    AST_FormulaNode[FormulaNode]:::classNode
    AST_Variable[Variable]:::classNode
    AST_is_structurally_equal(is_structurally_equal):::funcNode
  end
  subgraph main
    main_handle_variable_capture_interactive(handle_variable_capture_interactive):::funcNode
    main_get_default_env(get_default_env):::funcNode
    main_validate_new_name(validate_new_name):::funcNode
    main_get_target_resolutions(get_target_resolutions):::funcNode
    main_main(main):::funcNode
    main_print(print):::funcNode
  end
  subgraph test_capture_mock
    test_capture_mock_mock_input(mock_input):::funcNode
  end
  subgraph PropAbstraction
    PropAbstraction_clear_right_postfix_formatting(clear_right_postfix_formatting):::funcNode
    PropAbstraction_get_or_create_prop_var(get_or_create_prop_var):::funcNode
    PropAbstraction_abstract_to_propositional_with_mapping(abstract_to_propositional_with_mapping):::funcNode
    PropAbstraction_clone_ast_list(clone_ast_list):::funcNode
    PropAbstraction_recurse(recurse):::funcNode
    PropAbstraction_collect_total_postfix(collect_total_postfix):::funcNode
    PropAbstraction_clear_left_prefix_formatting(clear_left_prefix_formatting):::funcNode
    PropAbstraction_abstract_to_propositional(abstract_to_propositional):::funcNode
    PropAbstraction_collect_total_prefix(collect_total_prefix):::funcNode
  end
  subgraph SubstitutionManager
    SubstitutionManager_substitute_term(substitute_term):::funcNode
    SubstitutionManager_get_free(get_free):::funcNode
    SubstitutionManager_substitute_proposition(substitute_proposition):::funcNode
    SubstitutionManager_substitute_bound(substitute_bound):::funcNode
    SubstitutionManager_check_bound(check_bound):::funcNode
    SubstitutionManager_check_free(check_free):::funcNode
    SubstitutionManager_collect_term_vars_list(collect_term_vars_list):::funcNode
    SubstitutionManager_is_substitutable_free(is_substitutable_free):::funcNode
    SubstitutionManager_clone_ast(clone_ast):::funcNode
    SubstitutionManager_add_double_neg(add_double_neg):::funcNode
    SubstitutionManager_get_term_vars(get_term_vars):::funcNode
    SubstitutionManager_substitute_all(substitute_all):::funcNode
    SubstitutionManager_substitute_free(substitute_free):::funcNode
    SubstitutionManager__rebuild_non_formula(_rebuild_non_formula):::funcNode
    SubstitutionManager_collect_prop_vars_list(collect_prop_vars_list):::funcNode
    SubstitutionManager__is_double_neg(_is_double_neg):::funcNode
    SubstitutionManager_is_substitutable_bound(is_substitutable_bound):::funcNode
    SubstitutionManager_find_substituted(find_substituted):::funcNode
    SubstitutionManager__rebuild_node(_rebuild_node):::funcNode
    SubstitutionManager_match_nodes(match_nodes):::funcNode
    SubstitutionManager_get_bound(get_bound):::funcNode
    SubstitutionManager_collect_all_occurrences(collect_all_occurrences):::funcNode
    SubstitutionManager_in_place_replace(in_place_replace):::funcNode
    SubstitutionManager_is_valid_renaming(is_valid_renaming):::funcNode
    SubstitutionManager_replace_structurally(replace_structurally):::funcNode
    SubstitutionManager_remove_double_neg(remove_double_neg):::funcNode
  end
  subgraph ZFC_Rules
    ZFC_Rules_match(match):::funcNode
    ZFC_Rules_get_parsing_env(get_parsing_env):::funcNode
    ZFC_Rules_strip_universal_quantifiers(strip_universal_quantifiers):::funcNode
    ZFC_Rules_axiom_regularity(axiom_regularity):::funcNode
    ZFC_Rules_axiom_pairing(axiom_pairing):::funcNode
    ZFC_Rules_axiom_power_set(axiom_power_set):::funcNode
    ZFC_Rules_axiom_infinity(axiom_infinity):::funcNode
    ZFC_Rules_axiom_replacement(axiom_replacement):::funcNode
    ZFC_Rules_axiom_choice(axiom_choice):::funcNode
    ZFC_Rules_axiom_union(axiom_union):::funcNode
    ZFC_Rules_axiom_specification(axiom_specification):::funcNode
    ZFC_Rules_are_isomorphic(are_isomorphic):::funcNode
    ZFC_Rules_axiom_extension(axiom_extension):::funcNode
  end
  subgraph verify_fold_capture
    verify_fold_capture_read_until(read_until):::funcNode
    verify_fold_capture_run_test(run_test):::funcNode
  end
  subgraph BackwardSearch
    BackwardSearch_AdvancedSearchEngine[AdvancedSearchEngine]:::classNode
    BackwardSearch_finish_proof(finish_proof):::funcNode
    BackwardSearch_is_term_greater(is_term_greater):::funcNode
    BackwardSearch_skolemize(skolemize):::funcNode
    BackwardSearch_advanced_search(advanced_search):::funcNode
    BackwardSearch_term_weight(term_weight):::funcNode
    BackwardSearch_extract_clauses(extract_clauses):::funcNode
    BackwardSearch_apply_substitution_at_path(apply_substitution_at_path):::funcNode
    BackwardSearch_resolve(resolve):::funcNode
    BackwardSearch_extract_literals(extract_literals):::funcNode
    BackwardSearch_factorize(factorize):::funcNode
    BackwardSearch__standardize_term(_standardize_term):::funcNode
    BackwardSearch_paramodulate(paramodulate):::funcNode
    BackwardSearch_backward_subsume(backward_subsume):::funcNode
    BackwardSearch_solve(solve):::funcNode
    BackwardSearch_one_way_match(one_way_match):::funcNode
    BackwardSearch_to_nnf(to_nnf):::funcNode
    BackwardSearch_visit(visit):::funcNode
    BackwardSearch_unify(unify):::funcNode
    BackwardSearch_is_forward_subsumed(is_forward_subsumed):::funcNode
    BackwardSearch_get_subterms_with_paths(get_subterms_with_paths):::funcNode
    BackwardSearch_subsumes(subsumes):::funcNode
    BackwardSearch_occurs_check(occurs_check):::funcNode
    BackwardSearch_try_unify_all(try_unify_all):::funcNode
    BackwardSearch_are_variants(are_variants):::funcNode
    BackwardSearch_add_clause(add_clause):::funcNode
    BackwardSearch_distribute_or_over_and(distribute_or_over_and):::funcNode
    BackwardSearch_try_paramodulate(try_paramodulate):::funcNode
    BackwardSearch_apply_substitution(apply_substitution):::funcNode
    BackwardSearch_get_literal_core(get_literal_core):::funcNode
    BackwardSearch_standardize_variables(standardize_variables):::funcNode
    BackwardSearch_drop_universals(drop_universals):::funcNode
    BackwardSearch_process_to_cnf(process_to_cnf):::funcNode
    BackwardSearch_clause_to_string(clause_to_string):::funcNode
    BackwardSearch_get_var_counts(get_var_counts):::funcNode
    BackwardSearch_backtrack(backtrack):::funcNode
    BackwardSearch_add_to_history(add_to_history):::funcNode
    BackwardSearch_eliminate_implications(eliminate_implications):::funcNode
    BackwardSearch_backward_search(backward_search):::funcNode
  end
  rewrite_main_rewrite --> ProofLogger_open
  rewrite_main_rewrite --> main_print
  GraphSearch_extract_vocabulary --> AST_Function
  GraphSearch_extract_vocabulary --> AST_DummyVariable
  GraphSearch_extract_vocabulary --> GraphSearch_traverse
  GraphSearch_extract_vocabulary --> AST_PropositionalVariable
  GraphSearch_extract_vocabulary --> GraphSearch_Vocabulary
  GraphSearch_extract_vocabulary --> AST_Variable
  GraphSearch_extract_vocabulary --> AST_Relation
  GraphSearch_generate_terms --> AST_is_structurally_equal
  GraphSearch_generate_terms --> SubstitutionManager_clone_ast
  GraphSearch_generate_terms --> AST_Function
  GraphSearch_generate_formulas --> AST_Connective
  GraphSearch_generate_formulas --> SubstitutionManager_clone_ast
  GraphSearch_generate_formulas --> AST_Relation
  GraphSearch_generate_formulas --> AST_Quantifier
  GraphSearch_check_axioms --> DeductiveSystem_axiom_E2
  GraphSearch_check_axioms --> DeductiveSystem_axiom_E1
  GraphSearch_check_axioms --> DeductiveSystem_axiom_Q1
  GraphSearch_check_axioms --> DeductiveSystem_axiom_E3
  GraphSearch_check_axioms --> DeductiveSystem_axiom_Q2
  GraphSearch_check_axioms --> DeductiveSystem_rule_PC2
  GraphSearch_apply_modus_ponens --> AST_is_structurally_equal
  GraphSearch_apply_modus_ponens --> SubstitutionManager_clone_ast
  GraphSearch_apply_qr_rules --> GraphSearch_extract_v
  GraphSearch_apply_qr_rules --> AST_Connective
  GraphSearch_apply_qr_rules --> AST_Quantifier
  GraphSearch_apply_qr_rules --> DeductiveSystem_rule_QR2
  GraphSearch_apply_qr_rules --> SubstitutionManager_clone_ast
  GraphSearch_apply_qr_rules --> AST_Variable
  GraphSearch_apply_qr_rules --> DeductiveSystem_rule_QR1
  GraphSearch_forward_search --> GraphSearch_apply_qr_rules
  GraphSearch_forward_search --> Frontend_reconstruct_string
  GraphSearch_forward_search --> GraphSearch_generate_formulas
  GraphSearch_forward_search --> GraphSearch_check_axioms
  GraphSearch_forward_search --> GraphSearch_SearchLimits
  GraphSearch_forward_search --> GraphSearch_apply_modus_ponens
  GraphSearch_forward_search --> AST_is_structurally_equal
  GraphSearch_forward_search --> GraphSearch_extract_vocabulary
  GraphSearch_forward_search --> SubstitutionManager_clone_ast
  GraphSearch_forward_search --> main_print
  GraphSearch_forward_search --> GraphSearch_generate_terms
  GraphSearch_check_time --> GraphSearch_SearchLimitExceeded
  GraphSearch_check_space --> GraphSearch_SearchLimitExceeded
  ProofLogger_open --> main_print
  ProofLogger_log --> Frontend_reconstruct_string
  ProofLogger_log --> main_print
  extract_deps_get_local_imports --> ProofLogger_open
  extract_transformations_extract --> ProofLogger_open
  extract_transformations_extract --> extract_transformations_replace_continue
  extract_transformations_extract --> extract_transformations_clean_lines
  TruthEvaluator_is_tautology --> TruthEvaluator_get_prop_variables
  TruthEvaluator_is_tautology --> TruthEvaluator_evaluate_prop
  SequentEvaluator_prove_sequent --> AST_is_structurally_equal
  SequentEvaluator_is_tautology_sequent --> SequentEvaluator_prove_sequent
  AutoProver_collect_leaf_sequents --> AST_is_structurally_equal
  AutoProver_make_sequent_formula --> AST_Connective
  AutoProver_make_sequent_formula --> SubstitutionManager_clone_ast
  AutoProver_decode_propositional_to_fol --> AST_Connective
  AutoProver_decode_propositional_to_fol --> SubstitutionManager_clone_ast
  AutoProver_auto_prove --> SubstitutionManager_check_bound
  AutoProver_auto_prove --> DeductiveSystem_rule_QR1
  AutoProver_auto_prove --> Frontend_reconstruct_string
  AutoProver_auto_prove --> AutoProver_collect_leaf_sequents
  AutoProver_auto_prove --> AST_Connective
  AutoProver_auto_prove --> AutoProver_decode_propositional_to_fol
  AutoProver_auto_prove --> PropAbstraction_abstract_to_propositional_with_mapping
  AutoProver_auto_prove --> AST_is_structurally_equal
  AutoProver_auto_prove --> AutoProver_make_sequent_formula
  AutoProver_auto_prove --> SubstitutionManager_check_free
  AutoProver_auto_prove --> DeductiveSystem_rule_QR2
  AutoProver_auto_prove --> SubstitutionManager_clone_ast
  AutoProver_auto_prove --> main_print
  AutoProver_auto_prove --> DeductiveSystem_rule_PC2
  ProofGenerator_clause_to_string --> Frontend_reconstruct_string
  ProofGenerator_generate_proof --> ProofGenerator_dfs
  ProofGenerator_generate_proof --> BackwardSearch_clause_to_string
  Frontend_reconstruct_string --> Frontend_reconstruct_string_raw
  Frontend_reconstruct_string --> Frontend_colorize_formula
  Frontend_parse_term --> Frontend_Parser
  Frontend_parse_fol_formula --> Frontend_Parser
  Frontend_parse_prop_formula --> Frontend_Parser
  Frontend_show_environment --> Frontend__bold
  Frontend_show_environment --> Frontend_reconstruct_string
  Frontend_show_environment --> Frontend__yellow
  Frontend_show_environment --> Frontend__cyan
  Frontend_show_environment --> Frontend__green
  Frontend_show_environment --> main_print
  Frontend_parse --> Frontend_lex
  Frontend_parse --> Frontend_ParserError
  Frontend_consume_formatting --> AST_Whitespace
  Frontend_parse_expr --> AST_Function
  Frontend_parse_expr --> AST_Connective
  Frontend_parse_expr --> AST_Bracket
  Frontend_parse_expr --> AST_Relation
  Frontend_parse_expr --> Frontend_ParserError
  Frontend_parse_prefix --> Frontend_UnrecognizedSymbolError
  Frontend_parse_prefix --> AST_Function
  Frontend_parse_prefix --> AST_Connective
  Frontend_parse_prefix --> AST_DummyVariable
  Frontend_parse_prefix --> AST_Bracket
  Frontend_parse_prefix --> AST_PropositionalVariable
  Frontend_parse_prefix --> AST_SetBuilder
  Frontend_parse_prefix --> AST_Variable
  Frontend_parse_prefix --> Frontend_ParserError
  Frontend_parse_prefix --> AST_Relation
  Frontend_parse_quantifier --> AST_Bracket
  Frontend_parse_quantifier --> AST_Variable
  Frontend_parse_quantifier --> AST_Quantifier
  Frontend_parse_quantifier --> Frontend_ParserError
  StorageManager_save_environment_state --> ProofLogger_open
  StorageManager_save_environment_state --> Frontend_reconstruct_string
  StorageManager_save_environment_state --> StorageManager_get_env_chain
  StorageManager_load_environment_state --> ProofLogger_open
  StorageManager_load_environment_state --> AST_Function
  StorageManager_load_environment_state --> Frontend_parse_term
  StorageManager_load_environment_state --> AST_DummyVariable
  StorageManager_load_environment_state --> Frontend_parse_prop_formula
  StorageManager_load_environment_state --> Frontend_parse_fol_formula
  StorageManager_load_environment_state --> Environment_Environment
  StorageManager_load_environment_state --> Frontend_strip_ansi
  StorageManager_load_environment_state --> AST_PropositionalVariable
  StorageManager_load_environment_state --> AST_Variable
  StorageManager_load_environment_state --> AST_MetaVariable
  StorageManager_load_environment_state --> AST_Relation
  StorageManager_save_history --> ProofLogger_open
  StorageManager_load_history --> ProofLogger_open
  StorageManager_load_history --> Frontend_strip_ansi
  DefinitionExpander_substitute_dummy_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_substitute_dummy_in_formula --> SubstitutionManager_in_place_replace
  DefinitionExpander_substitute_dummy_in_formula --> DefinitionExpander_collect_and_map
  DefinitionExpander_get_internal_captures --> SubstitutionManager_collect_all_occurrences
  DefinitionExpander_get_internal_captures --> SubstitutionManager_get_term_vars
  DefinitionExpander_expand_user_defined_function_in_term --> DefinitionExpander_get_enclosing_bound_vars
  DefinitionExpander_expand_user_defined_function_in_term --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_user_defined_function_in_term --> SubstitutionManager_substitute_term
  DefinitionExpander_expand_user_defined_function_in_term --> DefinitionExpander_VariableCaptureError
  DefinitionExpander_expand_user_defined_function_in_term --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_user_defined_function_in_term --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_user_defined_function_in_term --> SubstitutionManager_get_term_vars
  DefinitionExpander_expand_user_defined_function_in_term --> DefinitionExpander_get_internal_captures
  DefinitionExpander_expand_user_defined_function_in_formula --> DefinitionExpander_get_enclosing_bound_vars
  DefinitionExpander_expand_user_defined_function_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_user_defined_function_in_formula --> SubstitutionManager_substitute_term
  DefinitionExpander_expand_user_defined_function_in_formula --> SubstitutionManager_get_free
  DefinitionExpander_expand_user_defined_function_in_formula --> DefinitionExpander_VariableCaptureError
  DefinitionExpander_expand_user_defined_function_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_user_defined_function_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_user_defined_function_in_formula --> DefinitionExpander_get_internal_captures
  DefinitionExpander_expand_user_defined_relation_in_formula --> DefinitionExpander_get_enclosing_bound_vars
  DefinitionExpander_expand_user_defined_relation_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_user_defined_relation_in_formula --> SubstitutionManager_get_free
  DefinitionExpander_expand_user_defined_relation_in_formula --> DefinitionExpander_substitute_dummy_in_formula
  DefinitionExpander_expand_user_defined_relation_in_formula --> DefinitionExpander_VariableCaptureError
  DefinitionExpander_expand_user_defined_relation_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_user_defined_relation_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_user_defined_relation_in_formula --> DefinitionExpander_get_internal_captures
  DefinitionExpander_expand_existential_in_formula --> AST_Connective
  DefinitionExpander_expand_existential_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_existential_in_formula --> AST_Quantifier
  DefinitionExpander_expand_existential_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_existential_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_unique_existential_in_formula --> SubstitutionManager_is_substitutable_free
  DefinitionExpander_expand_unique_existential_in_formula --> AST_Connective
  DefinitionExpander_expand_unique_existential_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_unique_existential_in_formula --> AST_Bracket
  DefinitionExpander_expand_unique_existential_in_formula --> SubstitutionManager_get_free
  DefinitionExpander_expand_unique_existential_in_formula --> SubstitutionManager_substitute_free
  DefinitionExpander_expand_unique_existential_in_formula --> AST_Variable
  DefinitionExpander_expand_unique_existential_in_formula --> AST_Quantifier
  DefinitionExpander_expand_unique_existential_in_formula --> AST_Whitespace
  DefinitionExpander_expand_unique_existential_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_unique_existential_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_unique_existential_in_formula --> AST_Relation
  DefinitionExpander_expand_epsilon_function_in_formula --> main_validate_new_name
  DefinitionExpander_expand_epsilon_function_in_formula --> SubstitutionManager_is_substitutable_free
  DefinitionExpander_expand_epsilon_function_in_formula --> AST_Connective
  DefinitionExpander_expand_epsilon_function_in_formula --> DefinitionExpander_get_enclosing_bound_vars
  DefinitionExpander_expand_epsilon_function_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_epsilon_function_in_formula --> AST_Bracket
  DefinitionExpander_expand_epsilon_function_in_formula --> SubstitutionManager_get_free
  DefinitionExpander_expand_epsilon_function_in_formula --> SubstitutionManager_substitute_free
  DefinitionExpander_expand_epsilon_function_in_formula --> DefinitionExpander_substitute_dummy_in_formula
  DefinitionExpander_expand_epsilon_function_in_formula --> AST_Variable
  DefinitionExpander_expand_epsilon_function_in_formula --> AST_Quantifier
  DefinitionExpander_expand_epsilon_function_in_formula --> AST_Whitespace
  DefinitionExpander_expand_epsilon_function_in_formula --> DefinitionExpander_VariableCaptureError
  DefinitionExpander_expand_epsilon_function_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_epsilon_function_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_epsilon_function_in_formula --> DefinitionExpander_get_internal_captures
  DefinitionExpander_expand_iota_function_in_formula --> main_validate_new_name
  DefinitionExpander_expand_iota_function_in_formula --> SubstitutionManager_is_substitutable_free
  DefinitionExpander_expand_iota_function_in_formula --> AST_Connective
  DefinitionExpander_expand_iota_function_in_formula --> DefinitionExpander_get_enclosing_bound_vars
  DefinitionExpander_expand_iota_function_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_iota_function_in_formula --> AST_Bracket
  DefinitionExpander_expand_iota_function_in_formula --> SubstitutionManager_get_free
  DefinitionExpander_expand_iota_function_in_formula --> SubstitutionManager_substitute_free
  DefinitionExpander_expand_iota_function_in_formula --> DefinitionExpander_substitute_dummy_in_formula
  DefinitionExpander_expand_iota_function_in_formula --> AST_Variable
  DefinitionExpander_expand_iota_function_in_formula --> DefinitionExpander_get_internal_captures
  DefinitionExpander_expand_iota_function_in_formula --> AST_Quantifier
  DefinitionExpander_expand_iota_function_in_formula --> AST_Whitespace
  DefinitionExpander_expand_iota_function_in_formula --> DefinitionExpander_VariableCaptureError
  DefinitionExpander_expand_iota_function_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_iota_function_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_iota_function_in_formula --> AST_Relation
  DefinitionExpander_expand_set_builder_in_formula --> main_validate_new_name
  DefinitionExpander_expand_set_builder_in_formula --> SubstitutionManager_is_substitutable_free
  DefinitionExpander_expand_set_builder_in_formula --> AST_Connective
  DefinitionExpander_expand_set_builder_in_formula --> DefinitionExpander_get_enclosing_bound_vars
  DefinitionExpander_expand_set_builder_in_formula --> DefinitionExpander_in_place_replace_node
  DefinitionExpander_expand_set_builder_in_formula --> AST_Bracket
  DefinitionExpander_expand_set_builder_in_formula --> SubstitutionManager_get_free
  DefinitionExpander_expand_set_builder_in_formula --> AST_Variable
  DefinitionExpander_expand_set_builder_in_formula --> AST_Quantifier
  DefinitionExpander_expand_set_builder_in_formula --> AST_Whitespace
  DefinitionExpander_expand_set_builder_in_formula --> SubstitutionManager_clone_ast
  DefinitionExpander_expand_set_builder_in_formula --> DefinitionExpander_collect_occurrences
  DefinitionExpander_expand_set_builder_in_formula --> AST_Relation
  DefinitionExpander_collect_and_map --> SubstitutionManager_clone_ast
  DeductiveSystem_axiom_E1 --> AST_is_structurally_equal
  DeductiveSystem_axiom_E2 --> AST_is_structurally_equal
  DeductiveSystem_axiom_E2 --> DeductiveSystem_get_conjuncts
  DeductiveSystem_axiom_E3 --> AST_is_structurally_equal
  DeductiveSystem_axiom_E3 --> DeductiveSystem_get_conjuncts
  DeductiveSystem_axiom_Q1 --> SubstitutionManager_is_substitutable_free
  DeductiveSystem_axiom_Q1 --> SubstitutionManager_find_substituted
  DeductiveSystem_axiom_Q2 --> SubstitutionManager_is_substitutable_free
  DeductiveSystem_axiom_Q2 --> SubstitutionManager_find_substituted
  DeductiveSystem_rule_QR1 --> AST_is_structurally_equal
  DeductiveSystem_rule_QR1 --> SubstitutionManager_check_bound
  DeductiveSystem_rule_QR1 --> SubstitutionManager_check_free
  DeductiveSystem_rule_QR2 --> AST_is_structurally_equal
  DeductiveSystem_rule_QR2 --> SubstitutionManager_check_bound
  DeductiveSystem_rule_QR2 --> SubstitutionManager_check_free
  DeductiveSystem_build_implication_formula --> AST_Connective
  DeductiveSystem_rule_PC1 --> TruthEvaluator_is_tautology
  DeductiveSystem_rule_PC1 --> PropAbstraction_abstract_to_propositional
  DeductiveSystem_rule_PC1 --> DeductiveSystem_build_implication_formula
  DeductiveSystem_rule_PC2 --> SequentEvaluator_is_tautology_sequent
  DeductiveSystem_rule_PC2 --> PropAbstraction_abstract_to_propositional
  DeductiveSystem_rule_PC2 --> DeductiveSystem_build_implication_formula
  app_get_dummy_env --> AST_Function
  app_get_dummy_env --> Environment_Environment
  app_get_dummy_env --> AST_PropositionalVariable
  app_get_dummy_env --> AST_Variable
  app_get_dummy_env --> AST_Relation
  app_print_header --> main_print
  app_main --> app_get_dummy_env
  app_main --> Frontend_reconstruct_string
  app_main --> Frontend_parse_term
  app_main --> AST_Function
  app_main --> AST_DummyVariable
  app_main --> Frontend_parse_prop_formula
  app_main --> Frontend_parse_fol_formula
  app_main --> AST_PropositionalVariable
  app_main --> AST_Variable
  app_main --> app_print_header
  app_main --> main_print
  app_main --> AST_Relation
  AST_TermNode --> AST_Node
  AST_FormulaNode --> AST_Node
  AST_Variable --> AST_TermNode
  AST_Function --> AST_TermNode
  AST_DummyVariable --> AST_TermNode
  AST_SetBuilder --> AST_TermNode
  AST_PropositionalVariable --> AST_FormulaNode
  AST_Relation --> AST_FormulaNode
  AST_Connective --> AST_FormulaNode
  AST_Quantifier --> AST_FormulaNode
  AST_MetaVariable --> AST_FormulaNode
  AST_Bracket --> AST_Node
  AST_Whitespace --> AST_Node
  main_get_default_env --> AST_Function
  main_get_default_env --> Environment_Environment
  main_get_default_env --> AST_PropositionalVariable
  main_get_default_env --> AST_Variable
  main_get_default_env --> AST_Relation
  main_validate_new_name --> main_print
  main_handle_variable_capture_interactive --> main_validate_new_name
  main_handle_variable_capture_interactive --> Frontend_reconstruct_string
  main_handle_variable_capture_interactive --> SubstitutionManager_substitute_bound
  main_handle_variable_capture_interactive --> SubstitutionManager_clone_ast
  main_handle_variable_capture_interactive --> AST_Variable
  main_handle_variable_capture_interactive --> main_print
  main_main --> SubstitutionManager_clone_ast
  main_main --> main_print
  main_main --> main_get_default_env
  test_capture_mock_mock_input --> main_print
  PropAbstraction_clone_ast_list --> SubstitutionManager_clone_ast
  PropAbstraction_collect_total_prefix --> PropAbstraction_clone_ast_list
  PropAbstraction_collect_total_postfix --> PropAbstraction_clone_ast_list
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_clear_right_postfix_formatting
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_get_or_create_prop_var
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_collect_total_prefix
  PropAbstraction_abstract_to_propositional_with_mapping --> AST_Connective
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_collect_total_postfix
  PropAbstraction_abstract_to_propositional_with_mapping --> AST_PropositionalVariable
  PropAbstraction_abstract_to_propositional_with_mapping --> AST_is_structurally_equal
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_clone_ast_list
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_recurse
  PropAbstraction_abstract_to_propositional_with_mapping --> SubstitutionManager_clone_ast
  PropAbstraction_abstract_to_propositional_with_mapping --> PropAbstraction_clear_left_prefix_formatting
  PropAbstraction_abstract_to_propositional --> PropAbstraction_abstract_to_propositional_with_mapping
  PropAbstraction_get_or_create_prop_var --> PropAbstraction_clear_right_postfix_formatting
  PropAbstraction_get_or_create_prop_var --> PropAbstraction_collect_total_prefix
  PropAbstraction_get_or_create_prop_var --> PropAbstraction_collect_total_postfix
  PropAbstraction_get_or_create_prop_var --> AST_PropositionalVariable
  PropAbstraction_get_or_create_prop_var --> AST_is_structurally_equal
  PropAbstraction_get_or_create_prop_var --> SubstitutionManager_clone_ast
  PropAbstraction_get_or_create_prop_var --> PropAbstraction_clear_left_prefix_formatting
  PropAbstraction_recurse --> AST_Connective
  PropAbstraction_recurse --> SubstitutionManager_clone_ast
  PropAbstraction_recurse --> PropAbstraction_get_or_create_prop_var
  PropAbstraction_recurse --> PropAbstraction_clone_ast_list
  SubstitutionManager_clone_ast --> AST_Function
  SubstitutionManager_clone_ast --> AST_Bracket
  SubstitutionManager_clone_ast --> AST_DummyVariable
  SubstitutionManager_clone_ast --> AST_Connective
  SubstitutionManager_clone_ast --> AST_PropositionalVariable
  SubstitutionManager_clone_ast --> AST_Quantifier
  SubstitutionManager_clone_ast --> AST_SetBuilder
  SubstitutionManager_clone_ast --> AST_MetaVariable
  SubstitutionManager_clone_ast --> AST_Whitespace
  SubstitutionManager_clone_ast --> AST_Variable
  SubstitutionManager_clone_ast --> AST_Relation
  SubstitutionManager_get_free --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_get_bound --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_check_free --> SubstitutionManager_get_free
  SubstitutionManager_check_bound --> SubstitutionManager_get_bound
  SubstitutionManager_is_substitutable_free --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_is_substitutable_free --> SubstitutionManager_get_term_vars
  SubstitutionManager_is_valid_renaming --> SubstitutionManager_get_free
  SubstitutionManager_is_valid_renaming --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_is_substitutable_bound --> SubstitutionManager_is_valid_renaming
  SubstitutionManager_is_substitutable_bound --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_substitute_free --> SubstitutionManager_in_place_replace
  SubstitutionManager_substitute_free --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_substitute_bound --> SubstitutionManager_in_place_replace
  SubstitutionManager_substitute_bound --> AST_Variable
  SubstitutionManager_substitute_bound --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_substitute_all --> SubstitutionManager_in_place_replace
  SubstitutionManager_substitute_all --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_substitute_term --> SubstitutionManager_in_place_replace
  SubstitutionManager_substitute_term --> SubstitutionManager_collect_term_vars_list
  SubstitutionManager_substitute_proposition --> SubstitutionManager_collect_prop_vars_list
  SubstitutionManager_substitute_proposition --> SubstitutionManager_in_place_replace
  SubstitutionManager_find_substituted --> AST_is_structurally_equal
  SubstitutionManager_find_substituted --> SubstitutionManager_match_nodes
  SubstitutionManager_find_substituted --> SubstitutionManager_clone_ast
  SubstitutionManager_find_substituted --> SubstitutionManager_collect_all_occurrences
  SubstitutionManager_replace_structurally --> AST_Function
  SubstitutionManager_replace_structurally --> AST_Bracket
  SubstitutionManager_replace_structurally --> AST_DummyVariable
  SubstitutionManager_replace_structurally --> AST_Connective
  SubstitutionManager_replace_structurally --> AST_PropositionalVariable
  SubstitutionManager_replace_structurally --> AST_Quantifier
  SubstitutionManager_replace_structurally --> AST_SetBuilder
  SubstitutionManager_replace_structurally --> AST_MetaVariable
  SubstitutionManager_replace_structurally --> AST_Whitespace
  SubstitutionManager_replace_structurally --> SubstitutionManager_clone_ast
  SubstitutionManager_replace_structurally --> AST_Variable
  SubstitutionManager_replace_structurally --> AST_Relation
  SubstitutionManager_remove_double_neg --> AST_Function
  SubstitutionManager_remove_double_neg --> AST_Bracket
  SubstitutionManager_remove_double_neg --> AST_DummyVariable
  SubstitutionManager_remove_double_neg --> AST_Connective
  SubstitutionManager_remove_double_neg --> SubstitutionManager__is_double_neg
  SubstitutionManager_remove_double_neg --> AST_PropositionalVariable
  SubstitutionManager_remove_double_neg --> AST_Quantifier
  SubstitutionManager_remove_double_neg --> AST_SetBuilder
  SubstitutionManager_remove_double_neg --> AST_MetaVariable
  SubstitutionManager_remove_double_neg --> AST_Whitespace
  SubstitutionManager_remove_double_neg --> SubstitutionManager_clone_ast
  SubstitutionManager_remove_double_neg --> AST_Variable
  SubstitutionManager_remove_double_neg --> AST_Relation
  SubstitutionManager_add_double_neg --> SubstitutionManager__rebuild_non_formula
  SubstitutionManager_add_double_neg --> AST_Connective
  SubstitutionManager_add_double_neg --> AST_SetBuilder
  SubstitutionManager_add_double_neg --> SubstitutionManager__rebuild_node
  SubstitutionManager_add_double_neg --> SubstitutionManager_clone_ast
  SubstitutionManager__rebuild_non_formula --> AST_Function
  SubstitutionManager__rebuild_non_formula --> AST_Bracket
  SubstitutionManager__rebuild_non_formula --> AST_DummyVariable
  SubstitutionManager__rebuild_non_formula --> AST_Whitespace
  SubstitutionManager__rebuild_non_formula --> SubstitutionManager_clone_ast
  SubstitutionManager__rebuild_non_formula --> AST_Variable
  SubstitutionManager__rebuild_node --> AST_Function
  SubstitutionManager__rebuild_node --> AST_Bracket
  SubstitutionManager__rebuild_node --> AST_DummyVariable
  SubstitutionManager__rebuild_node --> AST_Connective
  SubstitutionManager__rebuild_node --> AST_PropositionalVariable
  SubstitutionManager__rebuild_node --> AST_Quantifier
  SubstitutionManager__rebuild_node --> AST_SetBuilder
  SubstitutionManager__rebuild_node --> AST_MetaVariable
  SubstitutionManager__rebuild_node --> AST_Whitespace
  SubstitutionManager__rebuild_node --> SubstitutionManager_clone_ast
  SubstitutionManager__rebuild_node --> AST_Variable
  SubstitutionManager__rebuild_node --> AST_Relation
  SubstitutionManager_match_nodes --> AST_is_structurally_equal
  ZFC_Rules_are_isomorphic --> ZFC_Rules_match
  ZFC_Rules_get_parsing_env --> AST_Variable
  ZFC_Rules_get_parsing_env --> Environment_Environment
  ZFC_Rules_get_parsing_env --> AST_Relation
  ZFC_Rules_get_parsing_env --> AST_Function
  ZFC_Rules_axiom_extension --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_extension --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_pairing --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_pairing --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_union --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_union --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_power_set --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_power_set --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_regularity --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_regularity --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_infinity --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_infinity --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_choice --> ZFC_Rules_are_isomorphic
  ZFC_Rules_axiom_choice --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_specification --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_specification --> SubstitutionManager_get_free
  ZFC_Rules_axiom_replacement --> ZFC_Rules_strip_universal_quantifiers
  ZFC_Rules_axiom_replacement --> SubstitutionManager_get_free
  ZFC_Rules_axiom_replacement --> SubstitutionManager_substitute_free
  ZFC_Rules_axiom_replacement --> AST_is_structurally_equal
  ZFC_Rules_axiom_replacement --> SubstitutionManager_clone_ast
  ZFC_Rules_axiom_replacement --> AST_Variable
  verify_fold_capture_run_test --> verify_fold_capture_read_until
  verify_fold_capture_run_test --> main_print
  BackwardSearch_eliminate_implications --> AST_Connective
  BackwardSearch_eliminate_implications --> SubstitutionManager_clone_ast
  BackwardSearch_eliminate_implications --> AST_Quantifier
  BackwardSearch_to_nnf --> AST_Connective
  BackwardSearch_to_nnf --> SubstitutionManager_clone_ast
  BackwardSearch_to_nnf --> AST_Quantifier
  BackwardSearch_standardize_variables --> AST_Connective
  BackwardSearch_standardize_variables --> AST_Quantifier
  BackwardSearch_standardize_variables --> BackwardSearch__standardize_term
  BackwardSearch_standardize_variables --> SubstitutionManager_clone_ast
  BackwardSearch_standardize_variables --> AST_Variable
  BackwardSearch_standardize_variables --> AST_Relation
  BackwardSearch__standardize_term --> SubstitutionManager_clone_ast
  BackwardSearch__standardize_term --> AST_Variable
  BackwardSearch__standardize_term --> AST_Function
  BackwardSearch_skolemize --> SubstitutionManager_substitute_all
  BackwardSearch_skolemize --> AST_Function
  BackwardSearch_skolemize --> AST_Connective
  BackwardSearch_skolemize --> AST_Quantifier
  BackwardSearch_skolemize --> SubstitutionManager_clone_ast
  BackwardSearch_drop_universals --> AST_Connective
  BackwardSearch_drop_universals --> SubstitutionManager_clone_ast
  BackwardSearch_distribute_or_over_and --> AST_Connective
  BackwardSearch_distribute_or_over_and --> SubstitutionManager_clone_ast
  BackwardSearch_extract_clauses --> SubstitutionManager_clone_ast
  BackwardSearch_extract_clauses --> BackwardSearch_extract_literals
  BackwardSearch_process_to_cnf --> BackwardSearch_distribute_or_over_and
  BackwardSearch_process_to_cnf --> BackwardSearch_standardize_variables
  BackwardSearch_process_to_cnf --> BackwardSearch_extract_clauses
  BackwardSearch_process_to_cnf --> BackwardSearch_eliminate_implications
  BackwardSearch_process_to_cnf --> BackwardSearch_to_nnf
  BackwardSearch_process_to_cnf --> BackwardSearch_drop_universals
  BackwardSearch_process_to_cnf --> BackwardSearch_skolemize
  BackwardSearch_unify --> BackwardSearch_occurs_check
  BackwardSearch_unify --> SubstitutionManager_clone_ast
  BackwardSearch_apply_substitution --> AST_Connective
  BackwardSearch_apply_substitution --> SubstitutionManager_clone_ast
  BackwardSearch_apply_substitution --> AST_Relation
  BackwardSearch_apply_substitution --> AST_Function
  BackwardSearch_clause_to_string --> Frontend_reconstruct_string
  BackwardSearch_factorize --> AST_is_structurally_equal
  BackwardSearch_factorize --> SubstitutionManager_clone_ast
  BackwardSearch_are_variants --> BackwardSearch_unify
  BackwardSearch_are_variants --> BackwardSearch_try_unify_all
  BackwardSearch_resolve --> BackwardSearch_standardize_variables
  BackwardSearch_resolve --> BackwardSearch_get_literal_core
  BackwardSearch_resolve --> BackwardSearch_factorize
  BackwardSearch_resolve --> BackwardSearch_apply_substitution
  BackwardSearch_resolve --> BackwardSearch_unify
  BackwardSearch_backward_search --> BackwardSearch_finish_proof
  BackwardSearch_backward_search --> Frontend_reconstruct_string
  BackwardSearch_backward_search --> AST_Connective
  BackwardSearch_backward_search --> GraphSearch_SearchLimits
  BackwardSearch_backward_search --> ProofGenerator_ProofGenerator
  BackwardSearch_backward_search --> BackwardSearch_resolve
  BackwardSearch_backward_search --> BackwardSearch_process_to_cnf
  BackwardSearch_backward_search --> BackwardSearch_are_variants
  BackwardSearch_backward_search --> BackwardSearch_add_to_history
  BackwardSearch_backward_search --> SubstitutionManager_clone_ast
  BackwardSearch_backward_search --> main_print
  BackwardSearch_one_way_match --> AST_is_structurally_equal
  BackwardSearch_one_way_match --> SubstitutionManager_clone_ast
  BackwardSearch_subsumes --> BackwardSearch_one_way_match
  BackwardSearch_subsumes --> BackwardSearch_backtrack
  BackwardSearch_apply_substitution_at_path --> AST_Function
  BackwardSearch_apply_substitution_at_path --> AST_Connective
  BackwardSearch_apply_substitution_at_path --> BackwardSearch_apply_substitution
  BackwardSearch_apply_substitution_at_path --> SubstitutionManager_clone_ast
  BackwardSearch_apply_substitution_at_path --> AST_Relation
  BackwardSearch_get_var_counts --> BackwardSearch_visit
  BackwardSearch_is_term_greater --> BackwardSearch_get_var_counts
  BackwardSearch_is_term_greater --> BackwardSearch_term_weight
  BackwardSearch_paramodulate --> BackwardSearch_standardize_variables
  BackwardSearch_paramodulate --> BackwardSearch_is_term_greater
  BackwardSearch_paramodulate --> BackwardSearch_try_paramodulate
  BackwardSearch_paramodulate --> BackwardSearch_apply_substitution_at_path
  BackwardSearch_paramodulate --> BackwardSearch_factorize
  BackwardSearch_paramodulate --> BackwardSearch_apply_substitution
  BackwardSearch_paramodulate --> BackwardSearch_unify
  BackwardSearch_paramodulate --> BackwardSearch_get_subterms_with_paths
  BackwardSearch_advanced_search --> BackwardSearch_finish_proof
  BackwardSearch_advanced_search --> Frontend_reconstruct_string
  BackwardSearch_advanced_search --> AST_Connective
  BackwardSearch_advanced_search --> GraphSearch_SearchLimits
  BackwardSearch_advanced_search --> ProofGenerator_ProofGenerator
  BackwardSearch_advanced_search --> BackwardSearch_process_to_cnf
  BackwardSearch_advanced_search --> BackwardSearch_AdvancedSearchEngine
  BackwardSearch_advanced_search --> SubstitutionManager_clone_ast
  BackwardSearch_advanced_search --> main_print
  BackwardSearch_extract_literals --> SubstitutionManager_clone_ast
  BackwardSearch_try_unify_all --> BackwardSearch_unify
  BackwardSearch_finish_proof --> ProofGenerator_ProofGenerator
  BackwardSearch_finish_proof --> SubstitutionManager_clone_ast
  BackwardSearch_finish_proof --> main_print
  BackwardSearch_backtrack --> BackwardSearch_one_way_match
  BackwardSearch_try_paramodulate --> BackwardSearch_is_term_greater
  BackwardSearch_try_paramodulate --> BackwardSearch_apply_substitution_at_path
  BackwardSearch_try_paramodulate --> BackwardSearch_factorize
  BackwardSearch_try_paramodulate --> BackwardSearch_apply_substitution
  BackwardSearch_try_paramodulate --> BackwardSearch_unify
  BackwardSearch_try_paramodulate --> BackwardSearch_get_subterms_with_paths
  BackwardSearch_is_forward_subsumed --> BackwardSearch_subsumes
  BackwardSearch_backward_subsume --> BackwardSearch_subsumes
  BackwardSearch_add_clause --> BackwardSearch_are_variants
  BackwardSearch_add_clause --> BackwardSearch_clause_to_string
  BackwardSearch_solve --> BackwardSearch_paramodulate
  BackwardSearch_solve --> BackwardSearch_resolve
  classDef classNode fill:#f9f,stroke:#333,stroke-width:2px;
  classDef funcNode fill:#bbf,stroke:#333,stroke-width:1px;
```