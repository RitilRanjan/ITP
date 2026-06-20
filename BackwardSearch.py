import itertools
import heapq
from typing import List, Dict, Set, Optional, Tuple, Any

from AST import (
    Node, FormulaNode, TermNode, Variable, DummyVariable, PropositionalVariable,
    Function, Relation, Connective, Quantifier, is_structurally_equal
)
from SubstitutionManager import clone_ast, substitute_all
from GraphSearch import SearchLimits, SearchLimitExceeded, extract_vocabulary
from Frontend import reconstruct_string
from Environment import Environment
from ProofGenerator import ProofGenerator

# ==========================================
# 1. CNF Conversion Pipeline
# ==========================================

def eliminate_implications(formula: FormulaNode) -> FormulaNode:
    """Replaces A ⇒ B with ¬A ∨ B, and A ⇔ B with (¬A ∨ B) ∧ (A ∨ ¬B)."""
    if isinstance(formula, Connective):
        if formula.name == "⇒" and len(formula.arguments) == 2:
            A = eliminate_implications(formula.arguments[0])
            B = eliminate_implications(formula.arguments[1])
            not_A = Connective(name="¬", arity=1, arguments=[A])
            return Connective(name="∨", arity=2, arguments=[not_A, B])
        elif formula.name == "⇔" and len(formula.arguments) == 2:
            A = eliminate_implications(formula.arguments[0])
            B = eliminate_implications(formula.arguments[1])
            not_A = Connective(name="¬", arity=1, arguments=[clone_ast(A)])
            not_B = Connective(name="¬", arity=1, arguments=[clone_ast(B)])
            or1 = Connective(name="∨", arity=2, arguments=[not_A, clone_ast(B)])
            or2 = Connective(name="∨", arity=2, arguments=[clone_ast(A), not_B])
            return Connective(name="∧", arity=2, arguments=[or1, or2])
        else:
            return Connective(
                name=formula.name,
                arity=formula.arity,
                arguments=[eliminate_implications(arg) for arg in formula.arguments]
            )
    elif isinstance(formula, Quantifier):
        return Quantifier(
            name=formula.name,
            variable=clone_ast(formula.variable),
            formula=eliminate_implications(formula.formula)
        )
    return clone_ast(formula)

def to_nnf(formula: FormulaNode) -> FormulaNode:
    """Pushes negations inwards using De Morgan's laws and quantifier duality."""
    if isinstance(formula, Connective) and formula.name == "¬":
        arg = formula.arguments[0]
        if isinstance(arg, Connective):
            if arg.name == "¬":
                # ¬¬A -> A
                return to_nnf(arg.arguments[0])
            elif arg.name == "∧":
                # ¬(A ∧ B) -> ¬A ∨ ¬B
                not_A = Connective(name="¬", arity=1, arguments=[arg.arguments[0]])
                not_B = Connective(name="¬", arity=1, arguments=[arg.arguments[1]])
                return Connective(name="∨", arity=2, arguments=[to_nnf(not_A), to_nnf(not_B)])
            elif arg.name == "∨":
                # ¬(A ∨ B) -> ¬A ∧ ¬B
                not_A = Connective(name="¬", arity=1, arguments=[arg.arguments[0]])
                not_B = Connective(name="¬", arity=1, arguments=[arg.arguments[1]])
                return Connective(name="∧", arity=2, arguments=[to_nnf(not_A), to_nnf(not_B)])
        elif isinstance(arg, Quantifier):
            if arg.name == "∀":
                # ¬∀x P -> ∃x ¬P
                not_P = Connective(name="¬", arity=1, arguments=[arg.formula])
                return Quantifier(name="∃", variable=clone_ast(arg.variable), formula=to_nnf(not_P))
            elif arg.name == "∃":
                # ¬∃x P -> ∀x ¬P
                not_P = Connective(name="¬", arity=1, arguments=[arg.formula])
                return Quantifier(name="∀", variable=clone_ast(arg.variable), formula=to_nnf(not_P))
                
        # Base case for literal negation
        return Connective(name="¬", arity=1, arguments=[to_nnf(arg)])
        
    elif isinstance(formula, Connective):
        return Connective(
            name=formula.name,
            arity=formula.arity,
            arguments=[to_nnf(arg) for arg in formula.arguments]
        )
    elif isinstance(formula, Quantifier):
        return Quantifier(
            name=formula.name,
            variable=clone_ast(formula.variable),
            formula=to_nnf(formula.formula)
        )
        
    return clone_ast(formula)

std_counter = 0

