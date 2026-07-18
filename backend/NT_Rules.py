from backend.AST import FormulaNode, TermNode, Connective, Quantifier, LongTerm, LongFormula, Constant, Variable, is_structurally_equal
from backend.SubstitutionManager import substitute_all
from copy import deepcopy

def is_S_injective(formula: FormulaNode) -> bool:
    # S x = S y ⇒ x = y
    if not isinstance(formula, Connective) or formula.name != "⇒": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongFormula) or lhs.definition_name != "=": return False
    if not isinstance(rhs, LongFormula) or rhs.definition_name != "=": return False
    
    l_arg1, l_arg2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]
    r_arg1, r_arg2 = rhs.term_placeholders["t1"], rhs.term_placeholders["t2"]
    
    if not isinstance(l_arg1, LongTerm) or l_arg1.definition_name != "S": return False
    if not isinstance(l_arg2, LongTerm) or l_arg2.definition_name != "S": return False
    
    if not isinstance(r_arg1, Variable) or not isinstance(r_arg2, Variable): return False
    
    return (l_arg1.term_placeholders["t1"].name == r_arg1.name and 
            l_arg2.term_placeholders["t1"].name == r_arg2.name)

def is_0_pred(formula: FormulaNode) -> bool:
    # ¬∃x S x = 0
    if not isinstance(formula, Connective) or formula.name != "¬": return False
    arg = formula.arguments[0]
    if not isinstance(arg, Quantifier) or arg.name != "∃": return False
    x = arg.variable
    body = arg.formula
    if not isinstance(body, LongFormula) or body.definition_name != "=": return False
    lhs, rhs = body.term_placeholders["t1"], body.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "S": return False
    if lhs.term_placeholders["t1"].name != x.name: return False
    if not isinstance(rhs, Constant) or rhs.name != "0": return False
    return True

def is_add_base(formula: FormulaNode) -> bool:
    # x + 0 = x (works for any term x)
    if not isinstance(formula, LongFormula) or formula.definition_name != "=": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "+": return False
    
    arg1, arg2 = lhs.arguments
    if not is_structurally_equal(arg1, rhs): return False
    if not isinstance(arg2, Constant) or arg2.name != "0": return False
    return True

def is_add_induction(formula: FormulaNode) -> bool:
    # x + S y = S(x + y) (works for any terms x, y)
    if not isinstance(formula, LongFormula) or formula.definition_name != "=": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "+": return False
    if not isinstance(rhs, LongTerm) or rhs.definition_name != "S": return False
    
    l_arg1, l_arg2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]
    if not isinstance(l_arg2, LongTerm) or l_arg2.definition_name != "S": return False
    y = l_arg2.term_placeholders["t1"]
    
    r_arg = rhs.term_placeholders["t1"]
    if not isinstance(r_arg, LongTerm) or r_arg.definition_name != "+": return False
    r1, r2 = r_arg.term_placeholders["t1"], r_arg.term_placeholders["t2"]
    if not is_structurally_equal(r1, l_arg1): return False
    if not is_structurally_equal(r2, y): return False
    return True

def is_multiply_base(formula: FormulaNode) -> bool:
    # x * 0 = 0 (works for any term x)
    if not isinstance(formula, LongFormula) or formula.definition_name != "=": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "*": return False
    if not isinstance(rhs, Constant) or rhs.name != "0": return False
    arg1, arg2 = lhs.arguments
    if not isinstance(arg2, Constant) or arg2.name != "0": return False
    return True

