from dataclasses import dataclass, field
from typing import List
from enum import Enum

class FunctionType(Enum):
    PRE_DEFINED = "pre_defined"
    USER_DEFINED = "user_defined"
    IOTA_DEFINED = "iota_defined"

class RelationType(Enum):
    PRE_DEFINED = "pre_defined"
    USER_DEFINED = "user_defined"

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
    """Represents an FOL function."""
    arity: int
    func_type: FunctionType = FunctionType.USER_DEFINED
    arguments: List[TermNode] = field(default_factory=list)

    def __post_init__(self):
        if self.arity < 0:
            raise ValueError(f"Function arity cannot be negative: {self.arity}")
        if len(self.arguments) != self.arity:
            raise ValueError(f"Function '{self.name}' expects {self.arity} arguments, got {len(self.arguments)}.")

@dataclass
class DummyVariable(TermNode):
    """Acts as a placeholder for terms (used for term replacement)."""
    pass

# ==========================================
# Formula Nodes
# ==========================================

@dataclass
class PropositionalVariable(FormulaNode):
    """Represents a boolean propositional variable."""
    pass

@dataclass
class Relation(FormulaNode):
    """Represents an FOL predicate/relation."""
    arity: int
    rel_type: RelationType = RelationType.USER_DEFINED
    arguments: List[TermNode] = field(default_factory=list)

    def __post_init__(self):
        if self.arity < 0:
            raise ValueError(f"Relation arity cannot be negative: {self.arity}")
        if len(self.arguments) != self.arity:
            raise ValueError(f"Relation '{self.name}' expects {self.arity} arguments, got {len(self.arguments)}.")

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
    if isinstance(n1, (Variable, DummyVariable, PropositionalVariable, MetaVariable)):
        return n1.name == n2.name
    elif isinstance(n1, (Function, Relation, Connective)):
        if n1.name != n2.name or len(n1.arguments) != len(n2.arguments):
            return False
        return all(is_structurally_equal(a1, a2) for a1, a2 in zip(n1.arguments, n2.arguments))
    elif isinstance(n1, Quantifier):
        return (n1.name == n2.name and
                is_structurally_equal(n1.variable, n2.variable) and
                is_structurally_equal(n1.formula, n2.formula))
    return n1.name == n2.name