def standardize_variables(formula: FormulaNode, var_map: Optional[Dict[str, str]] = None) -> FormulaNode:
    """Ensures every quantifier binds a unique variable name."""
    global std_counter
    if var_map is None:
        var_map = {}
        
    if isinstance(formula, Quantifier):
        old_name = formula.variable.name
        std_counter += 1
        new_name = f"{old_name}{std_counter}"
        new_var_map = var_map.copy()
        new_var_map[old_name] = new_name
        
        return Quantifier(
            name=formula.name,
            variable=Variable(name=new_name),
            formula=standardize_variables(formula.formula, new_var_map)
        )
    elif isinstance(formula, Connective):
        return Connective(
            name=formula.name,
            arity=formula.arity,
            arguments=[standardize_variables(arg, var_map) for arg in formula.arguments]
        )
    elif isinstance(formula, Relation):
        new_args = []
        for arg in formula.arguments:
            new_args.append(_standardize_term(arg, var_map))
        return Relation(
            name=formula.name,
            arity=formula.arity,
            rel_type=formula.rel_type,
            arguments=new_args
        )
    return clone_ast(formula)

def _standardize_term(term: TermNode, var_map: Dict[str, str]) -> TermNode:
    if isinstance(term, Variable):
        return Variable(name=var_map.get(term.name, term.name))
    elif isinstance(term, Function):
        return Function(
            name=term.name,
            arity=term.arity,
            func_type=term.func_type,
            arguments=[_standardize_term(arg, var_map) for arg in term.arguments]
        )
    return clone_ast(term)

skolem_counter = 0

def skolemize(formula: FormulaNode, universal_vars: Optional[List[Variable]] = None) -> FormulaNode:
    """Replaces existential variables with Skolem functions."""
    global skolem_counter
    if universal_vars is None:
        universal_vars = []
        
    if isinstance(formula, Quantifier):
        if formula.name == "∀":
            new_universals = universal_vars + [formula.variable]
            return Quantifier(
                name="∀",
                variable=clone_ast(formula.variable),
                formula=skolemize(formula.formula, new_universals)
            )
        elif formula.name == "∃":
            skolem_counter += 1
            sk_name = f"sk{skolem_counter}"
            
            if len(universal_vars) == 0:
                # Skolem constant (0-ary function)
                sk_term = Function(name=sk_name, arity=0, arguments=[])
            else:
                sk_term = Function(name=sk_name, arity=len(universal_vars), arguments=[clone_ast(v) for v in universal_vars])
                
            # Substitute the existential variable with the skolem term
            substituted = substitute_all(clone_ast(formula.formula), formula.variable.name, sk_term)
            return skolemize(substituted, universal_vars)
            
    elif isinstance(formula, Connective):
        return Connective(
            name=formula.name,
            arity=formula.arity,
            arguments=[skolemize(arg, universal_vars) for arg in formula.arguments]
        )
        
    return clone_ast(formula)

def drop_universals(formula: FormulaNode) -> FormulaNode:
    """Strips all ∀ quantifiers."""
    if isinstance(formula, Quantifier):
        return drop_universals(formula.formula)
    elif isinstance(formula, Connective):
        return Connective(
            name=formula.name,
            arity=formula.arity,
            arguments=[drop_universals(arg) for arg in formula.arguments]
        )
    return clone_ast(formula)

def distribute_or_over_and(formula: FormulaNode) -> FormulaNode:
    """Converts a quantifier-free NNF into Conjunctive Normal Form (CNF)."""
    if isinstance(formula, Connective):
        if formula.name == "∨":
            # Flatten consecutive ORs (though not strictly necessary if recursive)
            # Binary OR case
            left = distribute_or_over_and(formula.arguments[0])
            right = distribute_or_over_and(formula.arguments[1])
            
            if isinstance(left, Connective) and left.name == "∧":
                # (A ∧ B) ∨ C -> (A ∨ C) ∧ (B ∨ C)
                A = left.arguments[0]
                B = left.arguments[1]
                C = right
                return Connective(name="∧", arity=2, arguments=[
                    distribute_or_over_and(Connective(name="∨", arity=2, arguments=[clone_ast(A), clone_ast(C)])),
                    distribute_or_over_and(Connective(name="∨", arity=2, arguments=[clone_ast(B), clone_ast(C)]))
                ])
            elif isinstance(right, Connective) and right.name == "∧":
                # A ∨ (B ∧ C) -> (A ∨ B) ∧ (A ∨ C)
                A = left
                B = right.arguments[0]
                C = right.arguments[1]
                return Connective(name="∧", arity=2, arguments=[
                    distribute_or_over_and(Connective(name="∨", arity=2, arguments=[clone_ast(A), clone_ast(B)])),
                    distribute_or_over_and(Connective(name="∨", arity=2, arguments=[clone_ast(A), clone_ast(C)]))
                ])
            else:
                return Connective(name="∨", arity=2, arguments=[left, right])
                
        elif formula.name == "∧":
            return Connective(
                name="∧",
                arity=2,
                arguments=[distribute_or_over_and(formula.arguments[0]), distribute_or_over_and(formula.arguments[1])]
            )
        elif formula.name == "¬":
            return Connective(name="¬", arity=1, arguments=[distribute_or_over_and(formula.arguments[0])])
            
    return clone_ast(formula)