def is_multiply_induction(formula: FormulaNode) -> bool:
    # x * S y = x * y + x (works for any terms x, y)
    if not isinstance(formula, LongFormula) or formula.definition_name != "=": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "*": return False
    if not isinstance(rhs, LongTerm) or rhs.definition_name != "+": return False
    
    l1, l2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]
    if not isinstance(l2, LongTerm) or l2.definition_name != "S": return False
    y = l2.term_placeholders["t1"]
    
    r1, r2 = rhs.arguments
    if not isinstance(r1, LongTerm) or r1.definition_name != "*": return False
    if not is_structurally_equal(r2, l1): return False
    r1_1, r1_2 = r1.term_placeholders["t1"], r1.term_placeholders["t2"]
    if not is_structurally_equal(r1_1, l1): return False
    if not is_structurally_equal(r1_2, y): return False
    return True

def is_power_base(formula: FormulaNode) -> bool:
    # x ^ 0 = S 0 (works for any term x)
    if not isinstance(formula, LongFormula) or formula.definition_name != "=": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "^": return False
    if not isinstance(rhs, LongTerm) or rhs.definition_name != "S": return False
    
    l1, l2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]
    if not isinstance(l2, Constant) or l2.name != "0": return False
    
    r1 = rhs.term_placeholders["t1"]
    if not isinstance(r1, Constant) or r1.name != "0": return False
    return True

def is_power_induction(formula: FormulaNode) -> bool:
    # x ^ S y = x ^ y * x (works for any terms x, y)
    if not isinstance(formula, LongFormula) or formula.definition_name != "=": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    if not isinstance(lhs, LongTerm) or lhs.definition_name != "^": return False
    if not isinstance(rhs, Function) or rhs.name != "*": return False
    
    l1, l2 = lhs.term_placeholders["t1"], lhs.term_placeholders["t2"]
    if not isinstance(l2, LongTerm) or l2.definition_name != "S": return False
    y = l2.term_placeholders["t1"]
    
    r1, r2 = rhs.arguments
    if not isinstance(r1, LongTerm) or r1.definition_name != "^": return False
    if not is_structurally_equal(r2, l1): return False
    
    r1_1, r1_2 = r1.term_placeholders["t1"], r1.term_placeholders["t2"]
    if not is_structurally_equal(r1_1, l1): return False
    if not is_structurally_equal(r1_2, y): return False
    return True

def is_induction(formula: FormulaNode) -> bool:
    # (ψ(0) ∧ ∀x (ψ(x) ⇒ ψ(S x))) ⇒ ∀x ψ(x)
    if not isinstance(formula, Connective) or formula.name != "⇒": return False
    lhs, rhs = formula.term_placeholders["t1"], formula.term_placeholders["t2"]
    
    if not isinstance(lhs, Connective) or lhs.name != "∧": return False
    if not isinstance(rhs, Quantifier) or rhs.name != "∀": return False
    
    psi_0 = lhs.term_placeholders["t1"]
    inductive_step = lhs.arguments[1]
    
    if not isinstance(inductive_step, Quantifier) or inductive_step.name != "∀": return False
    if inductive_step.variable.name != rhs.variable.name: return False
    
    x_var = rhs.variable
    
    if not isinstance(inductive_step.formula, Connective) or inductive_step.formula.name != "⇒": return False
    
    psi_x_step = inductive_step.formula.arguments[0]
    psi_Sx_step = inductive_step.formula.arguments[1]
    
    psi_x_rhs = rhs.formula
    
    from backend.AST import is_structurally_equal
    if not is_structurally_equal(psi_x_step, psi_x_rhs): return False
    
    # Check psi(0)
    psi_0_expected = deepcopy(psi_x_rhs)
    substitute_all(psi_0_expected, x_var.name, Constant("0"), None)
    if not is_structurally_equal(psi_0, psi_0_expected): return False
    
    # Check psi(S x)
    psi_Sx_expected = deepcopy(psi_x_rhs)
    
    substitute_all(psi_Sx_expected, x_var.name, LongTerm(definition_name="S", term_placeholders={"t1": Variable(x_var.name)}, var_placeholders={}, formula_placeholders={}, repetition_counts={}), None)
    if not is_structurally_equal(psi_Sx_step, psi_Sx_expected): return False
    
    return True
