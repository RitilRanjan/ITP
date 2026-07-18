import json
import dataclasses
from enum import Enum
from collections import ChainMap
from dataclasses import dataclass
from typing import Dict, Optional, Any, Tuple, TypeVar, Type

from backend.AST import (
    Node, Variable, DummyVariable, MetaVariable, TermNode,
    PropositionalVariable, FormulaNode, Connective,
    Quantifier, Constant, DefinitionType,
    LongTerm, LongFormula, TermPlaceholder, VariablePlaceholder
)

@dataclass
class LongDefinition:
    """Stores the parsed definition pattern and underlying AST for custom notations."""
    name: str
    pattern: list[str]  # e.g., ["add_2", "?t1"]
    definition_tokens: list[str]
    def_type: DefinitionType = DefinitionType.USER_DEFINED
    priority: int = 0

class ASTEncoder(json.JSONEncoder):
    """Custom JSON encoder for AST dataclasses and Enums."""
    def default(self, obj: Any) -> Any:
        if dataclasses.is_dataclass(obj):
            # Convert dataclass to dict and inject its type name for clarity
            d = {"__type__": obj.__class__.__name__}
            d.update(dataclasses.asdict(obj))
            return d
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

import collections.abc

class TheoremSetMap(collections.abc.MutableMapping):
    """A dictionary-like view that stores theorem names and yields pointers to env.formulae."""
    def __init__(self, env: 'Environment'):
        self.env = env

    def __getitem__(self, key: str) -> FormulaNode:
        if key in self.env.local_theorems:
            return self.env.formulae[key]
        if self.env.parent is not None and key in self.env.parent.theorems:
            return self.env.parent.theorems[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: FormulaNode) -> None:
        self.env.local_theorems.add(key)
        if key not in self.env.local_formulae:
            self.env.local_formulae[key] = value

    def __delitem__(self, key: str) -> None:
        self.env.remove_theorem(key)

    def __iter__(self):
        seen = set()
        curr = self.env
        while curr is not None:
            for k in curr.local_theorems:
                if k not in seen:
                    seen.add(k)
                    yield k
            curr = curr.parent

    def __len__(self):
        return sum(1 for _ in self)