def extract_clauses(formula: FormulaNode) -> List[List[FormulaNode]]:
    """Converts the CNF AST into a list of clauses (each clause is a list of literal AST nodes)."""
    if isinstance(formula, Connective) and formula.name == "∧":
        left_clauses = extract_clauses(formula.arguments[0])
        right_clauses = extract_clauses(formula.arguments[1])
        return left_clauses + right_clauses
        
    # It's a single clause, extract literals
    def extract_literals(node: FormulaNode) -> List[FormulaNode]:
        if isinstance(node, Connective) and node.name == "∨":
            return extract_literals(node.arguments[0]) + extract_literals(node.arguments[1])
        else:
            # It's a literal
            return [clone_ast(node)]
            
    return [extract_literals(formula)]

def process_to_cnf(formula: FormulaNode) -> List[List[FormulaNode]]:
    """Full pipeline: formula -> list of clauses."""
    f1 = eliminate_implications(formula)
    f2 = to_nnf(f1)
    f3 = standardize_variables(f2)
    f4 = skolemize(f3)
    f5 = drop_universals(f4)
    f6 = distribute_or_over_and(f5)
    return extract_clauses(f6)

# ==========================================
# 2. Unification
# ==========================================

def occurs_check(var_name: str, term: TermNode, subst: Dict[str, TermNode]) -> bool:
    """Returns True if var_name occurs in term (after applying substitutions)."""
    if isinstance(term, Variable):
        if term.name == var_name:
            return True
        elif term.name in subst:
            return occurs_check(var_name, subst[term.name], subst)
        return False
    elif isinstance(term, Function):
        for arg in term.arguments:
            if occurs_check(var_name, arg, subst):
                return True
        return False
    return False

def unify(node1: Node, node2: Node, subst: Dict[str, TermNode]) -> bool:
    """
    Implements Robinson's unification algorithm.
    Returns True if unified, updating `subst` in place.
    """
    # Resolve variables to their bounds
    if isinstance(node1, Variable) and node1.name in subst:
        return unify(subst[node1.name], node2, subst)
    if isinstance(node2, Variable) and node2.name in subst:
        return unify(node1, subst[node2.name], subst)

    # Identical variables or propositional variables
    if isinstance(node1, Variable) and isinstance(node2, Variable):
        if node1.name == node2.name:
            return True
        
    if isinstance(node1, PropositionalVariable) and isinstance(node2, PropositionalVariable):
        return node1.name == node2.name

    # Variable bindings
    if isinstance(node1, Variable):
        if occurs_check(node1.name, node2, subst):
            return False
        subst[node1.name] = clone_ast(node2)
        return True
    elif isinstance(node2, Variable):
        if occurs_check(node2.name, node1, subst):
            return False
        subst[node2.name] = clone_ast(node1)
        return True

    # Functions, Relations, Connectives
    if type(node1) != type(node2) or node1.name != node2.name:
        return False

    if hasattr(node1, 'arguments') and hasattr(node2, 'arguments'):
        if len(node1.arguments) != len(node2.arguments):
            return False
        for a1, a2 in zip(node1.arguments, node2.arguments):
            if not unify(a1, a2, subst):
                return False
        return True

    return False

def apply_substitution(node: Node, subst: Dict[str, TermNode]) -> Node:
    """Applies a substitution dictionary to an AST node."""
    if isinstance(node, Variable):
        if node.name in subst:
            # We must recursively apply substitution in case subst[v] contains variables that are also in subst
            return apply_substitution(subst[node.name], subst)
        return clone_ast(node)
    elif isinstance(node, PropositionalVariable):
        return clone_ast(node)
    elif isinstance(node, Function):
        return Function(
            name=node.name,
            arity=node.arity,
            func_type=node.func_type,
            arguments=[apply_substitution(arg, subst) for arg in node.arguments]
        )
    elif isinstance(node, Relation):
        return Relation(
            name=node.name,
            arity=node.arity,
            rel_type=node.rel_type,
            arguments=[apply_substitution(arg, subst) for arg in node.arguments]
        )
    elif isinstance(node, Connective):
        return Connective(
            name=node.name,
            arity=node.arity,
            arguments=[apply_substitution(arg, subst) for arg in node.arguments]
        )
    return clone_ast(node)

# ==========================================
# 3. Resolution
# ==========================================

def get_literal_core(literal: FormulaNode) -> Tuple[bool, FormulaNode]:
    """Returns (is_positive, core_literal_node)."""
    if isinstance(literal, Connective) and literal.name == "¬":
        return False, literal.arguments[0]
    return True, literal

def clause_to_string(clause: List[FormulaNode]) -> str:
    """Creates a stable string representation for a clause to help with deduplication."""
    lits = [reconstruct_string(l) for l in clause]
    return " ∨ ".join(sorted(lits))

