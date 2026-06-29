from Environment import Environment
from CommandHandlers.CommandRegistry import registry
from AST import Variable, PropositionalVariable, DummyVariable, Function, Relation
from Frontend import lex
import re
from typing import List

class AutocompleteEngine:
    def __init__(self):
        pass

    def get_suggestions(self, partial_command: str, env: Environment) -> List[str]:
        """
        Given the partial command string typed by the user, return a list of suggested strings.
        If the command is invalid, return ["ERROR: INVALID REPL COMMAND"].
        """
        tokens = partial_command.lstrip().split(" ")
        
        # Exclude save/load commands from web autocomplete as they have GUI equivalents
        excluded_cmds = {"save", "load", "save_h", "load_h"}
        
        # If there's only 1 token, the user is typing the command name
        if len(tokens) == 1:
            cmd_prefix = tokens[0]
            all_cmds = [cmd for cmd in registry.handlers.keys() if cmd not in excluded_cmds]
            suggestions = [cmd for cmd in all_cmds if cmd.startswith(cmd_prefix)]
            if not suggestions and cmd_prefix:
                return ["ERROR: INVALID REPL COMMAND"]
            return suggestions
            
        cmd_name = tokens[0]
        if not registry.is_registered(cmd_name) or cmd_name in excluded_cmds:
            return ["ERROR: INVALID REPL COMMAND"]
            
        # The user is typing arguments
        # Find which argument position we are at
        # tokens[1] is arg 1, tokens[2] is arg 2, etc.
        # But split(" ") keeps empty strings if there's trailing whitespace.
        # e.g. "fold " -> tokens=["fold", ""] -> len 2 -> typing arg 1
        arg_index = len(tokens) - 1 
        current_token = tokens[-1]
        # Helper to get pure formula names (excluding relation declarations like =, ∈)
        formula_names = [name for name, node in env.local_formulae.items() if not (isinstance(node, Relation) and node.name == name)]

        # Handlers map to argument suggestions
        if cmd_name == "fold":
            # fold <sym> [occ] [<target>] [<out>] [<equiv>]
            if arg_index == 1:
                options = ["∀", "∃", "∃!", "ε", "ι", "{", "all"] + list(env.user_functions.keys()) + list(env.user_relations.keys())
                return [opt for opt in options if opt.startswith(current_token)]
            elif arg_index == 2:
                return [] # occ
            elif arg_index == 3:
                return [opt for opt in formula_names if opt.startswith(current_token)]
            else:
                return []
                
        elif cmd_name in ["st", "sf", "sb", "sa", "sp"]:
            # e.g. st <var> <term> [occ] [<target>] [<out>]
            if arg_index == 1:
                # suggest variables
                if cmd_name == "sp":
                    options = list(env.propositional_variables)
                else:
                    options = list(env.variables)
                return [opt for opt in options if opt.startswith(current_token)]
            elif arg_index == 2:
                return [] # typing term/formula definition, handled in grammar predictor
            elif arg_index == 3:
                return [] # occ
            elif arg_index == 4:
                return [opt for opt in formula_names if opt.startswith(current_token)]
            else:
                return []
                
        elif cmd_name in ["apply", "simp_l_eq", "simp_r_eq", "simp_l_bi", "simp_r_bi"]:
            # apply [<target>] <axiom_or_theorem>
            # For simplicity, if arg 1 is not a formula, it might be the theorem. We suggest both.
            options = formula_names + ["E1", "E2", "E3", "Q1", "Q2", "QR1", "QR2", "PC1", "PC2", "PC3"]
            return [opt for opt in options if opt.startswith(current_token)]
            
        elif cmd_name in ["left", "right", "and", "imply", "intro", "neg-", "neg+", "dt"]:
            # target is arg 1 or implied
            options = formula_names
            return [opt for opt in options if opt.startswith(current_token)]
            
        elif cmd_name in ["cf", "ct", "cp", "mission", "def_f", "def_r", "auto", "search", "backward_search", "advanced_search"]:
            # Mathematical grammar prediction
            # cf <name> <formula>
            if cmd_name in ["cf", "ct", "cp"] and arg_index == 1:
                return [] # naming the new object
            if cmd_name in ["def_f", "def_r"] and arg_index in [1, 2]:
                return [] # name and arity
                
            # We are typing the formula/term.
            # Concatenate the mathematical part
            if cmd_name in ["cf", "ct", "cp"]:
                math_expr = " ".join(tokens[2:])
            elif cmd_name in ["def_f", "def_r"]:
                math_expr = " ".join(tokens[3:])
            else: # mission, auto, search, backward_search, advanced_search
                math_expr = " ".join(tokens[1:])
                
            return self._predict_grammar(math_expr, env, current_token)
            
        else:
            return []

    def _predict_grammar(self, expr: str, env: Environment, current_token: str) -> List[str]:
        """Predicts the next valid tokens based on partial mathematical expression."""
        try:
            tokens = lex(expr)
        except Exception:
            return []
            
        options = []
        
        vars_names = list(env.variables) + list(env.dummy_variables) + list(env.meta_variables)
        func_names = list(env.terms.keys())
        rel_names = list(env.formulae.keys())
        prop_vars = list(env.propositional_variables)
        
        # If empty expression or ends with operator, we expect a variable, function, relation, or '('
        if not tokens or tokens[-1] in ["∀", "∃", "∃!", "(", "+", "*", "=", "<", "∨", "∧", "⇒", "⇔", "¬", ","]:
            last_tok = tokens[-1] if tokens else ""
            if last_tok in ["∀", "∃", "∃!"]:
                options = vars_names
            elif last_tok in ["¬", "∨", "∧", "⇒", "⇔"]:
                options = rel_names + prop_vars + ["("]
            else:
                options = vars_names + func_names + rel_names + prop_vars + ["(", "¬", "∀", "∃"]
        else:
            # Last token was an operand or right paren, expect an operator
            options = ["+", "*", "=", "<", "∨", "∧", "⇒", "⇔", ")", ","]
            
        return [opt for opt in options if opt.startswith(current_token)]

autocomplete_engine = AutocompleteEngine()
