from typing import List, Tuple, Dict, Set, Optional
from AST import (
    Node, FormulaNode, Connective, Relation, Function, Variable,
    PropositionalVariable, Quantifier, is_structurally_equal
)
from SubstitutionManager import is_substitutable_free, clone_ast, check_free, check_bound
from PropAbstraction import abstract_to_propositional_with_mapping
from SequentEvaluator import is_tautology_sequent
from DeductiveSystem import (
    axiom_E1, axiom_E2, axiom_E3, axiom_Q1, axiom_Q2,
    rule_QR1, rule_QR2, rule_PC2
)
from ZFC_Rules import (
    axiom_extension, axiom_pairing, axiom_union, axiom_power_set,
    axiom_regularity, axiom_infinity, axiom_choice, axiom_specification,
    axiom_replacement
)
from Environment import Environment
from Frontend import reconstruct_string

AXIOMS = {
    "E1": axiom_E1,
    "E2": axiom_E2,
    "E3": axiom_E3,
    "Q1": axiom_Q1,
    "Q2": axiom_Q2,
    "extension": axiom_extension,
    "pairing": axiom_pairing,
    "union": axiom_union,
    "power_set": axiom_power_set,
    "regularity": axiom_regularity,
    "infinity": axiom_infinity,
    "choice": axiom_choice,
    "specification": axiom_specification,
    "replacement": axiom_replacement,
}

def collect_leaf_sequents(left: List[FormulaNode], right: List[FormulaNode]) -> List[Tuple[List[FormulaNode], List[FormulaNode]]]:
    """
    Recursively decomposes the sequent Left |- Right using Gentzen's G3cp rules,
    and returns a list of all leaf sequents (which contain only atomic propositional variables)
    that are NOT valid by the identity axiom.
    """
    # 1. Check Identity Axiom: if any formula appears on both sides, this branch is proven
    if any(is_structurally_equal(l, r) for l in left for r in right):
        return []

    # 2. Find a non-atomic formula to decompose in left
    for idx, f in enumerate(left):
        if isinstance(f, Connective):
            left_without_f = left[:idx] + left[idx+1:]
            if f.name == "¬":
                return collect_leaf_sequents(left_without_f, right + [f.arguments[0]])
            elif f.name == "∧":
                return collect_leaf_sequents(left_without_f + [f.arguments[0], f.arguments[1]], right)
            elif f.name == "∨":
                return (collect_leaf_sequents(left_without_f + [f.arguments[0]], right) +
                        collect_leaf_sequents(left_without_f + [f.arguments[1]], right))
            elif f.name == "⇒":
                return (collect_leaf_sequents(left_without_f, right + [f.arguments[0]]) +
                        collect_leaf_sequents(left_without_f + [f.arguments[1]], right))
            elif f.name == "⇔":
                return (collect_leaf_sequents(left_without_f + [f.arguments[0], f.arguments[1]], right) +
                        collect_leaf_sequents(left_without_f, right + [f.arguments[0], f.arguments[1]]))

    # 3. Find a non-atomic formula to decompose in right
    for idx, f in enumerate(right):
        if isinstance(f, Connective):
            right_without_f = right[:idx] + right[idx+1:]
            if f.name == "¬":
                return collect_leaf_sequents(left + [f.arguments[0]], right_without_f)
            elif f.name == "∧":
                return (collect_leaf_sequents(left, right_without_f + [f.arguments[0]]) +
                        collect_leaf_sequents(left, right_without_f + [f.arguments[1]]))
            elif f.name == "∨":
                return collect_leaf_sequents(left, right_without_f + [f.arguments[0], f.arguments[1]])
            elif f.name == "⇒":
                return collect_leaf_sequents(left + [f.arguments[0]], right_without_f + [f.arguments[1]])
            elif f.name == "⇔":
                return (collect_leaf_sequents(left + [f.arguments[0]], right_without_f + [f.arguments[1]]) +
                        collect_leaf_sequents(left + [f.arguments[1]], right_without_f + [f.arguments[0]]))

    # 4. If all formulas are atomic and no identity axiom is met, this is an unproven leaf sequent.
    return [(left, right)]

