from dataclasses import dataclass, field
from typing import List, Union, Optional
from enum import Enum

class FunctionType(Enum):
    PRE_DEFINED = "pre_defined"
    USER_DEFINED = "user_defined"
    SCHEMA = "schema"

class RelationType(Enum):
    PRE_DEFINED = "pre_defined"
    USER_DEFINED = "user_defined"
    SCHEMA = "schema"

from enum import Enum

class DefinitionType(Enum):
    PRE_DEFINED = "pre_defined"
    USER_DEFINED = "user_defined"
    SCHEMA = "schema"

@dataclass
class Node:
    """Base class for all Abstract Syntax Tree nodes."""
    name: str
    prefix_formatting: List['Node'] = field(default_factory=list, init=False)
    postfix_formatting: List['Node'] = field(default_factory=list, init=False)

    def is_structurally_equal(self, other: 'Node') -> bool:
        return is_structurally_equal(self, other)

@dataclass
class TermNode(Node):
    """Base class for term nodes."""
    pass

@dataclass
class FormulaNode(Node):
    """Base class for formula nodes (both First-Order and Propositional)."""
    pass

# ==========================================
# Term Nodes
# ==========================================

@dataclass
class Variable(TermNode):
    """Represents a standard FOL variable."""
    pass

@dataclass
class Function(TermNode):
    """Represents a function applied to arguments."""
    arity: int
    func_type: FunctionType
    arguments: List[TermNode] = field(default_factory=list)

@dataclass
class Relation(FormulaNode):
    """Represents a relation applied to arguments."""
    arity: int
    rel_type: RelationType
    arguments: List[TermNode] = field(default_factory=list)

@dataclass
class Constant(TermNode):
    """Represents a mathematical constant."""
    priority: int = 0
    pass



@dataclass
class DummyVariable(TermNode):
    """Acts as a placeholder for terms (used for term replacement)."""
    pass

from typing import Set

@dataclass
class TermPlaceholder(TermNode):
    """Placeholder for terms used in custom notation definitions (e.g. ?t1 or ?(v1)t1)."""
    index: int
    allowed_capture: Set[str] = field(default_factory=set)
    name: str = field(init=False)
    
    def __post_init__(self):
        if self.allowed_capture:
            v_names = ",".join(sorted(self.allowed_capture))
            self.name = f"?({v_names})t{self.index}"
        else:
            self.name = f"?t{self.index}"

@dataclass
class VariablePlaceholder(Variable):
    """Placeholder for variables used in custom notation definitions (e.g. ?v1)."""
    index: int
    name: str = field(init=False)
    
    def __post_init__(self):
        self.name = f"?v{self.index}"

@dataclass
class FormulaPlaceholder(FormulaNode):
    """Placeholder for formulas used in custom notation definitions (e.g. ?f1 or ?(v1)f1)."""
    index: int
    allowed_capture: Set[str] = field(default_factory=set)
    name: str = field(init=False)
    
    def __post_init__(self):
        if self.allowed_capture:
            v_names = ",".join(sorted(self.allowed_capture))
            self.name = f"?({v_names})f{self.index}"
        else:
            self.name = f"?f{self.index}"

from typing import Dict
@dataclass
class LongTerm(TermNode):
    """Represents a custom-defined long term with placeholders."""
    definition_name: str
    pattern: List[str] = field(default_factory=list)
    term_placeholders: Dict[str, Union[TermNode, List[TermNode]]] = field(default_factory=dict)
    var_placeholders: Dict[str, Union[Variable, List[Variable]]] = field(default_factory=dict)
    formula_placeholders: Dict[str, Union['FormulaNode', List['FormulaNode']]] = field(default_factory=dict)
    repetition_counts: Dict[int, int] = field(default_factory=dict)
    def_type: DefinitionType = DefinitionType.USER_DEFINED
    priority: int = 0
    name: str = field(init=False)
    
    def __post_init__(self):
        self.name = self.definition_name

# ==========================================
# Formula Nodes
# ==========================================

@dataclass
class Iota(TermNode):
    """Represents an Iota choice term (ι x Ψ(x))."""
    variable: Variable
    formula: 'FormulaNode'
    name: str = field(default="ι", init=False)

