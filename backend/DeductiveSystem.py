from typing import List, Dict, Set, Optional
from backend.AST import (
    Node, FormulaNode, Connective, Relation, Function, Variable,
    PropositionalVariable, Quantifier, is_structurally_equal, LongFormula
)
from backend.SubstitutionManager import is_substitutable_free, clone_ast, find_substituted
from backend.PropAbstraction import abstract_to_propositional
from backend.TruthEvaluator import is_tautology
from backend.SequentEvaluator import is_tautology_sequent

# ==========================================
# Helpers
# ==========================================

def get_conjuncts(node: FormulaNode) -> List[FormulaNode]:
    """Flattens a conjunction tree (left/right nested or flat) into a list of conjuncts."""
    if isinstance(node, Connective) and node.name == "∧":
        return get_conjuncts(node.arguments[0]) + get_conjuncts(node.arguments[1])
    return [node]

def check_equality(node: FormulaNode):
    """Returns (True, left, right) if node is an equality, else (False, None, None)."""
    if isinstance(node, Relation) and node.name == "=" and len(node.arguments) == 2:
        return True, node.arguments[0], node.arguments[1]
    if isinstance(node, LongFormula) and node.definition_name == "=":
        return True, node.term_placeholders.get("?t1"), node.term_placeholders.get("?t2")
    return False, None, None

# ==========================================
# Logical Axioms
# ==========================================

def axiom_E1(formula: FormulaNode) -> bool:
    """E1: reflexivity of equality. t = t for any term t."""
    is_eq, left, right = check_equality(formula)
    if not is_eq:
        return False
    return is_structurally_equal(left, right)

def axiom_E2(formula: FormulaNode) -> bool:
    """E2: variable replacement in function. (x1 = y1 ∧ ... ∧ xn = yn) ⇒ f(x1, ... xn) = f(y1, ... yn)."""
    if not isinstance(formula, Connective) or formula.name != "⇒" or len(formula.arguments) != 2:
        return False
    ant, cons = formula.arguments[0], formula.arguments[1]
    
    is_eq, f_left, f_right = check_equality(cons)
    if not is_eq:
        return False
    if not isinstance(f_left, Function) or not isinstance(f_right, Function):
        return False
    if f_left.name != f_right.name or len(f_left.arguments) != len(f_right.arguments):
        return False
        
    n = len(f_left.arguments)
    if n < 1:
        return False
        
    conjuncts = get_conjuncts(ant)
    if len(conjuncts) != n:
        return False
        
    for i in range(n):
        c = conjuncts[i]
        is_eq, c_left, c_right = check_equality(c)
        if not is_eq:
            return False
        if not is_structurally_equal(c_left, f_left.arguments[i]):
            return False
        if not is_structurally_equal(c_right, f_right.arguments[i]):
            return False
            
    return True

def axiom_E3(formula: FormulaNode) -> bool:
    """E3: variable replacement in relation. (x1 = y1 ∧ ... ∧ xn = yn) ⇒ (R(x1, ... xn) ⇒ R(y1, ... yn))."""
    if not isinstance(formula, Connective) or formula.name != "⇒" or len(formula.arguments) != 2:
        return False
    ant, cons = formula.arguments[0], formula.arguments[1]
    
    if not isinstance(cons, Connective) or cons.name != "⇒" or len(cons.arguments) != 2:
        return False
    r_left, r_right = cons.arguments[0], cons.arguments[1]
    if (not isinstance(r_left, Relation) and not isinstance(r_left, LongFormula)) or \
       (not isinstance(r_right, Relation) and not isinstance(r_right, LongFormula)):
        return False
    if isinstance(r_left, LongFormula):
        if r_left.definition_name != r_right.definition_name or len(r_left.term_placeholders) != len(r_right.term_placeholders):
            return False
        n = len(r_left.term_placeholders)
    else:
        if r_left.name != r_right.name or len(r_left.arguments) != len(r_right.arguments):
            return False
        n = len(r_left.arguments)
    if n < 1:
        return False
        
    conjuncts = get_conjuncts(ant)
    if len(conjuncts) != n:
        return False
        
    for i in range(n):
        c = conjuncts[i]
        is_eq, c_left, c_right = check_equality(c)
        if not is_eq:
            return False
        
        # r_left/r_right could be Relation or LongFormula. If they are LongFormula, 
        # their arguments are in term_placeholders. But wait, E3 specifically says R(x) => R(y).
        # We need to extract the arguments generically.
        if isinstance(r_left, LongFormula):
            l_args = list(r_left.term_placeholders.values())
            r_args = list(r_right.term_placeholders.values())
        else:
            l_args = r_left.arguments
            r_args = r_right.arguments

        if not is_structurally_equal(c_left, l_args[i]):
            return False
        if not is_structurally_equal(c_right, r_args[i]):
            return False
            
    return True

