import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from Frontend import Parser, lex
from Environment import Environment
from AST import Variable

def test_parser():
    env = Environment()
    env.add_variable(Variable("x"))
    env.add_variable(Variable("y"))
    env.add_variable(Variable("A"))
    env.add_variable(Variable("B"))
    
    # define relation P
    from AST import Relation, RelationType
    env.formulae["P"] = Relation(name="P", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[Variable("x")])
    # define binary function |
    from AST import Function, FunctionType
    env.terms["|"] = Function(name="|", arity=2, func_type=FunctionType.USER_DEFINED, arguments=[Variable("x"), Variable("x")])

    parser = Parser(env)
    
    test_strs = [
        "{ x ∈ y | P(x) }",
        "{ x ∈ y | x | y | P(x) }",
        "{ x ∈ y | y | x | y | x | P(x | y) }"
    ]
    for test_str in test_strs:
        try:
            node = parser.parse(test_str, "term")
            from Frontend import reconstruct_string
            print(f"Parsed successfully: {reconstruct_string(node)}")
            print(f"  base_set = {reconstruct_string(node.base_set)}")
            print(f"  formula = {reconstruct_string(node.formula)}")
        except Exception as e:
            print(f"Failed '{test_str}': {e}")

if __name__ == "__main__":
    test_parser()
