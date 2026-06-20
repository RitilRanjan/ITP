import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment
from AST import Quantifier, Variable, Connective, Relation
from Frontend import parse_fol_formula, reconstruct_string
env = Environment()
env.add_variable(Variable("C"))
env.add_variable(Variable("x"))
formula = parse_fol_formula("∀C (¬¬ {x∈C | ¬ x∈x} ∈ C)", env)
# find the set builder
from DefinitionExpander import collect_occurrences, SetBuilder, clone_ast, in_place_replace_node

occurrences = []
collect_occurrences(formula, SetBuilder, "{", occurrences)
target = occurrences[0]

def find_enclosing_relation(node, target):
    if node is target: return None
    if getattr(node, "arguments", None):
        for arg in node.arguments:
            if arg is target:
                return node if isinstance(node, Relation) else None
            res = find_enclosing_relation(arg, target)
            if res is not None:
                return node if isinstance(node, Relation) and res is True else res
    if getattr(node, "formula", None):
        res = find_enclosing_relation(node.formula, target)
        if res is not None: return res
    if getattr(node, "left", None):
        res = find_enclosing_relation(node.left, target)
        if res is not None: return res
        res = find_enclosing_relation(node.right, target)
        if res is not None: return res
    if getattr(node, "children", None):
        for c in node.children:
            res = find_enclosing_relation(c, target)
            if res is not None: return res
    return None

def find_parent_relation(root, target):
    def dfs(n):
        if n is target: return True
        if hasattr(n, "arguments"):
            for arg in n.arguments:
                res = dfs(arg)
                if res is True: return n if isinstance(n, Relation) else True
                if isinstance(res, Relation): return res
        if hasattr(n, "formula"):
            res = dfs(n.formula)
            if isinstance(res, Relation): return res
            # note: a relation doesn't have .formula
        if hasattr(n, "children"):
            for c in n.children:
                res = dfs(c)
                if isinstance(res, Relation): return res
        return False
    res = dfs(root)
    return res if isinstance(res, Relation) else None

rel = find_parent_relation(formula, target)
print("Enclosing relation:", reconstruct_string(rel) if rel else "None")