def factorize(clause: List[FormulaNode]) -> List[FormulaNode]:
    """Unifies literals within the same clause to reduce redundancy."""
    # A simple factorization: remove exactly identical literals structurally.
    # Advanced factorization would try to unify unifiable literals of the same sign.
    new_clause = []
    for lit in clause:
        if not any(is_structurally_equal(lit, existing) for existing in new_clause):
            new_clause.append(clone_ast(lit))
    return new_clause

def are_variants(clause1: List[FormulaNode], clause2: List[FormulaNode]) -> bool:
    """Checks if clause1 and clause2 are variants (subsumption with exact match up to renaming)."""
    if len(clause1) != len(clause2):
        return False
        
    def try_unify_all(idx1, c2_remaining, subst):
        if idx1 == len(clause1):
            return True
            
        for i, lit2 in enumerate(c2_remaining):
            new_subst = subst.copy()
            if unify(clause1[idx1], lit2, new_subst):
                new_remaining = c2_remaining[:i] + c2_remaining[i+1:]
                if try_unify_all(idx1 + 1, new_remaining, new_subst):
                    return True
        return False

    return try_unify_all(0, clause2, {})

def resolve(clause1: List[FormulaNode], clause2: List[FormulaNode]) -> List[List[FormulaNode]]:
    """Computes all possible resolvents of two clauses."""
    # Standardize apart variables before resolving
    c1 = [standardize_variables(lit) for lit in clause1]
    c2 = [standardize_variables(lit) for lit in clause2]
    
    resolvents = []
    
    for i, lit1 in enumerate(c1):
        for j, lit2 in enumerate(c2):
            sign1, core1 = get_literal_core(lit1)
            sign2, core2 = get_literal_core(lit2)
            
            # They must have opposite signs
            if sign1 == sign2:
                continue
                
            subst = {}
            if unify(core1, core2, subst):
                # We found a resolution pair!
                # Create the resolvent by removing lit1 and lit2, and applying subst
                resolvent = []
                for k, l in enumerate(c1):
                    if k != i:
                        resolvent.append(apply_substitution(l, subst))
                for k, l in enumerate(c2):
                    if k != j:
                        resolvent.append(apply_substitution(l, subst))
                        
                resolvent = factorize(resolvent)
                resolvents.append(resolvent)
                
    return resolvents

# ==========================================
# 4. Search Loop
# ==========================================
def deskolemize_clause(clause_node: FormulaNode) -> FormulaNode:
    """Converts a skolemized clause back into a quantified FOL formula for display."""
    from AST import Function, Variable, Quantifier
    from SubstitutionManager import clone_ast
    
    all_vars = set()
    skolem_funcs = {}
    
    def walk(node):
        if isinstance(node, Variable):
            all_vars.add(node.name)
        elif isinstance(node, Function):
            if node.name.startswith("sk"):
                skolem_funcs[node.name] = node
            for arg in node.arguments:
                walk(arg)
        elif hasattr(node, "arguments"):
            for arg in node.arguments:
                walk(arg)
        elif hasattr(node, "formula"):
            walk(node.formula)
            
    walk(clause_node)
    
    def replace_skolems(node):
        if isinstance(node, Function):
            if node.name.startswith("sk"):
                return Variable(name="y_" + node.name)
            else:
                new_args = [replace_skolems(arg) for arg in node.arguments]
                new_node = clone_ast(node)
                new_node.arguments = new_args
                return new_node
        elif hasattr(node, "arguments"):
            new_args = [replace_skolems(arg) for arg in node.arguments]
            new_node = clone_ast(node)
            new_node.arguments = new_args
            return new_node
        elif hasattr(node, "formula"):
            new_node = clone_ast(node)
            new_node.formula = replace_skolems(node.formula)
            return new_node
        return clone_ast(node)
        
    result_node = replace_skolems(clause_node)
    
    zero_ary_sk = sorted([name for name, f in skolem_funcs.items() if f.arity == 0])
    n_ary_sk = sorted([name for name, f in skolem_funcs.items() if f.arity > 0])
    
    for sk in n_ary_sk:
        result_node = Quantifier(name="∃", variable=Variable(name="y_" + sk), formula=result_node)
        
    for v in sorted(list(all_vars)):
        result_node = Quantifier(name="∀", variable=Variable(name=v), formula=result_node)
        
    for sk in zero_ary_sk:
        result_node = Quantifier(name="∃", variable=Variable(name="y_" + sk), formula=result_node)
        
    return result_node

