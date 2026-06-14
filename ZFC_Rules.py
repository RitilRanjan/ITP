from AST import Node, FormulaNode, Variable, Function, FunctionType, Relation, RelationType, Connective, Quantifier, DummyVariable, PropositionalVariable, MetaVariable, is_structurally_equal
from Environment import Environment
from Frontend import parse_fol_formula

def are_isomorphic(n1: Node, n2: Node) -> bool:
    """Checks if two AST nodes are structurally identical up to bijective variable renaming."""
    mapping12 = {}  # maps var name in n1 to var name in n2
    mapping21 = {}  # maps var name in n2 to var name in n1
    
    def match(p1, p2):
        if type(p1) != type(p2):
            return False
            
        if isinstance(p1, Variable):
            name1 = p1.name
            name2 = p2.name
            if name1 in mapping12:
                return mapping12[name1] == name2
            if name2 in mapping21:
                return mapping21[name2] == name1
            mapping12[name1] = name2
            mapping21[name2] = name1
            return True
            
        elif isinstance(p1, (Function, Relation, Connective)):
            if p1.name != p2.name or len(p1.arguments) != len(p2.arguments):
                return False
            for a1, a2 in zip(p1.arguments, p2.arguments):
                if not match(a1, a2):
                    return False
            return True
            
        elif isinstance(p1, Quantifier):
            if p1.name != p2.name:
                return False
            if not match(p1.variable, p2.variable):
                return False
            return match(p1.formula, p2.formula)
            
        # For formatting, dummy variables, etc.
        if p1.name != p2.name:
            return False
        return True
        
    return match(n1, n2)

def strip_universal_quantifiers(node: FormulaNode) -> FormulaNode:
    """Strips leading universal quantifiers from a formula to compare open and closed forms."""
    curr = node
    while isinstance(curr, Quantifier) and curr.name == "∀":
        curr = curr.formula
    return curr

