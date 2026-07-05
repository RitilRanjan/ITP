from backend.DeductiveSystem import (
    axiom_E1, axiom_E2, axiom_E3, axiom_Q1, axiom_Q2,
    rule_QR1, rule_QR2, rule_PC1, rule_PC2, rule_PC3
)
from backend.ZFC_Rules import (
    axiom_extension, axiom_pairing, axiom_union, axiom_power_set,
    axiom_regularity, axiom_infinity, axiom_choice, axiom_specification,
    axiom_replacement
)
from backend.NT_Rules import (
    is_S_injective, is_0_pred, is_add_base, is_add_induction,
    is_multiply_base, is_multiply_induction, is_power_base,
    is_power_induction, is_induction
)

AXIOMS = {
    # Logical Axioms
    "E1": axiom_E1,
    "E2": axiom_E2,
    "E3": axiom_E3,
    "Q1": axiom_Q1,
    "Q2": axiom_Q2,
    # ZFC Axioms
    "extension": axiom_extension,
    "pairing": axiom_pairing,
    "union": axiom_union,
    "power_set": axiom_power_set,
    "regularity": axiom_regularity,
    "infinity": axiom_infinity,
    "choice": axiom_choice,
    "specification": axiom_specification,
    "replacement": axiom_replacement,
    
    # NT Axioms
    "S_injective": is_S_injective,
    "0_pred": is_0_pred,
    "add_base": is_add_base,
    "add_induction": is_add_induction,
    "multiply_base": is_multiply_base,
    "multiply_induction": is_multiply_induction,
    "power_base": is_power_base,
    "power_induction": is_power_induction,
    "induction": is_induction,
}
LOGICAL_AXIOMS = {"E1", "E2", "E3", "Q1", "Q2"}
THEORY_AXIOMS = {
    "ZFC": {
        "extension", "pairing", "union", "power_set",
        "regularity", "infinity", "choice", "specification",
        "replacement"
    },
    "NT": {
        "S_injective", "0_pred", "add_base", "add_induction",
        "multiply_base", "multiply_induction", "power_base",
        "power_induction", "induction"
    }
}

RULES = {
    "QR1": rule_QR1,
    "QR2": rule_QR2,
    "PC1": rule_PC1,
    "PC2": rule_PC2,
    "PC3": rule_PC3,
}
