import pytest
from AST import (
    Variable, Function, DummyVariable, FunctionType, RelationType,
    PropositionalVariable, Relation, Connective, Quantifier, MetaVariable,
    Bracket, Whitespace
)

def test_variable_creation():
    v = Variable(name="x")
    assert v.name == "x"

def test_function_creation_success():
    v1 = Variable(name="x")
    v2 = Variable(name="y")
    f = Function(name="f", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[v1, v2])
    assert f.name == "f"
    assert f.arity == 2
    assert f.func_type == FunctionType.PRE_DEFINED
    assert len(f.arguments) == 2

def test_function_creation_failure():
    v1 = Variable(name="x")
    with pytest.raises(ValueError):
        # Arity is 2 but only 1 argument provided
        Function(name="f", arity=2, arguments=[v1])

def test_dummy_variable():
    dv = DummyVariable(name="_placeholder1")
    assert dv.name == "_placeholder1"

def test_relation_creation():
    v = Variable(name="x")
    r = Relation(name="P", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[v])
    assert r.name == "P"
    assert r.rel_type == RelationType.USER_DEFINED

def test_relation_failure():
    with pytest.raises(ValueError):
        Relation(name="Q", arity=2, arguments=[])

def test_connective_creation():
    p = PropositionalVariable(name="P")
    q = PropositionalVariable(name="Q")
    and_conn = Connective(name="∧", arity=2, arguments=[p, q])
    assert and_conn.name == "∧"

def test_quantifier_creation():
    v = Variable(name="x")
    r = Relation(name="P", arity=1, arguments=[v])
    forall = Quantifier(name="∀", variable=v, formula=r)
    assert forall.name == "∀"
    assert forall.variable.name == "x"

def test_formatting_nodes():
    lparen = Bracket(name="(")
    ws = Whitespace(name=" ")
    assert lparen.name == "("
    assert ws.name == " "