# Helper environment to parse predefined templates
def get_parsing_env() -> Environment:
    env = Environment()
    for var_name in ["x", "y", "z", "w", "u", "v", "A", "B", "C", "D", "X", "E", "Y"]:
        env.add_variable(Variable(var_name))
    dummy = Variable("x")
    env.add_term(Function("S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
    env.add_formula(Relation("=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    env.add_formula(Relation("∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    return env

_env = get_parsing_env()

# Pre-parse ZFC Axiom templates at module load time
templates_extension = [
    parse_fol_formula("( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ x = y", _env),
    parse_fol_formula("( ∀ z ( z ∈ x ⇔ z ∈ y ) ) ⇒ y = x", _env),
    parse_fol_formula("( ∀ z ( z ∈ y ⇔ z ∈ x ) ) ⇒ x = y", _env),
    parse_fol_formula("( ∀ z ( z ∈ y ⇔ z ∈ x ) ) ⇒ y = x", _env)
]

templates_pairing = [
    parse_fol_formula("∃ z ∀ w ( w ∈ z ⇔ w = x ∨ w = y )", _env),
    parse_fol_formula("∃ z ∀ w ( w ∈ z ⇔ w = y ∨ w = x )", _env)
]

templates_union = [
    parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )", _env),
    parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ ∃ w ( w ∈ x ∧ z ∈ w ) )", _env)
]

template_power_set = parse_fol_formula("∃ y ∀ z ( z ∈ y ⇔ ∀ w ( w ∈ z ⇒ w ∈ x ) )", _env)

templates_regularity = [
    parse_fol_formula("∃ y ( y ∈ x ) ⇒ ∃ y ( y ∈ x ∧ ¬ ∃ z ( z ∈ y ∧ z ∈ x ) )", _env),
    parse_fol_formula("∃ y ( y ∈ x ) ⇒ ∃ y ( y ∈ x ∧ ¬ ∃ z ( z ∈ x ∧ z ∈ y ) )", _env),
    parse_fol_formula("∃ y ( y ∈ x ) ⇒ ∃ y ( y ∈ x ∧ ∀ z ( z ∈ y ⇒ ¬ ( z ∈ x ) ) )", _env),
    parse_fol_formula("∃ y ( y ∈ x ) ⇒ ∃ y ( y ∈ x ∧ ∀ z ( z ∈ x ⇒ ¬ ( z ∈ y ) ) )", _env)
]

templates_infinity = [
    parse_fol_formula("∃ X ( ∃ E ( E ∈ X ∧ ∀ z ( ¬ ( z ∈ E ) ) ) ∧ ∀ y ( y ∈ X ⇒ ∃ Y ( Y ∈ X ∧ ∀ z ( z ∈ Y ⇔ z ∈ y ∨ z = y ) ) ) )", _env),
    parse_fol_formula("∃ X ( ∃ E ( E ∈ X ∧ ∀ z ( ¬ ( z ∈ E ) ) ) ∧ ∀ y ( y ∈ X ⇒ ∃ Y ( Y ∈ X ∧ ∀ z ( z = y ∨ z ∈ y ) ) ) )", _env),
    parse_fol_formula("∃ X ( ∀ y ( y ∈ X ⇒ ∃ Y ( Y ∈ X ∧ ∀ z ( z ∈ Y ⇔ z ∈ y ∨ z = y ) ) ) ∧ ∃ E ( E ∈ X ∧ ∀ z ( ¬ ( z ∈ E ) ) ) )", _env),
    parse_fol_formula("∃ X ( ∀ y ( y ∈ X ⇒ ∃ Y ( Y ∈ X ∧ ∀ z ( z = y ∨ z ∈ y ) ) ) ∧ ∃ E ( E ∈ X ∧ ∀ z ( ¬ ( z ∈ E ) ) ) )", _env)
]

templates_choice = [
    parse_fol_formula(
        "∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ) ) ∧ ∀ y ∀ z ( y ∈ X ∧ z ∈ X ∧ ¬ ( y = z ) ⇒ ¬ ∃ w ( w ∈ y ∧ w ∈ z ) ) ⇒ ∃ C ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ∧ z ∈ C ∧ ∀ w ( w ∈ y ∧ w ∈ C ⇒ w = z ) ) )",
        _env
    ),
    parse_fol_formula(
        "∀ y ∀ z ( y ∈ X ∧ z ∈ X ∧ ¬ ( y = z ) ⇒ ¬ ∃ w ( w ∈ y ∧ w ∈ z ) ) ∧ ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ) ) ⇒ ∃ C ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ∧ z ∈ C ∧ ∀ w ( w ∈ y ∧ w ∈ C ⇒ w = z ) ) )",
        _env
    ),
    parse_fol_formula(
        "∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ) ) ∧ ∀ y ∀ z ( y ∈ X ∧ z ∈ X ∧ ¬ ( y = z ) ⇒ ¬ ∃ w ( w ∈ y ∧ w ∈ z ) ) ⇒ ∃ C ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ∧ z ∈ C ∧ ∀ w ( w ∈ C ∧ w ∈ y ⇒ w = z ) ) )",
        _env
    ),
    parse_fol_formula(
        "∀ y ∀ z ( y ∈ X ∧ z ∈ X ∧ ¬ ( y = z ) ⇒ ¬ ∃ w ( w ∈ y ∧ w ∈ z ) ) ∧ ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ) ) ⇒ ∃ C ∀ y ( y ∈ X ⇒ ∃ z ( z ∈ y ∧ z ∈ C ∧ ∀ w ( w ∈ C ∧ w ∈ y ⇒ w = z ) ) )",
        _env
    )
]

# Axiom Functions
def axiom_extension(formula: FormulaNode) -> bool:
    stripped = strip_universal_quantifiers(formula)
    return any(are_isomorphic(stripped, t) for t in templates_extension)

def axiom_pairing(formula: FormulaNode) -> bool:
    stripped = strip_universal_quantifiers(formula)
    return any(are_isomorphic(stripped, t) for t in templates_pairing)

def axiom_union(formula: FormulaNode) -> bool:
    stripped = strip_universal_quantifiers(formula)
    return any(are_isomorphic(stripped, t) for t in templates_union)

def axiom_power_set(formula: FormulaNode) -> bool:
    return are_isomorphic(strip_universal_quantifiers(formula), template_power_set)

def axiom_regularity(formula: FormulaNode) -> bool:
    stripped = strip_universal_quantifiers(formula)
    return any(are_isomorphic(stripped, t) for t in templates_regularity)

def axiom_infinity(formula: FormulaNode) -> bool:
    stripped = strip_universal_quantifiers(formula)
    return any(are_isomorphic(stripped, t) for t in templates_infinity)

def axiom_choice(formula: FormulaNode) -> bool:
    stripped = strip_universal_quantifiers(formula)
    return any(are_isomorphic(stripped, t) for t in templates_choice)

def axiom_specification(formula: FormulaNode) -> bool:
    node = strip_universal_quantifiers(formula)
    
    # Must be ∃y
    if not isinstance(node, Quantifier) or node.name != "∃":
        return False
    y = node.variable.name
    
    # Must be ∀z
    body = node.formula
    if not isinstance(body, Quantifier) or body.name != "∀":
        return False
    z = body.variable.name
    
    if y == z:
        return False
        
    # Must be ⇔
    scope = body.formula
    if not isinstance(scope, Connective) or scope.name != "⇔" or len(scope.arguments) != 2:
        return False
        
    left, right = scope.arguments[0], scope.arguments[1]
    
    # Check left: z ∈ y
    if not isinstance(left, Relation) or left.name != "∈" or len(left.arguments) != 2:
        return False
    if left.arguments[0].name != z or left.arguments[1].name != y:
        return False
        
    # Check right: z ∈ x ∧ phi
    if not isinstance(right, Connective) or right.name != "∧" or len(right.arguments) != 2:
        return False
        
    c1, c2 = right.arguments[0], right.arguments[1]
    if not isinstance(c1, Relation) or c1.name != "∈" or len(c1.arguments) != 2:
        return False
    if c1.arguments[0].name != z:
        return False
    x = c1.arguments[1].name
    
    if x == y or x == z:
        return False
        
    # y must not be free in c2 (phi)
    from SubstitutionManager import get_free
    free_vars_phi = get_free(c2)
    if y in free_vars_phi:
        return False
        
    return True

def axiom_replacement(formula: FormulaNode) -> bool:
    node = strip_universal_quantifiers(formula)
    
    # Must be ⇒
    if not isinstance(node, Connective) or node.name != "⇒" or len(node.arguments) != 2:
        return False
        
    ant, cons = node.arguments[0], node.arguments[1]
    
    # 1. Parse Consequent: ∃B ∀v (v ∈ B ⇔ ∃u (u ∈ A ∧ phi_uv))
    if not isinstance(cons, Quantifier) or cons.name != "∃":
        return False
    B = cons.variable.name
    
    body = cons.formula
    if not isinstance(body, Quantifier) or body.name != "∀":
        return False
    v = body.variable.name
    
    if B == v:
        return False
        
    scope = body.formula
    if not isinstance(scope, Connective) or scope.name != "⇔" or len(scope.arguments) != 2:
        return False
        
    left, right = scope.arguments[0], scope.arguments[1]
    
    # Check left: v ∈ B
    if not isinstance(left, Relation) or left.name != "∈" or len(left.arguments) != 2:
        return False
    if left.arguments[0].name != v or left.arguments[1].name != B:
        return False
        
    # Check right: ∃u (u ∈ A ∧ phi_uv)
    if not isinstance(right, Quantifier) or right.name != "∃":
        return False
    u = right.variable.name
    
    if u == B or u == v:
        return False
        
    r_body = right.formula
    if not isinstance(r_body, Connective) or r_body.name != "∧" or len(r_body.arguments) != 2:
        return False
        
    c1, phi_uv = r_body.arguments[0], r_body.arguments[1]
    
    # Check c1: u ∈ A
    if not isinstance(c1, Relation) or c1.name != "∈" or len(c1.arguments) != 2:
        return False
    if c1.arguments[0].name != u:
        return False
    A = c1.arguments[1].name
    
    if A == B or A == u or A == v:
        return False
        
    # B must not be free in phi_uv
    from SubstitutionManager import get_free
    if B in get_free(phi_uv):
        return False
        
    # 2. Parse Antecedent: ∀u ∀v ∀w (phi_uv ∧ phi_uw ⇒ v = w)
    ant_stripped = strip_universal_quantifiers(ant)
    
    # The core must be ⇒
    if not isinstance(ant_stripped, Connective) or ant_stripped.name != "⇒" or len(ant_stripped.arguments) != 2:
        return False
        
    ant_left, ant_right = ant_stripped.arguments[0], ant_stripped.arguments[1]
    
    # Check ant_right: v = w or w = v
    if not isinstance(ant_right, Relation) or ant_right.name != "=" or len(ant_right.arguments) != 2:
        return False
    arn1, arn2 = ant_right.arguments[0].name, ant_right.arguments[1].name
    
    if arn1 == v:
        w = arn2
    elif arn2 == v:
        w = arn1
    else:
        return False
        
    if w == u or w == v or w == B or w == A:
        return False
        
    # Check ant_left: phi_uv ∧ phi_uw
    if not isinstance(ant_left, Connective) or ant_left.name != "∧" or len(ant_left.arguments) != 2:
        return False
        
    p_uv, p_uw = ant_left.arguments[0], ant_left.arguments[1]
    
    # Check that p_uv matches phi_uv
    if not is_structurally_equal(p_uv, phi_uv):
        p_uw, p_uv = p_uv, p_uw
        if not is_structurally_equal(p_uv, phi_uv):
            return False
            
    # Check that p_uw is exactly phi_uv with v substituted by w
    from SubstitutionManager import substitute_free, clone_ast
    phi_cloned = clone_ast(phi_uv)
    phi_substituted = substitute_free(phi_cloned, v, Variable(w))
    
    if not is_structurally_equal(p_uw, phi_substituted):
        return False
        
    return True
