import pytest
from AST import Variable, PropositionalVariable, Function, FunctionType, Relation, RelationType
from Environment import Environment
from Frontend import parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string, UnrecognizedSymbolError, ParserError

def get_test_env():
    env = Environment()
    env.add_variable(Variable("x"))
    env.add_variable(Variable("y"))
    env.add_variable(Variable("z"))
    env.add_propositional_variable(PropositionalVariable("P"))
    env.add_propositional_variable(PropositionalVariable("Q"))
    
    dummy = Variable("x")
    env.add_term(Function("g", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_term(Function("+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_term(Function("f", arity=3, func_type=FunctionType.USER_DEFINED, arguments=[dummy, dummy, dummy]))
    
    env.add_formula(Relation("=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    return env

def test_parse_term():
    env = get_test_env()
    
    s1 = "x + y"
    ast1 = parse_term(s1, env)
    assert reconstruct_string(ast1) == s1
    
    s2 = "f x y z"
    ast2 = parse_term(s2, env)
    assert reconstruct_string(ast2) == s2
    
    s3 = "g ( x + y )"
    ast3 = parse_term(s3, env)
    assert reconstruct_string(ast3) == s3

def test_parse_prop_formula():
    env = get_test_env()
    
    s1 = "¬ P ∨ Q"
    ast1 = parse_prop_formula(s1, env)
    assert ast1.name == "∨"
    assert reconstruct_string(ast1) == s1
    
    s2 = "¬ ( P ∨ Q )"
    ast2 = parse_prop_formula(s2, env)
    assert ast2.name == "¬"
    assert reconstruct_string(ast2) == s2

def test_parse_fol_formula():
    env = get_test_env()
    
    s1 = "∀ x ( x = y ) ∧ ∀ z g z = x"
    ast1 = parse_fol_formula(s1, env)
    assert reconstruct_string(ast1) == s1
    
def test_errors():
    env = get_test_env()
    
    with pytest.raises(UnrecognizedSymbolError):
        parse_term("a + b", env)
        
    with pytest.raises(UnrecognizedSymbolError):
        parse_fol_formula("x = y ∧ P", env)
