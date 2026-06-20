import itertools
import time
from typing import List, Set, Dict, Tuple
from AST import (
    Node, FormulaNode, TermNode, Variable, PropositionalVariable, DummyVariable, 
    Function, Relation, Connective, Quantifier, is_structurally_equal
)
from Frontend import reconstruct_string
from Environment import Environment
from DeductiveSystem import (
    axiom_E1, axiom_E2, axiom_E3, axiom_Q1, axiom_Q2, 
    rule_PC2, rule_QR1, rule_QR2
)
from SubstitutionManager import clone_ast

class SearchLimitExceeded(Exception):
    """Exception raised when search space or time limit is exceeded."""
    pass

class SearchLimits:
    def __init__(self, time_limit: float = 10.0, space_limit: int = 10000):
        self.time_limit = time_limit
        self.space_limit = space_limit
        self.start_time = time.time()
        
    def check_time(self):
        if self.time_limit is not None:
            elapsed = time.time() - self.start_time
            if elapsed > self.time_limit:
                raise SearchLimitExceeded(f"Time limit of {self.time_limit} seconds exceeded.")

    def check_space(self, current_count: int):
        if self.space_limit is not None:
            if current_count > self.space_limit:
                raise SearchLimitExceeded(f"Space limit of {self.space_limit} structures exceeded (currently at {current_count}).")


class Vocabulary:
    def __init__(self):
        self.variables: List[Variable] = []
        self.prop_vars: List[PropositionalVariable] = []
        self.functions: List[Function] = []  
        self.relations: List[Relation] = []  
        self.quantifier_names = ["∀", "∃"]
        self.connective_names = ["¬", "∧", "∨", "⇒", "⇔"]

def extract_vocabulary(goal: FormulaNode, env: Environment) -> Vocabulary:
    """Extracts the symbols used in the goal to restrict the search space."""
    vocab = Vocabulary()
    seen_vars = set()
    seen_prop = set()
    seen_funcs = set()
    seen_rels = set()
    
    def traverse(node: Node):
        if isinstance(node, Variable):
            seen_vars.add(node.name)
        elif isinstance(node, PropositionalVariable):
            seen_prop.add(node.name)
        elif isinstance(node, Function):
            seen_funcs.add((node.name, node.arity, node.func_type))
            for arg in node.arguments:
                traverse(arg)
        elif isinstance(node, Relation):
            seen_rels.add((node.name, node.arity, node.rel_type))
            for arg in node.arguments:
                traverse(arg)
        elif isinstance(node, Connective):
            for arg in node.arguments:
                traverse(arg)
        elif isinstance(node, Quantifier):
            seen_vars.add(node.variable.name)
            traverse(node.formula)
            
    traverse(goal)
    
    # Always include at least one variable if none exist, so we can generate statements
    if not seen_vars:
        seen_vars.add("x")
        
    for v in seen_vars:
        vocab.variables.append(Variable(name=v))
    for p in seen_prop:
        vocab.prop_vars.append(PropositionalVariable(name=p))
    for name, arity, ftype in seen_funcs:
        dummy_args = [DummyVariable(name="d") for _ in range(arity)]
        vocab.functions.append(Function(name=name, arity=arity, func_type=ftype, arguments=dummy_args))
    for name, arity, rtype in seen_rels:
        dummy_args = [DummyVariable(name="d") for _ in range(arity)]
        vocab.relations.append(Relation(name=name, arity=arity, rel_type=rtype, arguments=dummy_args))
        
    return vocab

def generate_terms(vocab: Vocabulary, depth: int, limits: SearchLimits, base_count: int = 0) -> List[TermNode]:
    """Generates all terms up to the given syntactic depth."""
    limits.check_time()
    if depth == 0:
        res = [clone_ast(v) for v in vocab.variables]
        limits.check_space(base_count + len(res))
        return res
    
    prev_terms = generate_terms(vocab, depth - 1, limits, base_count)
    new_terms = list(prev_terms)
    
    for f in vocab.functions:
        for args in itertools.product(prev_terms, repeat=f.arity):
            limits.check_time()
            new_f = Function(name=f.name, arity=f.arity, func_type=f.func_type, arguments=[clone_ast(a) for a in args])
            # Simple deduplication (structural equality can be slow, but essential here)
            if not any(is_structurally_equal(new_f, t) for t in new_terms):
                new_terms.append(new_f)
                limits.check_space(base_count + len(new_terms))
            
    return new_terms

