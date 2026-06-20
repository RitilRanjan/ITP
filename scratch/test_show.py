import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from Frontend import show_environment
from Environment import Environment
from AST import Variable, PropositionalVariable

def test_show():
    # Ground Env
    ground = Environment()
    ground.add_variable(Variable("x"))
    ground.add_propositional_variable(PropositionalVariable("p"))
    
    from AST import Relation, RelationType, FormulaNode, Connective
    
    eq = Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[Variable("x"), Variable("x")])
    ground.formulae["eq_thm"] = eq
    ground.theorems["eq_thm"] = eq
    
    ground.formulae["unproven_rel"] = Relation(name="R", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[Variable("x")])
    
    # Prop formula
    ground.formulae["prop_form"] = Connective(name="¬", arity=1, arguments=[PropositionalVariable("p")])

    # Child Env
    child = Environment(parent=ground, goal_formula_name="unproven_rel")
    child.add_variable(Variable("y"))
    
    show_environment(child)

if __name__ == "__main__":
    test_show()