class Environment:
    """Stores the state of the theorem prover."""
    def __init__(
        self,
        parent: Optional['Environment'] = None,
        goal_formula_name: Optional[str] = None,
        target_proven_formula_name: Optional[str] = None,
        theory: str = "ZFC"
    ) -> None:
        self.parent: Optional['Environment'] = parent
        self.goal_formula_name: Optional[str] = goal_formula_name
        # Tracks the original mission goal name before any left/right/and reduction
        self.original_goal_formula_name: Optional[str] = goal_formula_name
        self.target_proven_formula_name: Optional[str] = target_proven_formula_name
        # Tracks the right-hand sub-goal name when goal was split by 'and' command
        self.and_right_formula_name: Optional[str] = None
        self.iff_right_formula_name: Optional[str] = None
        self.theory: str = theory if parent is None else parent.theory
        self.target_goal = None
        
        self.local_variables: Dict[str, Variable] = {}
        self.local_dummy_variables: Dict[str, DummyVariable] = {}
        self.local_meta_variables: Dict[str, MetaVariable] = {}
        self.local_terms: Dict[str, TermNode] = {}
        self.local_propositional_variables: Dict[str, PropositionalVariable] = {}
        self.local_formulae: Dict[str, FormulaNode] = {}
        self.local_theorems: set = set()
        
        # Long Definitions store LongDefinition instances
        self.local_long_terms: Dict[str, LongDefinition] = {}
        self.local_long_formulae: Dict[str, LongDefinition] = {}
        
        self.local_free_vars_cache: Dict[str, set[str]] = {}
        
        if parent is not None:
            self.variables: ChainMap[str, Variable] = ChainMap(self.local_variables, parent.variables)
            self.dummy_variables: ChainMap[str, DummyVariable] = ChainMap(self.local_dummy_variables, parent.dummy_variables)
            self.meta_variables: ChainMap[str, MetaVariable] = ChainMap(self.local_meta_variables, parent.meta_variables)
            self.terms: ChainMap[str, TermNode] = ChainMap(self.local_terms, parent.terms)
            self.propositional_variables: ChainMap[str, PropositionalVariable] = ChainMap(self.local_propositional_variables, parent.propositional_variables)
            self.formulae: ChainMap[str, FormulaNode] = ChainMap(self.local_formulae, parent.formulae)
            self.theorems = TheoremSetMap(self)
            self.long_terms: ChainMap[str, LongDefinition] = ChainMap(self.local_long_terms, parent.long_terms)
            self.long_formulae: ChainMap[str, LongDefinition] = ChainMap(self.local_long_formulae, parent.long_formulae)
            self.free_vars_cache: ChainMap[str, set[str]] = ChainMap(self.local_free_vars_cache, parent.free_vars_cache)
        else:
            self.variables = ChainMap(self.local_variables)
            self.dummy_variables = ChainMap(self.local_dummy_variables)
            self.meta_variables = ChainMap(self.local_meta_variables)
            self.terms = ChainMap(self.local_terms)
            self.propositional_variables = ChainMap(self.local_propositional_variables)
            self.formulae = ChainMap(self.local_formulae)
            self.theorems = TheoremSetMap(self)
            self.long_terms = ChainMap(self.local_long_terms)
            self.long_formulae = ChainMap(self.local_long_formulae)
            self.free_vars_cache = ChainMap(self.local_free_vars_cache)
            self.local_long_formulae["="] = LongDefinition(name="=", pattern=["?t1", "=", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            
            if self.theory == "ZFC":
                self.local_long_formulae["∈"] = LongDefinition(name="∈", pattern=["?t1", "∈", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            elif self.theory == "NT":
                self.local_terms["0"] = Constant("0")
                self.local_long_terms["S"] = LongDefinition(name="S", pattern=["S", "?t1"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
                self.local_long_terms["+"] = LongDefinition(name="+", pattern=["?t1", "+", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
                self.local_long_terms["*"] = LongDefinition(name="*", pattern=["?t1", "*", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
                self.local_long_terms["^"] = LongDefinition(name="^", pattern=["?t1", "^", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)

    def add_variable(self, node: Variable) -> None:
        self.local_variables[node.name] = node

    def add_dummy_variable(self, node: DummyVariable) -> None:
        self.local_dummy_variables[node.name] = node

    def add_meta_variable(self, node: MetaVariable) -> None:
        self.local_meta_variables[node.name] = node

    def add_term(self, node: TermNode) -> None:
        self.local_terms[node.name] = node
        from backend.SubstitutionManager import compute_free_variables
        self.local_free_vars_cache[node.name] = compute_free_variables(node, self)

    def add_propositional_variable(self, node: PropositionalVariable) -> None:
        self.local_propositional_variables[node.name] = node

    def add_formula(self, node: FormulaNode) -> None:
        self.local_formulae[node.name] = node
        from backend.SubstitutionManager import compute_free_variables
        self.local_free_vars_cache[node.name] = compute_free_variables(node, self)

    def add_theorem(self, name: str) -> None:
        self.local_theorems.add(name)

    def remove_theorem(self, name: str) -> None:
        curr = self
        while curr is not None:
            if name in curr.local_theorems:
                curr.local_theorems.remove(name)
                return
            curr = curr.parent

    def to_json(self) -> str:
        """Serializes the entire environment state to a JSON string."""
        state = {
            "variables": dict(self.variables),
            "dummy_variables": dict(self.dummy_variables),
            "meta_variables": dict(self.meta_variables),
            "terms": dict(self.terms),
            "propositional_variables": dict(self.propositional_variables),
            "formulae": dict(self.formulae),
            "theorems": dict(self.theorems),
            "long_terms": {k: dataclasses.asdict(v) for k, v in dict(self.long_terms).items()},
            "long_formulae": {k: dataclasses.asdict(v) for k, v in dict(self.long_formulae).items()},
        }
        return json.dumps(state, cls=ASTEncoder, indent=4)

    @classmethod
    def from_json(cls, json_str: str) -> None:
        # Deserialization can be implemented later as needed when we load from files.
        pass
