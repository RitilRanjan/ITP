from backend.AST import Variable, DummyVariable, Function, FunctionType, Relation, RelationType, Quantifier
from backend.Environment import Environment
from backend.Parser import parse_term, parse_fol_formula, reconstruct_string, lex
from backend.SubstitutionManager import clone_ast, substitute_term, substitute_free

def get_test_env():
    env = Environment()
    env.add_variable(Variable("x"))
    env.add_variable(Variable("y"))
    env.add_variable(Variable("z"))
    
    dummy = Variable("x")
    env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

def test_inline_def_f_prefix():
    env = get_test_env()
    # Let's define: def_f 1 F x S x + y
    args_str = "1 F x S x + y"
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    arity = int(cmd_args[0])
    assert arity == 1
    f_name = cmd_args[1]
    variables = cmd_args[2 : arity + 2]
    tail_tokens = cmd_args[arity + 2 :]
    
    assert f_name == "F"
    assert variables == ["x"]
    assert tail_tokens == ["S", "x", "+", "y"]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.terms:
        definition = clone_ast(env.terms[tail_tokens[0]])
    else:
        t1_expr = " ".join(tail_tokens)
        definition = parse_term(t1_expr, env)
        
    for i, var_name in enumerate(variables):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_term(definition, var_name, dummy_var)
        
    assert reconstruct_string(definition).replace(" ", "") == "S_1+y"

def test_inline_def_f_infix():
    env = get_test_env()
    # def_f 2 x F y x + y + z
    args_str = "2 x F y x + y + z"
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    arity = int(cmd_args[0])
    assert arity == 2
    v1_name, f_name, v2_name = cmd_args[1], cmd_args[2], cmd_args[3]
    variables = [v1_name, v2_name]
    tail_tokens = cmd_args[4:]
    
    assert f_name == "F"
    assert variables == ["x", "y"]
    assert tail_tokens == ["x", "+", "y", "+", "z"]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.terms:
        definition = clone_ast(env.terms[tail_tokens[0]])
    else:
        t1_expr = " ".join(tail_tokens)
        definition = parse_term(t1_expr, env)
        
    for i, var_name in enumerate(variables):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_term(definition, var_name, dummy_var)
        
    assert reconstruct_string(definition).replace(" ", "") == "_1+_2+z"

def test_inline_def_r_prefix():
    env = get_test_env()
    # def_r 1 R x x = y ∧ y = z
    args_str = "1 R x x = y ∧ y = z"
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    arity = int(cmd_args[0])
    f_name = cmd_args[1]
    variables = cmd_args[2 : arity + 2]
    tail_tokens = cmd_args[arity + 2 :]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.formulae:
        definition = clone_ast(env.formulae[tail_tokens[0]])
    else:
        f1_expr = " ".join(tail_tokens)
        definition = parse_fol_formula(f1_expr, env)
        
    for i, var_name in enumerate(variables):
        dummy_name = f"_{i+1}"
        dummy_var = DummyVariable(name=dummy_name)
        env.add_dummy_variable(dummy_var)
        definition = substitute_free(definition, var_name, dummy_var)
        
    assert reconstruct_string(definition).replace(" ", "") == "_1=y∧y=z"

def test_inline_iota():
    env = get_test_env()
    # Set up a proven theorem
    th_ast = parse_fol_formula("∃! x ( x = y )", env)
    env.theorems["th1"] = th_ast
    
    # Try inline match
    args_str = "F ∃! x ( x = y )"
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    f_name = cmd_args[0]
    tail_tokens = cmd_args[1:]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.theorems:
        theorem_node = env.theorems[tail_tokens[0]]
    else:
        f1_expr = " ".join(tail_tokens)
        target_formula = parse_fol_formula(f1_expr, env)
        theorem_node = None
        for th in env.theorems.values():
            if target_formula.is_structurally_equal(th):
                theorem_node = th
                break
                
    assert theorem_node is not None
    assert reconstruct_string(theorem_node).replace(" ", "") == "∃!x(x=y)"

def test_inline_epsilon():
    env = get_test_env()
    # Set up a proven theorem
    th_ast = parse_fol_formula("∃ x ( x = y )", env)
    env.theorems["th1"] = th_ast
    
    # Try inline match
    args_str = "E ∃ x ( x = y )"
    cmd_args = [t for t in lex(args_str) if not t.isspace()]
    f_name = cmd_args[0]
    tail_tokens = cmd_args[1:]
    
    if len(tail_tokens) == 1 and tail_tokens[0] in env.theorems:
        theorem_node = env.theorems[tail_tokens[0]]
    else:
        f1_expr = " ".join(tail_tokens)
        target_formula = parse_fol_formula(f1_expr, env)
        theorem_node = None
        for th in env.theorems.values():
            if target_formula.is_structurally_equal(th):
                theorem_node = th
                break
                
    assert theorem_node is not None
    assert reconstruct_string(theorem_node).replace(" ", "") == "∃x(x=y)"