def log_resolution_proof(pg, proof_logger, env, goal_name, goal):
    structured = pg.get_structured_proof()
    if not structured:
        return
        
    id_to_name = {}
    from AST import Connective
    
    for step_num, (node_id, op, parents, clause) in enumerate(structured, 1):
        clause_name = f"res_{goal_name}_{step_num}"
        id_to_name[node_id] = clause_name
        
        # Build FormulaNode from clause
        if not clause:
            # Empty clause is false (⊥)
            from AST import PropositionalVariable
            clause_node = PropositionalVariable("⊥")
        elif len(clause) == 1:
            clause_node = clone_ast(clause[0])
        else:
            curr = clone_ast(clause[0])
            for lit in clause[1:]:
                curr = Connective(name="∨", arity=2, arguments=[curr, clone_ast(lit)])
            clause_node = curr
            
        clause_node = deskolemize_clause(clause_node)
            
        env.formulae[clause_name] = clause_node
        
        # Log it
        if op.startswith("axiom:"):
            # Original axiom
            ax_name = op.split("axiom: ")[1]
            if ax_name in env.theorems:
                proof_logger.log_rule([(ax_name, env.theorems[ax_name])], clause_name, clause_node, f"cnf-conversion (skolemized)")
            else:
                proof_logger.log_rule([], clause_name, clause_node, op)
        elif op.startswith("goal:"):
            # Negated goal
            proof_logger.log_rule([], clause_name, clause_node, "negated-goal (skolemized)")
        else:
            # Resolution or paramodulation step
            parent_names = [id_to_name[p] for p in parents]
            proof_logger.log_rule([(p, env.formulae[p]) for p in parent_names], clause_name, clause_node, op)
            
    # Finally log the contradiction resolving the main goal
    empty_clause_name = id_to_name.get(structured[-1][0], None)
    if empty_clause_name:
        proof_logger.log_rule([(empty_clause_name, env.formulae[empty_clause_name])], goal_name, goal, "contradiction-elim (resolution)")

def backward_search(env: Environment, goal_name: str, time_limit: float = 10.0, space_limit: int = 10000, generate_proof: bool = False, proof_logger=None) -> bool:
    """
    Executes a refutation-based resolution theorem prover.
    """
    if goal_name not in env.formulae:
        print(f"Error: Goal formula '{goal_name}' not found.")
        return False
        
    goal = env.formulae[goal_name]
    print(f"--- Backward Search (Resolution) ---")
    print(f"Goal: {reconstruct_string(goal)}")
    print(f"Time Limit: {time_limit} seconds")
    print(f"Space Limit: {space_limit} structures")
    
    limits = SearchLimits(time_limit=time_limit, space_limit=space_limit)
    
    clauses: List[List[FormulaNode]] = []
    
    # History tracking
    all_clauses = []
    clause_history = {}
    
    def add_to_history(c: List[FormulaNode], op: str, parents: Tuple[int, ...]):
        c_id = id(c)
        all_clauses.append(c)
        clause_history[c_id] = (op, parents, c)
        return c_id

    # 1. Convert axioms to CNF
    print("Converting environment theorems to CNF...")
    for thm_name, thm_node in env.theorems.items():
        thm_clauses = process_to_cnf(thm_node)
        for c in thm_clauses:
            add_to_history(c, f"axiom: {thm_name}", ())
            clauses.append(c)
            
    # 2. Negate goal and convert to CNF
    print("Negating goal and converting to CNF...")
    negated_goal = Connective(name="¬", arity=1, arguments=[clone_ast(goal)])
    goal_clauses = process_to_cnf(negated_goal)
    for c in goal_clauses:
        add_to_history(c, f"goal: {goal_name}", ())
        clauses.append(c)
        
    print(f"Initial clause set size: {len(clauses)}")
    
    # Deduplicate initial clauses
    unique_clauses = []
    for c in clauses:
        if not any(are_variants(c, existing) for existing in unique_clauses):
            unique_clauses.append(c)
    clauses = unique_clauses
    print(f"Unique initial clauses: {len(clauses)}")
    
    if len(clauses) == 0:
        print("Empty clause set, nothing to resolve.")
        return False

    def finish_proof(empty_clause_id: int):
        print("\nSUCCESS! Empty clause derived.")
        pg = ProofGenerator(clause_history, empty_clause_id)
        if generate_proof:
            print("\n" + pg.generate_proof())
        env.theorems[goal_name] = clone_ast(goal)
        if proof_logger:
            log_resolution_proof(pg, proof_logger, env, goal_name, goal)
        return True

    # Check if empty clause is already there
    for c in clauses:
        if len(c) == 0:
            return finish_proof(id(c))

    try:
        new_clauses = list(clauses)
        level = 0
        
        while True:
            limits.check_time()
            level += 1
            print(f"\n[Resolution Level {level}]")
            
            generated_this_level = []
            
            # Resolve every clause in new_clauses against every clause in clauses
            for i, c1 in enumerate(new_clauses):
                for j, c2 in enumerate(clauses):
                    limits.check_time()
                    
                    res_list = resolve(c1, c2)
                    for r in res_list:
                        r_id = add_to_history(r, "resolution", (id(c1), id(c2)))
                        # Check if it's the empty clause
                        if len(r) == 0:
                            print(f"\nSUCCESS! Empty clause derived at level {level}.")
                            return finish_proof(r_id)
                            
                        # Keep it if it's not a variant of existing clauses
                        is_redundant = False
                        # We use are_variants for subsumption
                        for existing in clauses + generated_this_level:
                            if are_variants(r, existing):
                                is_redundant = True
                                break
                        
                        if not is_redundant:
                            generated_this_level.append(r)
                            
            print(f"Generated {len(generated_this_level)} new unique clauses.")
            
            if not generated_this_level:
                print("\nFAILED: No new clauses can be generated (Saturation reached).")
                return False
                
            limits.check_space(len(clauses) + len(generated_this_level))
            
            # Incorporate new clauses
            clauses.extend(generated_this_level)
            new_clauses = generated_this_level

    except SearchLimitExceeded as e:
        print(f"\nSearch stopped: {e}")
        return False