def make_sequent_formula(left: List[FormulaNode], right: List[FormulaNode]) -> FormulaNode:
    """Converts a leaf sequent (Left |- Right) to its equivalent propositional formula representation."""
    if not left:
        if len(right) == 1:
            return clone_ast(right[0])
        curr = right[0]
        for r in right[1:]:
            curr = Connective(name="∨", arity=2, arguments=[curr, r])
        return curr
    
    if len(left) == 1:
        left_formula = clone_ast(left[0])
    else:
        left_formula = left[0]
        for l in left[1:]:
            left_formula = Connective(name="∧", arity=2, arguments=[left_formula, l])
            
    if not right:
        return Connective(name="¬", arity=1, arguments=[left_formula])
        
    if len(right) == 1:
        right_formula = clone_ast(right[0])
    else:
        right_formula = right[0]
        for r in right[1:]:
            right_formula = Connective(name="∨", arity=2, arguments=[right_formula, r])
            
    return Connective(name="⇒", arity=2, arguments=[left_formula, right_formula])

def decode_propositional_to_fol(node: FormulaNode, reverse_mapping: Dict[str, FormulaNode]) -> FormulaNode:
    """Reconstructs the first-order logic formula from its propositional variable representation."""
    if isinstance(node, PropositionalVariable):
        if node.name in reverse_mapping:
            res = clone_ast(reverse_mapping[node.name])
            res.prefix_formatting = [clone_ast(n) for n in node.prefix_formatting]
            res.postfix_formatting = [clone_ast(n) for n in node.postfix_formatting]
            return res
        return clone_ast(node)
    elif isinstance(node, Connective):
        decoded_args = [decode_propositional_to_fol(arg, reverse_mapping) for arg in node.arguments]
        res = Connective(name=node.name, arity=node.arity, arguments=decoded_args)
        res.prefix_formatting = [clone_ast(n) for n in node.prefix_formatting]
        res.postfix_formatting = [clone_ast(n) for n in node.postfix_formatting]
        return res
    else:
        return clone_ast(node)