def generate_formulas(vocab: Vocabulary, depth: int, terms: List[TermNode], limits: SearchLimits, base_count: int = 0) -> List[FormulaNode]:
    """Generates all formulas up to the given syntactic depth."""
    limits.check_time()
    if depth == 0:
        formulas = [clone_ast(p) for p in vocab.prop_vars]
        limits.check_space(base_count + len(formulas))
        for r in vocab.relations:
            for args in itertools.product(terms, repeat=r.arity):
                limits.check_time()
                new_r = Relation(name=r.name, arity=r.arity, rel_type=r.rel_type, arguments=[clone_ast(a) for a in args])
                formulas.append(new_r)
                limits.check_space(base_count + len(formulas))
        return formulas
        
    prev_formulas = generate_formulas(vocab, depth - 1, terms, limits, base_count)
    new_formulas = list(prev_formulas)
    
    # Connectives
    for f in prev_formulas:
        limits.check_time()
        new_formulas.append(Connective(name="¬", arity=1, arguments=[clone_ast(f)]))
        limits.check_space(base_count + len(new_formulas))
        
    for op in ["∧", "∨", "⇒", "⇔"]:
        for f1, f2 in itertools.product(prev_formulas, repeat=2):
            limits.check_time()
            new_formulas.append(Connective(name=op, arity=2, arguments=[clone_ast(f1), clone_ast(f2)]))
            limits.check_space(base_count + len(new_formulas))
            
    # Quantifiers
    for q in ["∀", "∃"]:
        for v in vocab.variables:
            for f in prev_formulas:
                limits.check_time()
                new_formulas.append(Quantifier(name=q, variable=clone_ast(v), formula=clone_ast(f)))
                limits.check_space(base_count + len(new_formulas))
                
    return new_formulas

def check_axioms(formulas: List[FormulaNode], limits: SearchLimits) -> List[FormulaNode]:
    """Checks generated formulas against logical axioms and PC2."""
    theorems = []
    for f in formulas:
        limits.check_time()
        if axiom_E1(f) or axiom_E2(f) or axiom_E3(f) or axiom_Q1(f) or axiom_Q2(f):
            theorems.append(f)
            continue
        # PC2 checks if the formula is a propositional tautology
        # We wrap in try/except because SequentEvaluator might raise on complex FOL nesting
        try:
            if rule_PC2([], f):
                theorems.append(f)
        except Exception:
            pass
    return theorems

def apply_modus_ponens(theorems: List[FormulaNode], limits: SearchLimits) -> List[FormulaNode]:
    """Applies Modus Ponens (PC1 without additional premises) to the pool of theorems."""
    new_theorems = []
    for t1 in theorems:
        limits.check_time()
        if isinstance(t1, Connective) and t1.name == "⇒" and len(t1.arguments) == 2:
            P, Q = t1.arguments[0], t1.arguments[1]
            for t2 in theorems:
                limits.check_time()
                if is_structurally_equal(P, t2):
                    new_theorems.append(clone_ast(Q))
                    break
    return new_theorems

def apply_qr_rules(theorems: List[FormulaNode], limits: SearchLimits) -> List[FormulaNode]:
    """Applies QR1 and QR2 rules to the pool of theorems."""
    new_theorems = []
    for t in theorems:
        limits.check_time()
        # We just try to construct conclusion forms and check if QR1/QR2 allows them.
        # This is essentially forward application.
        # QR1: P => Q  ⊢ P => ∀x Q
        if isinstance(t, Connective) and t.name == "⇒" and len(t.arguments) == 2:
            P, Q = t.arguments[0], t.arguments[1]
            
            # Try to derive P => ∀x Q for all variables
            # To avoid enumerating all vars, we extract vars from P and Q
            vars_in_PQ = set()
            def extract_v(node):
                if isinstance(node, Variable): vars_in_PQ.add(node.name)
                elif isinstance(node, Quantifier): 
                    vars_in_PQ.add(node.variable.name)
                    extract_v(node.formula)
                elif hasattr(node, 'arguments'):
                    for a in node.arguments: extract_v(a)
            extract_v(P)
            extract_v(Q)
            
            for v_name in vars_in_PQ:
                limits.check_time()
                # Build conclusion: P => ∀v Q
                conclusion1 = Connective(name="⇒", arity=2, arguments=[
                    clone_ast(P), 
                    Quantifier(name="∀", variable=Variable(name=v_name), formula=clone_ast(Q))
                ])
                if rule_QR1([t], conclusion1):
                    new_theorems.append(conclusion1)
                    
                # QR2: P => Q ⊢ (∃x P) => Q
                conclusion2 = Connective(name="⇒", arity=2, arguments=[
                    Quantifier(name="∃", variable=Variable(name=v_name), formula=clone_ast(P)),
                    clone_ast(Q)
                ])
                if rule_QR2([t], conclusion2):
                    new_theorems.append(conclusion2)
                    
    return new_theorems

