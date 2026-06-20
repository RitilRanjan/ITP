import sys
import os

from main import get_default_env
from AST import Variable, Function, FunctionType, Relation, RelationType, Connective, Quantifier
from BackwardSearch import backward_search, advanced_search

def main():
    env = get_default_env()
    
    # 1. Define variables
    x = Variable("x")
    env.add_variable(x)
    
    # Socrates (constant - arity 0 function)
    soc = Function(name="Socrates", arity=0, func_type=FunctionType.USER_DEFINED, arguments=[])
    env.add_term(soc)
    
    # Man(x) and Mortal(x) relations
    Man_x = Relation(name="Man", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[x])
    Mortal_x = Relation(name="Mortal", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[x])
    
    # ∀x (Man(x) ⇒ Mortal(x))
    imp = Connective("⇒", 2, [Man_x, Mortal_x])
    forall = Quantifier("∀", x, imp)
    env.theorems["AllMenMortal"] = forall
    
    # Man(Socrates)
    Man_soc = Relation(name="Man", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[soc])
    env.theorems["SocratesIsMan"] = Man_soc
    
    # Goal: Mortal(Socrates)
    Mortal_soc = Relation(name="Mortal", arity=1, rel_type=RelationType.USER_DEFINED, arguments=[soc])
    env.formulae["SocratesIsMortal"] = Mortal_soc
    
    print("=== Testing Base Backward Search ===")
    backward_search(env, "SocratesIsMortal", time_limit=5.0, space_limit=1000, generate_proof=True)
    
    print("\n\n=== Testing Advanced Search (with Paramodulation and SOS) ===")
    env.theorems.pop("SocratesIsMortal", None) # remove from proven
    flags = {"sos": True, "unit": False, "subsumption": True, "paramodulation": True, "ordering": False}
    advanced_search(env, "SocratesIsMortal", time_limit=5.0, space_limit=1000, flags=flags, generate_proof=True)

if __name__ == "__main__":
    main()