# ==========================================
# 5. Advanced Heuristics (Subsumption, Paramodulation, Priority Queue)
# ==========================================

def one_way_match(pattern: Node, target: Node, subst: Dict[str, TermNode]) -> bool:
    """Matches pattern to target. Only variables in pattern can be bound."""
    if isinstance(pattern, Variable):
        if pattern.name in subst:
            return is_structurally_equal(subst[pattern.name], target)
        else:
            subst[pattern.name] = clone_ast(target)
            return True
    elif isinstance(target, Variable):
        return False
        
    if type(pattern) != type(target) or pattern.name != target.name:
        return False
        
    if hasattr(pattern, 'arguments') and hasattr(target, 'arguments'):
        if len(pattern.arguments) != len(target.arguments):
            return False
        for p_arg, t_arg in zip(pattern.arguments, target.arguments):
            if not one_way_match(p_arg, t_arg, subst):
                return False
        return True
    return False

def subsumes(c1: List[FormulaNode], c2: List[FormulaNode]) -> bool:
    """Returns True if clause c1 subsumes clause c2 (c1θ ⊆ c2)."""
    if len(c1) > len(c2):
        return False
    if len(c1) == 0:
        return True
        
    def backtrack(idx, current_subst):
        if idx == len(c1):
            return True
        lit1 = c1[idx]
        for lit2 in c2:
            new_subst = current_subst.copy()
            if one_way_match(lit1, lit2, new_subst):
                if backtrack(idx + 1, new_subst):
                    return True
        return False

    return backtrack(0, {})

def get_subterms_with_paths(node: Node, current_path: List[int] = None) -> List[Tuple[List[int], TermNode]]:
    if current_path is None:
        current_path = []
    res = []
    if isinstance(node, (Variable, Function)):
        res.append((current_path, node))
    if hasattr(node, 'arguments'):
        for i, arg in enumerate(node.arguments):
            res.extend(get_subterms_with_paths(arg, current_path + [i]))
    return res

def apply_substitution_at_path(node: Node, path: List[int], replacement_term: TermNode, subst: Dict[str, TermNode]) -> Node:
    if not path:
        return apply_substitution(replacement_term, subst)
    
    idx = path[0]
    new_args = []
    for i, arg in enumerate(node.arguments):
        if i == idx:
            new_args.append(apply_substitution_at_path(arg, path[1:], replacement_term, subst))
        else:
            new_args.append(apply_substitution(arg, subst))
            
    if isinstance(node, Function):
        return Function(node.name, node.arity, node.func_type, new_args)
    elif isinstance(node, Relation):
        return Relation(node.name, node.arity, node.rel_type, new_args)
    elif isinstance(node, Connective):
        return Connective(node.name, node.arity, new_args)
    return clone_ast(node)

def get_var_counts(term: TermNode) -> Dict[str, int]:
    counts = {}
    def visit(node):
        if isinstance(node, Variable):
            counts[node.name] = counts.get(node.name, 0) + 1
        elif hasattr(node, 'arguments'):
            for arg in node.arguments:
                visit(arg)
    visit(term)
    return counts

def term_weight(term: TermNode) -> int:
    if isinstance(term, Variable):
        return 1
    w = 1
    if hasattr(term, 'arguments'):
        for arg in term.arguments:
            w += term_weight(arg)
    return w

def is_term_greater(t1: TermNode, t2: TermNode) -> bool:
    # 1. Variables constraint: counts(t1, x) >= counts(t2, x) for all variables x
    c1 = get_var_counts(t1)
    c2 = get_var_counts(t2)
    for var, count2 in c2.items():
        if c1.get(var, 0) < count2:
            return False
            
    # 2. Check weight
    w1 = term_weight(t1)
    w2 = term_weight(t2)
    if w1 > w2:
        return True
    if w1 < w2:
        return False
        
    # Weights are equal: check if both are functions
    if isinstance(t1, Function) and isinstance(t2, Function):
        if t1.name > t2.name:
            return True
        elif t1.name < t2.name:
            return False
            
        if t1.arity > t2.arity:
            return True
        elif t1.arity < t2.arity:
            return False
            
        for arg1, arg2 in zip(t1.arguments, t2.arguments):
            if is_term_greater(arg1, arg2):
                return True
            if is_term_greater(arg2, arg1):
                return False
                
    return False