def forward_search(env: Environment, goal_name: str, time_limit: float = 10.0, space_limit: int = 10000) -> bool:
    """
    Executes a dovetailed Breadth-First Search (Forward Saturation).
    Generates terms and formulas iteratively, checks axioms, 
    and applies Modus Ponens + QR rules until fixed point or goal is found,
    or time/space limits are exceeded.
    """
    if goal_name not in env.formulae:
        print(f"Error: Goal formula '{goal_name}' not found.")
        return False
        
    goal = env.formulae[goal_name]
    print(f"--- Bounded Forward Search ---")
    print(f"Goal: {reconstruct_string(goal)}")
    print(f"Time Limit: {time_limit} seconds")
    print(f"Space Limit: {space_limit} structures")
    
    vocab = extract_vocabulary(goal, env)
    print(f"Extracted Vocabulary: {len(vocab.variables)} vars, {len(vocab.prop_vars)} prop vars, "
          f"{len(vocab.functions)} funcs, {len(vocab.relations)} rels.")
    
    limits = SearchLimits(time_limit=time_limit, space_limit=space_limit)
    
    proven_theorems: List[FormulaNode] = []
    # Seed with existing environment theorems
    for thm_node in env.theorems.values():
        proven_theorems.append(clone_ast(thm_node))
        
    current_depth = 0
    try:
        while True:
            print(f"\n[Generation {current_depth}]")
            
            terms = generate_terms(vocab, current_depth, limits, base_count=len(proven_theorems))
            print(f"Generated {len(terms)} term structures.")
            
            formulas = generate_formulas(vocab, current_depth, terms, limits, base_count=len(terms) + len(proven_theorems))
            print(f"Generated {len(formulas)} formula structures.")
            
            print("Evaluating axioms and tautologies...")
            new_axioms = check_axioms(formulas, limits)
            added_count = 0
            for ax in new_axioms:
                if not any(is_structurally_equal(ax, p) for p in proven_theorems):
                    proven_theorems.append(ax)
                    limits.check_space(len(terms) + len(formulas) + len(proven_theorems))
                    added_count += 1
                    if is_structurally_equal(ax, goal):
                        print(f"\nSUCCESS! Goal '{goal_name}' proved at depth {current_depth} via Axiom/Tautology.")
                        env.theorems[goal_name] = clone_ast(goal)
                        return True
            print(f"Found {added_count} new axiom/tautology instances.")
            
            # Apply inference rules until fixed point
            print("Applying inference rules (Modus Ponens, QR1, QR2)...")
            added_new = True
            loop_counter = 0
            while added_new:
                loop_counter += 1
                added_new = False
                
                # MP
                mp_results = apply_modus_ponens(proven_theorems, limits)
                # QR
                qr_results = apply_qr_rules(proven_theorems, limits)
                
                for res in mp_results + qr_results:
                    if not any(is_structurally_equal(res, p) for p in proven_theorems):
                        proven_theorems.append(res)
                        limits.check_space(len(terms) + len(formulas) + len(proven_theorems))
                        added_new = True
                        if is_structurally_equal(res, goal):
                            print(f"\nSUCCESS! Goal '{goal_name}' proved at depth {current_depth} via Inference Rules.")
                            env.theorems[goal_name] = clone_ast(goal)
                            return True
                            
            print(f"Inference fixed point reached after {loop_counter} passes.")
            print(f"Total proven theorems in pool: {len(proven_theorems)}")
            current_depth += 1

    except SearchLimitExceeded as e:
        print(f"\nSearch stopped: {e}")
        return False


