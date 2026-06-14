import json
import dataclasses
from enum import Enum
from collections import ChainMap
from AST import Node

class ASTEncoder(json.JSONEncoder):
    """Custom JSON encoder for AST dataclasses and Enums."""
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            # Convert dataclass to dict and inject its type name for clarity
            d = {"__type__": obj.__class__.__name__}
            d.update(dataclasses.asdict(obj))
            return d
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

class Environment:
    """Stores the state of the theorem prover."""
    def __init__(self, parent=None, goal_formula_name=None, target_proven_formula_name=None):
        self.parent = parent
        self.goal_formula_name = goal_formula_name
        self.target_proven_formula_name = target_proven_formula_name
        
        self.local_variables = {}
        self.local_dummy_variables = {}
        self.local_meta_variables = {}
        self.local_terms = {}
        self.local_propositional_variables = {}
        self.local_formulae = {}
        self.local_theorems = {}
        self.local_user_functions = {}
        self.local_user_relations = {}
        
        if parent is not None:
            self.variables = ChainMap(self.local_variables, parent.variables)
            self.dummy_variables = ChainMap(self.local_dummy_variables, parent.dummy_variables)
            self.meta_variables = ChainMap(self.local_meta_variables, parent.meta_variables)
            self.terms = ChainMap(self.local_terms, parent.terms)
            self.propositional_variables = ChainMap(self.local_propositional_variables, parent.propositional_variables)
            self.formulae = ChainMap(self.local_formulae, parent.formulae)
            self.theorems = ChainMap(self.local_theorems, parent.theorems)
            self.user_functions = ChainMap(self.local_user_functions, parent.user_functions)
            self.user_relations = ChainMap(self.local_user_relations, parent.user_relations)
        else:
            self.variables = ChainMap(self.local_variables)
            self.dummy_variables = ChainMap(self.local_dummy_variables)
            self.meta_variables = ChainMap(self.local_meta_variables)
            self.terms = ChainMap(self.local_terms)
            self.propositional_variables = ChainMap(self.local_propositional_variables)
            self.formulae = ChainMap(self.local_formulae)
            self.theorems = ChainMap(self.local_theorems)
            self.user_functions = ChainMap(self.local_user_functions)
            self.user_relations = ChainMap(self.local_user_relations)

    def add_variable(self, node):
        self.local_variables[node.name] = node

    def add_dummy_variable(self, node):
        self.local_dummy_variables[node.name] = node

    def add_meta_variable(self, node):
        self.local_meta_variables[node.name] = node

    def add_term(self, node):
        self.local_terms[node.name] = node

    def add_propositional_variable(self, node):
        self.local_propositional_variables[node.name] = node

    def add_formula(self, node):
        self.local_formulae[node.name] = node

    def add_theorem(self, node):
        self.local_theorems[node.name] = node

    def remove_theorem(self, name: str):
        if name in self.local_theorems:
            del self.local_theorems[name]

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
            "user_functions": dict(self.user_functions),
            "user_relations": dict(self.user_relations),
        }
        return json.dumps(state, cls=ASTEncoder, indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        # Deserialization can be implemented later as needed when we load from files.
        pass