def paramodulate(clause1: List[FormulaNode], clause2: List[FormulaNode], use_ordering: bool = False) -> List[List[FormulaNode]]:
    """Yields all paramodulants of clause1 into clause2 and clause2 into clause1."""
    c1 = [standardize_variables(lit) for lit in clause1]
    c2 = [standardize_variables(lit) for lit in clause2]
    resolvents = []
    
    def try_paramodulate(from_clause, into_clause):
        for i, lit1 in enumerate(from_clause):
            # Check if lit1 is an equality: t1 = t2
            # Our parser creates Relation("=", 2, ...)
            if getattr(lit1, 'name', None) == "=" and hasattr(lit1, 'arguments') and len(lit1.arguments) == 2:
                t1, t2 = lit1.arguments[0], lit1.arguments[1]
                for j, lit2 in enumerate(into_clause):
                    subterms = get_subterms_with_paths(lit2)
                    for path, target_subterm in subterms:
                        if isinstance(target_subterm, Variable):
                            continue # Paramodulating into variables explodes the search space
                            
                        # Try t1 unifying with target_subterm
                        subst = {}
                        if unify(t1, target_subterm, subst):
                            t1_subst = apply_substitution(t1, subst)
                            t2_subst = apply_substitution(t2, subst)
                            if not use_ordering or is_term_greater(t1_subst, t2_subst):
                                new_c1 = [apply_substitution(l, subst) for k, l in enumerate(from_clause) if k != i]
                                new_lit2 = apply_substitution_at_path(lit2, path, t2, subst)
                                new_c2 = [apply_substitution(l, subst) for k, l in enumerate(into_clause) if k != j]
                                res = factorize(new_c1 + new_c2 + [new_lit2])
                                resolvents.append(res)
                            
                        # Try t2 unifying with target_subterm
                        subst = {}
                        if unify(t2, target_subterm, subst):
                            t1_subst = apply_substitution(t1, subst)
                            t2_subst = apply_substitution(t2, subst)
                            if not use_ordering or is_term_greater(t2_subst, t1_subst):
                                new_c1 = [apply_substitution(l, subst) for k, l in enumerate(from_clause) if k != i]
                                new_lit2 = apply_substitution_at_path(lit2, path, t1, subst)
                                new_c2 = [apply_substitution(l, subst) for k, l in enumerate(into_clause) if k != j]
                                res = factorize(new_c1 + new_c2 + [new_lit2])
                                resolvents.append(res)
                            
    try_paramodulate(c1, c2)
    try_paramodulate(c2, c1)
    return resolvents

