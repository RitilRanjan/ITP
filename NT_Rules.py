from AST import FormulaNode, TermNode, Connective, Relation, Quantifier, Function, Constant, Variable
from SubstitutionManager import substitute_bound
from copy import deepcopy

def is_S_injective(formula: FormulaNode) -> bool:
    # S x = S y ⇒ x = y
    if not isinstance(formula, Connective) or formula.name != "⇒": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Relation) or lhs.name != "=": return False
    if not isinstance(rhs, Relation) or rhs.name != "=": return False
    
    l_arg1, l_arg2 = lhs.arguments
    r_arg1, r_arg2 = rhs.arguments
    
    if not isinstance(l_arg1, Function) or l_arg1.name != "S": return False
    if not isinstance(l_arg2, Function) or l_arg2.name != "S": return False
    
    if not isinstance(r_arg1, Variable) or not isinstance(r_arg2, Variable): return False
    
    return (l_arg1.arguments[0].name == r_arg1.name and 
            l_arg2.arguments[0].name == r_arg2.name)

def is_0_pred(formula: FormulaNode) -> bool:
    # ¬∃x S x = 0
    if not isinstance(formula, Connective) or formula.name != "¬": return False
    arg = formula.arguments[0]
    if not isinstance(arg, Quantifier) or arg.name != "∃": return False
    x = arg.variable
    body = arg.formula
    if not isinstance(body, Relation) or body.name != "=": return False
    lhs, rhs = body.arguments
    if not isinstance(lhs, Function) or lhs.name != "S": return False
    if lhs.arguments[0].name != x.name: return False
    if not isinstance(rhs, Constant) or rhs.name != "0": return False
    return True

def is_add_base(formula: FormulaNode) -> bool:
    # x + 0 = x
    if not isinstance(formula, Relation) or formula.name != "=": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Function) or lhs.name != "+": return False
    if not isinstance(rhs, Variable): return False
    arg1, arg2 = lhs.arguments
    if not isinstance(arg1, Variable) or arg1.name != rhs.name: return False
    if not isinstance(arg2, Constant) or arg2.name != "0": return False
    return True

def is_add_induction(formula: FormulaNode) -> bool:
    # x + S y = S(x + y)
    if not isinstance(formula, Relation) or formula.name != "=": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Function) or lhs.name != "+": return False
    if not isinstance(rhs, Function) or rhs.name != "S": return False
    
    l_arg1, l_arg2 = lhs.arguments
    if not isinstance(l_arg1, Variable): return False
    if not isinstance(l_arg2, Function) or l_arg2.name != "S": return False
    y = l_arg2.arguments[0]
    if not isinstance(y, Variable): return False
    
    r_arg = rhs.arguments[0]
    if not isinstance(r_arg, Function) or r_arg.name != "+": return False
    r1, r2 = r_arg.arguments
    if not isinstance(r1, Variable) or r1.name != l_arg1.name: return False
    if not isinstance(r2, Variable) or r2.name != y.name: return False
    return True

def is_multiply_base(formula: FormulaNode) -> bool:
    # x * 0 = 0
    if not isinstance(formula, Relation) or formula.name != "=": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Function) or lhs.name != "*": return False
    if not isinstance(rhs, Constant) or rhs.name != "0": return False
    arg1, arg2 = lhs.arguments
    if not isinstance(arg1, Variable): return False
    if not isinstance(arg2, Constant) or arg2.name != "0": return False
    return True

def is_multiply_induction(formula: FormulaNode) -> bool:
    # x * S y = x * y + x
    if not isinstance(formula, Relation) or formula.name != "=": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Function) or lhs.name != "*": return False
    if not isinstance(rhs, Function) or rhs.name != "+": return False
    
    l1, l2 = lhs.arguments
    if not isinstance(l1, Variable): return False
    if not isinstance(l2, Function) or l2.name != "S": return False
    y = l2.arguments[0]
    if not isinstance(y, Variable): return False
    
    r1, r2 = rhs.arguments
    if not isinstance(r1, Function) or r1.name != "*": return False
    if not isinstance(r2, Variable) or r2.name != l1.name: return False
    r1_1, r1_2 = r1.arguments
    if not isinstance(r1_1, Variable) or r1_1.name != l1.name: return False
    if not isinstance(r1_2, Variable) or r1_2.name != y.name: return False
    return True

def is_power_base(formula: FormulaNode) -> bool:
    # x ^ 0 = S 0
    if not isinstance(formula, Relation) or formula.name != "=": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Function) or lhs.name != "^": return False
    if not isinstance(rhs, Function) or rhs.name != "S": return False
    
    l1, l2 = lhs.arguments
    if not isinstance(l1, Variable): return False
    if not isinstance(l2, Constant) or l2.name != "0": return False
    
    r1 = rhs.arguments[0]
    if not isinstance(r1, Constant) or r1.name != "0": return False
    return True

def is_power_induction(formula: FormulaNode) -> bool:
    # x ^ S y = x ^ y * x
    if not isinstance(formula, Relation) or formula.name != "=": return False
    lhs, rhs = formula.arguments
    if not isinstance(lhs, Function) or lhs.name != "^": return False
    if not isinstance(rhs, Function) or rhs.name != "*": return False
    
    l1, l2 = lhs.arguments
    if not isinstance(l1, Variable): return False
    if not isinstance(l2, Function) or l2.name != "S": return False
    y = l2.arguments[0]
    if not isinstance(y, Variable): return False
    
    r1, r2 = rhs.arguments
    if not isinstance(r1, Function) or r1.name != "^": return False
    if not isinstance(r2, Variable) or r2.name != l1.name: return False
    
    r1_1, r1_2 = r1.arguments
    if not isinstance(r1_1, Variable) or r1_1.name != l1.name: return False
    if not isinstance(r1_2, Variable) or r1_2.name != y.name: return False
    return True

def is_induction(formula: FormulaNode) -> bool:
    # (ψ(0) ∧ ∀x (ψ(x) ⇒ ψ(S x))) ⇒ ∀x ψ(x)
    if not isinstance(formula, Connective) or formula.name != "⇒": return False
    lhs, rhs = formula.arguments
    
    if not isinstance(lhs, Connective) or lhs.name != "∧": return False
    if not isinstance(rhs, Quantifier) or rhs.name != "∀": return False
    
    psi_0 = lhs.arguments[0]
    inductive_step = lhs.arguments[1]
    
    if not isinstance(inductive_step, Quantifier) or inductive_step.name != "∀": return False
    if inductive_step.variable.name != rhs.variable.name: return False
    
    x_var = rhs.variable
    
    if not isinstance(inductive_step.formula, Connective) or inductive_step.formula.name != "⇒": return False
    
    psi_x_step = inductive_step.formula.arguments[0]
    psi_Sx_step = inductive_step.formula.arguments[1]
    
    psi_x_rhs = rhs.formula
    
    from AST import is_structurally_equal
    if not is_structurally_equal(psi_x_step, psi_x_rhs): return False
    
    # Check psi(0)
    psi_0_expected = deepcopy(psi_x_rhs)
    substitute_bound(psi_0_expected, x_var.name, Constant("0"), None)
    if not is_structurally_equal(psi_0, psi_0_expected): return False
    
    # Check psi(S x)
    psi_Sx_expected = deepcopy(psi_x_rhs)
    from AST import FunctionType
    substitute_bound(psi_Sx_expected, x_var.name, Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[Variable(x_var.name)]), None)
    if not is_structurally_equal(psi_Sx_step, psi_Sx_expected): return False
    
    return True