@dataclass
class Epsilon(TermNode):
    """Represents an Epsilon choice term (ε x Ψ(x))."""
    variable: Variable
    formula: 'FormulaNode'
    name: str = field(default="ε", init=False)

# ==========================================
# Formula Nodes
# ==========================================

@dataclass
class PropositionalVariable(FormulaNode):
    """Represents a boolean propositional variable."""
    pass



@dataclass
class FormulaConstant(FormulaNode):
    """Represents a formula macro."""
    name: str
    priority: int = 0

@dataclass
class Connective(FormulaNode):
    """Represents a logical connective (¬, ∧, ∨, ⇒, ⇔)."""
    arity: int
    arguments: List[FormulaNode] = field(default_factory=list)

    def __post_init__(self):
        if self.arity < 0:
            raise ValueError(f"Connective arity cannot be negative: {self.arity}")
        if len(self.arguments) != self.arity:
            raise ValueError(f"Connective '{self.name}' expects {self.arity} arguments, got {len(self.arguments)}.")

@dataclass
class Quantifier(FormulaNode):
    """Represents a logical quantifier (∀, ∃, ∃!)."""
    variable: Variable
    formula: FormulaNode

@dataclass
class LongFormula(FormulaNode):
    """Represents a custom-defined long formula with placeholders."""
    definition_name: str
    pattern: List[str] = field(default_factory=list)
    term_placeholders: Dict[str, Union[TermNode, List[TermNode]]] = field(default_factory=dict)
    var_placeholders: Dict[str, Union[Variable, List[Variable]]] = field(default_factory=dict)
    formula_placeholders: Dict[str, Union['FormulaNode', List['FormulaNode']]] = field(default_factory=dict)
    repetition_counts: Dict[int, int] = field(default_factory=dict)
    def_type: DefinitionType = DefinitionType.USER_DEFINED
    priority: int = 0
    name: str = field(init=False)
    
    def __post_init__(self):
        self.name = self.definition_name

@dataclass
class MetaVariable(FormulaNode):
    """Acts as a placeholder for 1st order formulae."""
    pass

# ==========================================
# Formatting Nodes
# ==========================================

@dataclass
class Bracket(Node):
    """Represents formatting brackets like '(' or ')'."""
    pass

@dataclass
class Whitespace(Node):
    """Represents whitespace used for formatting."""
    pass

def is_structurally_equal(n1: Node, n2: Node) -> bool:
    """Checks if two AST nodes are structurally identical, ignoring formatting (whitespace and brackets)."""
    if type(n1) != type(n2):
        return False
    if isinstance(n1, list):
        if len(n1) != len(n2):
            return False
        return all(is_structurally_equal(a1, a2) for a1, a2 in zip(n1, n2))
    if isinstance(n1, (Variable, DummyVariable, TermPlaceholder, FormulaPlaceholder, PropositionalVariable, MetaVariable)):
        return n1.name == n2.name
    elif isinstance(n1, Constant):
        return n1.name == n2.name
    elif isinstance(n1, Connective):
        if n1.name != n2.name or len(n1.arguments) != len(n2.arguments):
            return False
        return all(is_structurally_equal(a1, a2) for a1, a2 in zip(n1.arguments, n2.arguments))
    elif isinstance(n1, Quantifier):
        return n1.name == n2.name and n1.variable.name == n2.variable.name and is_structurally_equal(n1.formula, n2.formula)
    elif isinstance(n1, (Iota, Epsilon)):
        return n1.name == n2.name and n1.variable.name == n2.variable.name and is_structurally_equal(n1.formula, n2.formula)
    elif isinstance(n1, (LongTerm, LongFormula)):
        if n1.definition_name != n2.definition_name:
            return False
        if len(n1.term_placeholders) != len(n2.term_placeholders) or len(n1.var_placeholders) != len(n2.var_placeholders):
            return False
        if n1.formula_placeholders.keys() != n2.formula_placeholders.keys(): return False
        for k in n1.term_placeholders:
            if not is_structurally_equal(n1.term_placeholders[k], n2.term_placeholders[k]): return False
        for k in n1.var_placeholders:
            if not is_structurally_equal(n1.var_placeholders[k], n2.var_placeholders[k]): return False
        for k in n1.formula_placeholders:
            if not is_structurally_equal(n1.formula_placeholders[k], n2.formula_placeholders[k]): return False
        return True
    return n1.name == n2.name