def axiom_Q1(formula: FormulaNode) -> bool:
    """Q1: Universal instantiation. ∀x φ ⇒ (x substituted for t in φ) if substitutable."""
    if not isinstance(formula, Connective) or formula.name != "⇒" or len(formula.arguments) != 2:
        return False
    ant, cons = formula.arguments[0], formula.arguments[1]
    
    if not isinstance(ant, Quantifier) or ant.name != "∀":
        return False
    x_name = ant.variable.name
    phi = ant.formula
    
    res_t = find_substituted(phi, cons, x_name)
    if res_t is None:
        return False
    if res_t is True:
        return True
        
    return is_substitutable_free(x_name, res_t, phi)

def axiom_Q2(formula: FormulaNode) -> bool:
    """Q2: Existential generalisation. (x substituted for t in φ) ⇒ ∃x φ if substitutable."""
    if not isinstance(formula, Connective) or formula.name != "⇒" or len(formula.arguments) != 2:
        return False
    ant, cons = formula.arguments[0], formula.arguments[1]
    
    if not isinstance(cons, Quantifier) or cons.name != "∃":
        return False
    x_name = cons.variable.name
    phi = cons.formula
    
    res_t = find_substituted(phi, ant, x_name)
    if res_t is None:
        return False
    if res_t is True:
        return True
        
    return is_substitutable_free(x_name, res_t, phi)

# ==========================================
# Inference Rules
# ==========================================

def rule_QR1(premises: List[FormulaNode], conclusion: FormulaNode) -> bool:
    """QR1: {ψ ⇒ φ} ⊢ ψ ⇒ (∀x φ) where x is not free in ψ and not bound in φ."""
    if not isinstance(conclusion, Connective) or conclusion.name != "⇒" or len(conclusion.arguments) != 2:
        return False
    psi, cons_right = conclusion.arguments[0], conclusion.arguments[1]
    
    if not isinstance(cons_right, Quantifier) or cons_right.name != "∀":
        return False
    x_name = cons_right.variable.name
    phi = cons_right.formula
    
    from backend.SubstitutionManager import check_free, check_bound
    found_premise = False
    for p in premises:
        if isinstance(p, Connective) and p.name == "⇒" and len(p.arguments) == 2:
            if is_structurally_equal(psi, p.arguments[0]) and is_structurally_equal(phi, p.arguments[1]):
                found_premise = True
                break
    if not found_premise:
        return False
        
    if check_free(psi, x_name):
        return False
    if check_bound(phi, x_name):
        return False
        
    return True

def rule_QR2(premises: List[FormulaNode], conclusion: FormulaNode) -> bool:
    """QR2: {φ ⇒ ψ} ⊢ (∃x φ) ⇒ ψ where x is not free in ψ and not bound in φ."""
    if not isinstance(conclusion, Connective) or conclusion.name != "⇒" or len(conclusion.arguments) != 2:
        return False
    cons_left, psi = conclusion.arguments[0], conclusion.arguments[1]
    
    if not isinstance(cons_left, Quantifier) or cons_left.name != "∃":
        return False
    x_name = cons_left.variable.name
    phi = cons_left.formula
    
    from backend.SubstitutionManager import check_free, check_bound
    found_premise = False
    for p in premises:
        if isinstance(p, Connective) and p.name == "⇒" and len(p.arguments) == 2:
            if is_structurally_equal(phi, p.arguments[0]) and is_structurally_equal(psi, p.arguments[1]):
                found_premise = True
                break
    if not found_premise:
        return False
        
    if check_free(psi, x_name):
        return False
    if check_bound(phi, x_name):
        return False
        
    return True

def build_implication_formula(premises: List[FormulaNode], conclusion: FormulaNode) -> FormulaNode:
    """Builds (P1 ∧ P2 ∧ ... ∧ Pk) ⇒ C from premises and conclusion."""
    if not premises:
        return conclusion
    curr = premises[0]
    for p in premises[1:]:
        curr = Connective(name="∧", arity=2, arguments=[curr, p])
    return Connective(name="⇒", arity=2, arguments=[curr, conclusion])

def rule_PC1(premises: List[FormulaNode], conclusion: FormulaNode) -> bool:
    """PC1: propositional calculus checker using truth table."""
    combined = build_implication_formula(premises, conclusion)
    prop_formula = abstract_to_propositional(combined)
    try:
        return is_tautology(prop_formula)
    except ValueError:
        return False

def rule_PC2(premises: List[FormulaNode], conclusion: FormulaNode) -> bool:
    """PC2: propositional calculus checker using sequent calculus."""
    combined = build_implication_formula(premises, conclusion)
    prop_formula = abstract_to_propositional(combined)
    return is_tautology_sequent(prop_formula)

def rule_PC3(premises: List[FormulaNode], conclusion: FormulaNode) -> bool:
    """PC3: PC2 but with recursive tautology checking for matching quantifiers."""
    from backend.PropAbstraction import abstract_formulas_modulo_pc3
    combined = build_implication_formula(premises, conclusion)
    prop_formulas = abstract_formulas_modulo_pc3([combined])
    prop_formula = prop_formulas[0]
    return is_tautology_sequent(prop_formula)