class AdvancedSearchEngine:
    def __init__(self, limits: SearchLimits, flags: Dict[str, bool]):
        self.limits = limits
        self.use_sos = flags.get("sos", False)
        self.use_unit_pref = flags.get("unit", False)
        self.use_subsumption = flags.get("subsumption", False)
        self.use_paramodulation = flags.get("paramodulation", False)
        self.use_ordering = flags.get("ordering", False)
        
        self.usable_axioms = []
        self.usable_sos = []
        self.unprocessed = [] # heapq: (priority, counter, clause_str, clause, is_sos, c_id)
        self.unprocessed_set = [] # keeping active clauses in queue
        self.counter = 0
        self.clause_history = {} # id -> (operation, parent_ids, clause)
        self.all_clauses = [] # keep references so ids don't get reused

    def is_forward_subsumed(self, clause: List[FormulaNode]) -> bool:
        if not self.use_subsumption:
            return False
        # Check if clause is subsumed by any active usable or unprocessed clause
        all_active = self.usable_axioms + self.usable_sos + [item[3] for item in self.unprocessed_set]
        for c in all_active:
            if subsumes(c, clause):
                return True
        return False

    def backward_subsume(self, clause: List[FormulaNode]):
        if not self.use_subsumption:
            return
        # Remove any clause from usable or unprocessed that is subsumed by `clause`
        self.usable_axioms = [c for c in self.usable_axioms if not subsumes(clause, c)]
        self.usable_sos = [c for c in self.usable_sos if not subsumes(clause, c)]
        # Filter unprocessed_set
        new_unprocessed_set = []
        for item in self.unprocessed_set:
            if not subsumes(clause, item[3]):
                new_unprocessed_set.append(item)
        self.unprocessed_set = new_unprocessed_set

    def add_clause(self, clause: List[FormulaNode], is_sos: bool, parents: Tuple[int, ...] = (), operation: str = "axiom") -> Tuple[bool, Optional[int]]:
        """Returns (found_empty_clause, new_clause_id)."""
        if not self.use_subsumption:
            all_active = self.usable_axioms + self.usable_sos + [item[3] for item in self.unprocessed_set]
            if any(are_variants(clause, existing) for existing in all_active):
                return False, None
                
        if self.is_forward_subsumed(clause):
            return False, None
            
        self.all_clauses.append(clause)
        c_id = id(clause)
        self.clause_history[c_id] = (operation, parents, clause)

        if len(clause) == 0:
            return True, c_id
            
        self.backward_subsume(clause)
        
        priority = len(clause) if self.use_unit_pref else self.counter
        clause_str = clause_to_string(clause)
        item = (priority, self.counter, clause_str, clause, is_sos, c_id)
        heapq.heappush(self.unprocessed, item)
        self.unprocessed_set.append(item)
        self.counter += 1
        return False, c_id

    def solve(self) -> Tuple[bool, Optional[int]]:
        while self.unprocessed:
            self.limits.check_time()
            
            # Pop the best clause
            priority, _, _, given_clause, is_sos, c_id = heapq.heappop(self.unprocessed)
            
            # Check if it was deleted by backward subsumption
            if not any(given_clause is item[3] for item in self.unprocessed_set):
                continue
                
            # Remove from unprocessed_set
            self.unprocessed_set = [item for item in self.unprocessed_set if item[3] is not given_clause]
            
            # Add to usable
            if is_sos:
                self.usable_sos.append(given_clause)
            else:
                self.usable_axioms.append(given_clause)
                
            # Determine targets to resolve against
            if not self.use_sos:
                targets = self.usable_axioms + self.usable_sos
            else:
                if is_sos:
                    targets = self.usable_axioms + self.usable_sos
                else:
                    targets = self.usable_sos
                    
            for target in targets:
                self.limits.check_time()
                t_id = id(target)
                resolvents = resolve(given_clause, target)
                for res in resolvents:
                    found, res_id = self.add_clause(res, is_sos=True, parents=(c_id, t_id), operation="resolution")
                    if found:
                        return True, res_id

                if self.use_paramodulation:
                    paramodulants = paramodulate(given_clause, target, use_ordering=self.use_ordering)
                    for res in paramodulants:
                        found, res_id = self.add_clause(res, is_sos=True, parents=(c_id, t_id), operation="paramodulation")
                        if found:
                            return True, res_id
                        
            self.limits.check_space(len(self.usable_axioms) + len(self.usable_sos) + len(self.unprocessed_set))
            
        return False, None

def advanced_search(env: Environment, goal_name: str, time_limit: float = 10.0, space_limit: int = 10000, flags: Dict[str, bool] = None, generate_proof: bool = False, proof_logger=None) -> bool:
    if flags is None:
        flags = {}
        
    if goal_name not in env.formulae:
        print(f"Error: Goal formula '{goal_name}' not found.")
        return False
        
    goal = env.formulae[goal_name]
    print(f"--- Advanced Backward Search ---")
    print(f"Goal: {reconstruct_string(goal)}")
    print(f"Time Limit: {time_limit} seconds")
    print(f"Space Limit: {space_limit} structures")
    print(f"Flags: {flags}")
    
    limits = SearchLimits(time_limit=time_limit, space_limit=space_limit)
    engine = AdvancedSearchEngine(limits, flags)
    
    def finish_proof(empty_clause_id: int):
        print("\nSUCCESS! Empty clause derived.")
        pg = ProofGenerator(engine.clause_history, empty_clause_id)
        if generate_proof:
            print("\n" + pg.generate_proof())
        env.theorems[goal_name] = clone_ast(goal)
        if proof_logger:
            log_resolution_proof(pg, proof_logger, env, goal_name, goal)
        return True

    print("Converting environment theorems to CNF...")
    for thm_name, thm_node in env.theorems.items():
        thm_clauses = process_to_cnf(thm_node)
        for c in thm_clauses:
            found, c_id = engine.add_clause(c, is_sos=False, parents=(), operation=f"axiom: {thm_name}")
            if found:
                print("\nSUCCESS! Empty clause derived instantly.")
                return finish_proof(c_id)
                
    print("Negating goal and converting to CNF...")
    negated_goal = Connective(name="¬", arity=1, arguments=[clone_ast(goal)])
    goal_clauses = process_to_cnf(negated_goal)
    for c in goal_clauses:
        found, c_id = engine.add_clause(c, is_sos=True, parents=(), operation=f"goal: {goal_name}")
        if found:
            print("\nSUCCESS! Empty clause derived instantly.")
            return finish_proof(c_id)
            
    print(f"Initial usable axioms: {len(engine.usable_axioms)}")
    print(f"Initial unprocessed clauses: {len(engine.unprocessed_set)}")
    
    try:
        success, empty_id = engine.solve()
        if success:
            return finish_proof(empty_id)
        else:
            print("\nFAILED: Saturation reached, no proof found.")
            return False
    except SearchLimitExceeded as e:
        print(f"\nSearch stopped: {e}")
        return False
