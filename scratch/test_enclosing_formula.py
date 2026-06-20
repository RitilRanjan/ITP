import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from AST import Relation, FormulaNode, TermNode, Quantifier, SetBuilder
from Frontend import parse_fol_formula, reconstruct_string

def find_smallest_enclosing_formula(root, target):
    def dfs(n):
        if n is target: return True
        
        # Traverse attributes that can hold AST nodes
        # arguments for Function/Relation
        if hasattr(n, "arguments"):
            for arg in n.arguments:
                res = dfs(arg)
                if res is True:
                    return n if isinstance(n, FormulaNode) else True
                if isinstance(res, FormulaNode): return res
                
        # formula for Quantifier/SetBuilder
        if hasattr(n, "formula"):
            res = dfs(n.formula)
            if res is True:
                return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
            
        # base_set for Quantifier/SetBuilder
        if hasattr(n, "base_set") and n.base_set is not None:
            res = dfs(n.base_set)
            if res is True:
                return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
            
        # children for Connective
        if hasattr(n, "children"):
            for c in n.children:
                res = dfs(c)
                if res is True:
                    return n if isinstance(n, FormulaNode) else True
                if isinstance(res, FormulaNode): return res
                
        # left/right for some nodes? (Connective uses children, but just in case)
        if hasattr(n, "left"):
            res = dfs(n.left)
            if res is True: return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
        if hasattr(n, "right"):
            res = dfs(n.right)
            if res is True: return n if isinstance(n, FormulaNode) else True
            if isinstance(res, FormulaNode): return res
            
        return False
        
    res = dfs(root)
    return res if isinstance(res, FormulaNode) else None

env = Environment()
from AST import Variable
env.add_variable(Variable("C"))
env.add_variable(Variable("A"))
env.add_variable(Variable("x"))
f1 = parse_fol_formula("∀C (¬¬ {x∈C | ¬ x∈x} ∈ C)", env)
from DefinitionExpander import collect_occurrences
occs = []
collect_occurrences(f1, SetBuilder, "{", occs)
target = occs[0]

enclosing = find_smallest_enclosing_formula(f1, target)
print("Formula 1:")
print("Target:", reconstruct_string(target))
print("Enclosing:", reconstruct_string(enclosing) if enclosing else "None")

f2 = parse_fol_formula("∀C ∈ {x∈A | ¬ x∈x} (C = C)", env)
occs = []
collect_occurrences(f2, SetBuilder, "{", occs)
target = occs[0]
enclosing = find_smallest_enclosing_formula(f2, target)
print("\nFormula 2:")
print("Target:", reconstruct_string(target))
print("Enclosing:", reconstruct_string(enclosing) if enclosing else "None")
