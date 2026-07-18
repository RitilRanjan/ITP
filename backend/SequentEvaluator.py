from typing import List
from backend.AST import FormulaNode, Connective, PropositionalVariable, is_structurally_equal

def prove_sequent(left: List[FormulaNode], right: List[FormulaNode]) -> bool:
    """
    Recursively checks the validity of a propositional sequent Left |- Right using Gentzen's G3cp calculus.
    """
    # 1. Check Identity Axiom: if any formula appears on both sides (ignoring formatting)
    if any(is_structurally_equal(l, r) for l in left for r in right):
        return True

    # 1.5. Check Logical Constant Axioms (⊤ and ⊥)
    if any(isinstance(l, Connective) and l.name == "⊥" for l in left):
        return True
    if any(isinstance(r, Connective) and r.name == "⊤" for r in right):
        return True

    # 2. Find a non-atomic formula to decompose in left
    for idx, f in enumerate(left):
        if isinstance(f, Connective):
            left_without_f = left[:idx] + left[idx+1:]
            if f.name == "¬":
                return prove_sequent(left_without_f, right + [f.arguments[0]])
            elif f.name == "∧":
                return prove_sequent(left_without_f + [f.arguments[0], f.arguments[1]], right)
            elif f.name == "∨":
                return (prove_sequent(left_without_f + [f.arguments[0]], right) and
                        prove_sequent(left_without_f + [f.arguments[1]], right))
            elif f.name == "⇒":
                return (prove_sequent(left_without_f, right + [f.arguments[0]]) and
                        prove_sequent(left_without_f + [f.arguments[1]], right))
            elif f.name == "⇔":
                return (prove_sequent(left_without_f + [f.arguments[0], f.arguments[1]], right) and
                        prove_sequent(left_without_f, right + [f.arguments[0], f.arguments[1]]))

    # 3. Find a non-atomic formula to decompose in right
    for idx, f in enumerate(right):
        if isinstance(f, Connective):
            right_without_f = right[:idx] + right[idx+1:]
            if f.name == "¬":
                return prove_sequent(left + [f.arguments[0]], right_without_f)
            elif f.name == "∧":
                return (prove_sequent(left, right_without_f + [f.arguments[0]]) and
                        prove_sequent(left, right_without_f + [f.arguments[1]]))
            elif f.name == "∨":
                return prove_sequent(left, right_without_f + [f.arguments[0], f.arguments[1]])
            elif f.name == "⇒":
                return prove_sequent(left + [f.arguments[0]], right_without_f + [f.arguments[1]])
            elif f.name == "⇔":
                return (prove_sequent(left + [f.arguments[0]], right_without_f + [f.arguments[1]]) and
                        prove_sequent(left + [f.arguments[1]], right_without_f + [f.arguments[0]]))

    # 4. If all formulas are atomic and no identity axiom is met, the sequent is invalid.
    return False

def is_tautology_sequent(formula: FormulaNode) -> bool:
    """
    Returns True iff the given propositional formula is a tautology using Sequent Calculus.
    """
    return prove_sequent([], [formula])
