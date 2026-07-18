from typing import Optional, Union, List, Callable, Dict
from backend.AST import Node, LongTerm, LongFormula, TermPlaceholder, VariablePlaceholder, Quantifier, Iota, Epsilon, Connective, Relation, Function, Bracket, Whitespace, Variable, DummyVariable, PropositionalVariable, MetaVariable, Constant
from backend.SubstitutionManager import clone_ast, instantiate_long_definition, instantiate_macro_tokens, get_placeholders

class VariableCaptureError(Exception):
    def __init__(self, message: str, captured_vars: List[str], new_node: Node):
        super().__init__(message)
        self.captured_vars = captured_vars
        self.new_node = new_node

def replace_long_definition(
    node: Node,
    definition_name: str,
    def_ast: Node,
    occurrence_idx: Optional[Union[int, List[int]]],
    get_fresh_var_interactive: Callable[[str], Variable],
    get_fresh_term_interactive: Callable[[str], Node],
    env: 'Environment' = None,
    current_count: List[int] = None,
    enclosing_vars: set = None
) -> Node:
    if current_count is None:
        current_count = [0]
    if enclosing_vars is None:
        enclosing_vars = set()

    def _matches():
        if occurrence_idx is None: return True
        if isinstance(occurrence_idx, int): return current_count[0] == occurrence_idx
        return current_count[0] in occurrence_idx

    # If it's a LongTerm or LongFormula and matches name
    if isinstance(node, (LongTerm, LongFormula)) and node.definition_name == definition_name:
        current_count[0] += 1
        if _matches():
            term_args = dict(node.term_placeholders)
            var_args = dict(node.var_placeholders)
            formula_args = dict(node.formula_placeholders)
            
            long_def = env.long_terms[node.definition_name] if isinstance(node, LongTerm) else env.long_formulae[node.definition_name]
            def_tokens = long_def.definition_tokens
            
            instantiated = instantiate_macro_tokens(def_tokens, term_args, var_args, formula_args, node.repetition_counts, env, "term" if isinstance(node, LongTerm) else "fol")

            # Check variable capture!

            from backend.SubstitutionManager import compute_free_variables
            if env is not None:
                free_in_instantiated = compute_free_variables(instantiated, env)
            else:
                from backend.SubstitutionManager import get_free
                free_in_instantiated = get_free(instantiated)
                
            capture = free_in_instantiated.intersection(enclosing_vars)
            if capture:
                # We need to raise VariableCaptureError so handle_rw can resolve it
                raise VariableCaptureError("Variable capture detected.", list(capture), instantiated)
            
            # preserve formatting
            instantiated.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
            instantiated.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
            return instantiated

    # Otherwise recurse
    if isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable, Bracket, Whitespace, Constant, TermPlaceholder, VariablePlaceholder)):
        return clone_ast(node)
    
    if isinstance(node, (Function, Relation, Connective)):
        args = [replace_long_definition(arg, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for arg in node.arguments]
        if isinstance(node, Function):
            c = Function(name=node.name, arity=node.arity, func_type=node.func_type, arguments=args)
        elif isinstance(node, Relation):
            c = Relation(name=node.name, arity=node.arity, rel_type=node.rel_type, arguments=args)
        else:
            c = Connective(name=node.name, arity=node.arity, arguments=args)
        c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
        c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
        return c

    if isinstance(node, Quantifier):
        new_enclosing = enclosing_vars | {node.variable.name}
        c = Quantifier(
            name=node.name,
            variable=clone_ast(node.variable),
            formula=replace_long_definition(node.formula, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, new_enclosing)
        )
        c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
        c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
        return c

    if isinstance(node, (Iota, Epsilon)):
        new_enclosing = enclosing_vars | {node.variable.name}
        if isinstance(node, Iota):
            c = Iota(variable=clone_ast(node.variable), formula=replace_long_definition(node.formula, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, new_enclosing))
        else:
            c = Epsilon(variable=clone_ast(node.variable), formula=replace_long_definition(node.formula, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, new_enclosing))
        c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
        c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
        return c



    if isinstance(node, (LongTerm, LongFormula)):
        t_args = {k: [replace_long_definition(i, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for i in v] if isinstance(v, list) else replace_long_definition(v, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for k, v in node.term_placeholders.items()}
        v_args = {k: [replace_long_definition(i, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for i in v] if isinstance(v, list) else replace_long_definition(v, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for k, v in node.var_placeholders.items()}
        f_args = {k: [replace_long_definition(i, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for i in v] if isinstance(v, list) else replace_long_definition(v, definition_name, def_ast, occurrence_idx, get_fresh_var_interactive, get_fresh_term_interactive, env, current_count, enclosing_vars) for k, v in node.formula_placeholders.items()}
        
        if isinstance(node, LongTerm):
            c = LongTerm(definition_name=node.definition_name, term_placeholders=t_args, var_placeholders=v_args, formula_placeholders=f_args, repetition_counts=dict(node.repetition_counts), pattern=node.pattern)
        else:
            c = LongFormula(definition_name=node.definition_name, term_placeholders=t_args, var_placeholders=v_args, formula_placeholders=f_args, repetition_counts=dict(node.repetition_counts), pattern=node.pattern)
        c.prefix_formatting = [clone_ast(f) for f in node.prefix_formatting]
        c.postfix_formatting = [clone_ast(f) for f in node.postfix_formatting]
        return c

    raise ValueError(f"Unknown AST node type: {type(node)}")