def auto_prove(f_name: str, env: Environment, visited_nodes: Optional[List[FormulaNode]] = None) -> bool:
    """
    Attempts to prove the formula with name f_name in environment env.
    If proven, adds it to env.theorems and returns True. Otherwise, returns False.
    """
    if visited_nodes is None:
        visited_nodes = []

    if f_name not in env.formulae:
        print(f"Error: Formula '{f_name}' not found in environment.")
        return False

    f_node = env.formulae[f_name]

    # 1. Already proven check (including structural isomorphism)
    if f_name in env.theorems:
        print(f"Goal '{f_name}' is already proven.")
        return True
    
    for th_name, th_node in env.theorems.items():
        if is_structurally_equal(f_node, th_node):
            print(f"Goal '{f_name}' is already proven (as theorem '{th_name}').")
            env.theorems[f_name] = clone_ast(th_node)
            return True

    # Check for recursion loop
    if any(is_structurally_equal(f_node, vn) for vn in visited_nodes):
        return False

    # Push to visited list
    visited_nodes = visited_nodes + [f_node]

    # 2. Try direct axioms (logical and ZFC)
    for ax_name, axiom_func in AXIOMS.items():
        try:
            if axiom_func(f_node):
                print(f"[Auto] Proved '{f_name}' ('{reconstruct_string(f_node)}') using axiom '{ax_name}'.")
                env.theorems[f_name] = clone_ast(f_node)
                return True
        except Exception:
            pass

    # 3. Try QR1
    # psi => (∀x phi)
    if isinstance(f_node, Connective) and f_node.name == "⇒" and len(f_node.arguments) == 2:
        psi, cons_right = f_node.arguments[0], f_node.arguments[1]
        if isinstance(cons_right, Quantifier) and cons_right.name == "∀":
            x_name = cons_right.variable.name
            phi = cons_right.formula
            
            # Check QR1 conditions
            if not check_free(psi, x_name) and not check_bound(phi, x_name):
                # Premise is: psi => phi
                premise = Connective(name="⇒", arity=2, arguments=[clone_ast(psi), clone_ast(phi)])
                
                # Find or create premise name
                premise_name = None
                for name, node in env.formulae.items():
                    if is_structurally_equal(node, premise):
                        premise_name = name
                        break
                if premise_name is None:
                    counter = len(env.formulae)
                    while True:
                        premise_name = f"auto_f_{counter}"
                        if premise_name not in env.formulae:
                            break
                        counter += 1
                    env.formulae[premise_name] = premise
                
                # Try to prove the premise recursively
                print(f"[Auto] Attempting QR1: Proving premise '{premise_name}' ('{reconstruct_string(premise)}') to prove '{f_name}'...")
                if auto_prove(premise_name, env, visited_nodes):
                    # Verify using rule_QR1
                    premise_theorem = env.theorems[premise_name]
                    if rule_QR1([premise_theorem], f_node):
                        env.theorems[f_name] = clone_ast(f_node)
                        print(f"[Auto] Proved '{f_name}' using rule 'QR1' with premise '{premise_name}'.")
                        return True

    # 4. Try QR2
    # (∃x phi) => psi
    if isinstance(f_node, Connective) and f_node.name == "⇒" and len(f_node.arguments) == 2:
        cons_left, psi = f_node.arguments[0], f_node.arguments[1]
        if isinstance(cons_left, Quantifier) and cons_left.name == "∃":
            x_name = cons_left.variable.name
            phi = cons_left.formula
            
            # Check QR2 conditions
            if not check_free(psi, x_name) and not check_bound(phi, x_name):
                # Premise is: phi => psi
                premise = Connective(name="⇒", arity=2, arguments=[clone_ast(phi), clone_ast(psi)])
                
                # Find or create premise name
                premise_name = None
                for name, node in env.formulae.items():
                    if is_structurally_equal(node, premise):
                        premise_name = name
                        break
                if premise_name is None:
                    counter = len(env.formulae)
                    while True:
                        premise_name = f"auto_f_{counter}"
                        if premise_name not in env.formulae:
                            break
                        counter += 1
                    env.formulae[premise_name] = premise
                
                # Try to prove the premise recursively
                print(f"[Auto] Attempting QR2: Proving premise '{premise_name}' ('{reconstruct_string(premise)}') to prove '{f_name}'...")
                if auto_prove(premise_name, env, visited_nodes):
                    premise_theorem = env.theorems[premise_name]
                    if rule_QR2([premise_theorem], f_node):
                        env.theorems[f_name] = clone_ast(f_node)
                        print(f"[Auto] Proved '{f_name}' using rule 'QR2' with premise '{premise_name}'.")
                        return True

    # 5. Try PC2 (propositional sequent calculus decomposition)
    try:
        prop_f1, mappings = abstract_to_propositional_with_mapping(f_node)
        reverse_mapping = {p_var.name: sf_clean for sf_clean, p_var in mappings}
        
        leaf_sequents = collect_leaf_sequents([], [prop_f1])
        
        if not leaf_sequents:
            # Already a propositional tautology
            if rule_PC2([], f_node):
                env.theorems[f_name] = clone_ast(f_node)
                print(f"[Auto] Proved '{f_name}' using rule 'PC2' with no premises.")
                return True
        else:
            # Check for progress: if there's only one leaf and it decodes back to the same formula, skip to avoid loop
            if len(leaf_sequents) == 1:
                p_leaf = make_sequent_formula(leaf_sequents[0][0], leaf_sequents[0][1])
                fol_leaf = decode_propositional_to_fol(p_leaf, reverse_mapping)
                if is_structurally_equal(fol_leaf, f_node):
                    return False
            
            # Attempt to prove all leaf formulas
            premise_names = []
            all_proven = True
            
            print(f"[Auto] Attempting PC2 decomposition: Decomposing '{f_name}' into {len(leaf_sequents)} leaf formulas...")
            for idx, (left_seq, right_seq) in enumerate(leaf_sequents):
                p_leaf = make_sequent_formula(left_seq, right_seq)
                fol_leaf = decode_propositional_to_fol(p_leaf, reverse_mapping)
                
                # Find or create name for leaf formula
                leaf_name = None
                for name, node in env.formulae.items():
                    if is_structurally_equal(node, fol_leaf):
                        leaf_name = name
                        break
                if leaf_name is None:
                    counter = len(env.formulae)
                    while True:
                        leaf_name = f"auto_f_{counter}"
                        if leaf_name not in env.formulae:
                            break
                        counter += 1
                    env.formulae[leaf_name] = fol_leaf
                
                # Recursively prove the leaf formula
                print(f"[Auto] Decomposed leaf {idx+1}/{len(leaf_sequents)}: Proving '{leaf_name}' ('{reconstruct_string(fol_leaf)}')...")
                if auto_prove(leaf_name, env, visited_nodes):
                    premise_names.append(leaf_name)
                else:
                    all_proven = False
                    print(f"[Auto] Failed to prove leaf '{leaf_name}' ('{reconstruct_string(fol_leaf)}').")
                    break
            
            if all_proven:
                premise_nodes = [env.theorems[pn] for pn in premise_names]
                if rule_PC2(premise_nodes, f_node):
                    env.theorems[f_name] = clone_ast(f_node)
                    print(f"[Auto] Proved '{f_name}' using rule 'PC2' and premises: {', '.join(premise_names)}.")
                    return True
    except Exception as e:
        print(f"[Auto] Error during PC2 decomposition for '{f_name}': {e}")
        pass

    return False
