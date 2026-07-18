import re
from typing import List, Optional, Any
from backend.AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, 
    PropositionalVariable,  Connective, Quantifier, MetaVariable,
    Bracket, Whitespace, Iota, Epsilon, Constant, LongTerm, LongFormula,
    TermPlaceholder, VariablePlaceholder, FormulaPlaceholder
)
from backend.Environment import Environment

class UnrecognizedSymbolError(Exception): pass
class ParserError(Exception): pass

LOGICAL_CONNECTIVES = {"¬", "∧", "∨", "⇒", "⇔"}
QUANTIFIERS = {"∀", "∃", "∃!"}

def lex(input_str: str) -> List[str]:
    """Tokenize the input string into a flat list of strings, preserving whitespaces, brackets, and logical symbols."""
    pattern = r'(⇔|⇒|∃!|ε|ι|\?\([\w,]+\)[tf]\d+|\?\(|\)r\d+|\s+|[\?\w]+|[^\s\?\w])'
    tokens = re.split(pattern, input_str)
    return [t for t in tokens if t]

class Parser:
    def __init__(self, env: Environment):
        self.env = env
        self.tokens = []
        self.pos = 0
        
        self.prefix_patterns = []
        self.infix_patterns = []
        
        for name, long_def in env.long_terms.items():
            if len(long_def.pattern) == 0: continue
            prio = getattr(long_def, "priority", 0)
            if long_def.pattern[0].startswith('?'):
                self.infix_patterns.append((long_def.pattern, name, "term", prio))
            else:
                self.prefix_patterns.append((long_def.pattern, name, "term", prio))
                
        for name, long_def in env.long_formulae.items():
            if len(long_def.pattern) == 0: continue
            prio = getattr(long_def, "priority", 0)
            if long_def.pattern[0].startswith('?'):
                self.infix_patterns.append((long_def.pattern, name, "formula", prio))
            else:
                self.prefix_patterns.append((long_def.pattern, name, "formula", prio))

        for name, term_def in env.terms.items():
            prio = getattr(term_def, "priority", 0)
            self.prefix_patterns.append(([name], name, "term_short", prio))

        for name, form_def in env.formulae.items():
            prio = getattr(form_def, "priority", 0)
            self.prefix_patterns.append(([name], name, "formula_short", prio))
                
        # Sort by priority descending, then length descending
        self.prefix_patterns.sort(key=lambda x: (x[3], len(x[0])), reverse=True)
        self.infix_patterns.sort(key=lambda x: (x[3], len(x[0])), reverse=True)

    def parse(self, input_data, target: str):
        if isinstance(input_data, str):
            self.tokens = lex(input_data)
        else:
            self.tokens = input_data
        self.pos = 0
        
        prefix = self.consume_formatting()
        
        if self.pos >= len(self.tokens):
            raise ParserError("Empty input")
            
        node = self.parse_expr(0, target)
        
        postfix = self.consume_formatting()
        
        if self.pos < len(self.tokens):
            raise ParserError(f"Unexpected trailing tokens at position {self.pos}: '{self.tokens[self.pos]}'")
            
        node.prefix_formatting = prefix + node.prefix_formatting
        node.postfix_formatting = node.postfix_formatting + postfix
        
        return node

    def peek(self) -> Optional[str]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> str:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def consume_formatting(self):
        fmt = []
        while True:
            t = self.peek()
            if not t or not isinstance(t, str):
                break
            if t.isspace():
                fmt.append(Whitespace(name=t))
                self.consume()
            else:
                break
        return fmt

    def get_precedence(self, op) -> int:
        if not isinstance(op, str): return 0
        if op in ("⇔",): return 10
        if op in ("⇒",): return 20
        if op in ("∨",): return 30
        if op in ("∧",): return 40
        if op in ("=", "∈") or (op in self.env.long_formulae and len(self.env.long_formulae[op].pattern) == 3 and self.env.long_formulae[op].pattern[1] == op):
            return 50
        if op == "+": return 60
        if op == "*": return 70
        if op == "^": return 80
        if op in self.env.long_terms and len(self.env.long_terms[op].pattern) == 3 and self.env.long_terms[op].pattern[1] == op:
            return 60
        return 0

    def try_match_pattern(self, pattern: list[str], expected_target: str, name: str, left_node: 'Optional[Node]' = None) -> 'Optional[Node]':
        from backend.MacroExpander import parse_pattern_structure
        saved_pos = self.pos
        term_args = {}
        var_args = {}
        formula_args = {}
        
        pattern_struct = parse_pattern_structure(pattern)
        
        def match_element(el, current_pos, is_first=False):
            if current_pos >= len(self.tokens): return None
            
            # if we have a left_node and we are at the first element, it matches the left node
            if is_first and left_node is not None:
                if (el.startswith('?t') or el.startswith('?u')) and isinstance(left_node, TermNode):
                    if el.startswith('?u') and isinstance(left_node, Variable):
                        return None
                    return (current_pos, el, left_node)
                elif el.startswith('?v') and isinstance(left_node, Variable):
                    return (current_pos, el, left_node)
                else:
                    return None
            
            if el.startswith('?'):
                try:
                    # We must save pos, set it to current_pos to use parse_expr
                    old_pos = self.pos
                    self.pos = current_pos
                    
                    if el.startswith('?t'):
                        arg = self.parse_expr(0, "term")
                        ret_pos = self.pos
                        self.pos = old_pos
                        return (ret_pos, el, arg)
                    elif el.startswith('?u'):
                        arg = self.parse_expr(0, "term")
                        
                        if isinstance(arg, Variable):
                            self.pos = old_pos
                            return None
                        ret_pos = self.pos
                        self.pos = old_pos
                        return (ret_pos, el, arg)
                    elif el.startswith('?u'):
                        arg = self.parse_expr(0, "term")
                        
                        if isinstance(arg, Variable):
                            self.pos = old_pos
                            return None
                        ret_pos = self.pos
                        self.pos = old_pos
                        return (ret_pos, el, arg)
                    elif el.startswith('?v'):
                        arg_str = self.peek()
                        if not arg_str or arg_str not in self.env.variables:
                            self.pos = old_pos; return None
                        self.consume()
                        var_node = Variable(arg_str)
                        var_node.postfix_formatting = self.consume_formatting()
                        ret_pos = self.pos
                        self.pos = old_pos
                        return (ret_pos, el, var_node)
                    elif el.startswith('?f'):
                        arg = self.parse_expr(0, "fol")
                        ret_pos = self.pos
                        self.pos = old_pos
                        return (ret_pos, el, arg)
                    else:
                        self.pos = old_pos
                        return None
                except Exception:
                    self.pos = old_pos
                    return None
            else:
                if self.tokens[current_pos] != el:
                    return None
                # Check formatting
                old_pos = self.pos
                self.pos = current_pos + 1
                self.consume_formatting()
                ret_pos = self.pos
                self.pos = old_pos
                return (ret_pos, None, None)
                
        def backtrack(pat_idx, current_pos, current_term_args, current_var_args, current_formula_args, current_rep_counts):
            if pat_idx == len(pattern_struct):
                return current_pos, current_term_args, current_var_args, current_formula_args, current_rep_counts
                
            p = pattern_struct[pat_idx]
            
            if isinstance(p, tuple) and p[0] == 'rep':
                _, scope, rep_idx = p
                
                def match_scope_sequence(seq_pos, iteration):
                    temp_pos = seq_pos
                    temp_term, temp_var, temp_form = {}, {}, {}
                    for sp in scope:
                        res = match_element(sp, temp_pos)
                        if not res: return None
                        temp_pos, arg_name, arg_val = res
                        if arg_name:
                            
                            if arg_name.startswith('?u') and isinstance(arg_val, (Variable, DummyVariable)): return None
                            if arg_name.startswith('?t') or arg_name.startswith('?u'): temp_term[arg_name] = arg_val
                            elif arg_name.startswith('?v'): temp_var[arg_name] = arg_val
                            elif arg_name.startswith('?f'): temp_form[arg_name] = arg_val
                    return temp_pos, temp_term, temp_var, temp_form
                
                possible_states = [(current_pos, [], [], [], 0)]
                curr_state = possible_states[0]
                while True:
                    res = match_scope_sequence(curr_state[0], curr_state[4])
                    if not res: break
                    next_pos, temp_t, temp_v, temp_f = res
                    curr_state = (next_pos, curr_state[1] + [temp_t], curr_state[2] + [temp_v], curr_state[3] + [temp_f], curr_state[4] + 1)
                    possible_states.append(curr_state)
                
                for state in reversed(possible_states):
                    state_pos, list_t, list_v, list_f, count = state
                    
                    new_term = {k: list(v) if isinstance(v, list) else v for k, v in current_term_args.items()}
                    new_var = {k: list(v) if isinstance(v, list) else v for k, v in current_var_args.items()}
                    new_form = {k: list(v) if isinstance(v, list) else v for k, v in current_formula_args.items()}
                    
                    for temp_t in list_t:
                        for k, v in temp_t.items():
                            if k not in new_term: new_term[k] = []
                            new_term[k].append(v)
                    for temp_v in list_v:
                        for k, v in temp_v.items():
                            if k not in new_var: new_var[k] = []
                            new_var[k].append(v)
                    for temp_f in list_f:
                        for k, v in temp_f.items():
                            if k not in new_form: new_form[k] = []
                            new_form[k].append(v)
                            
                    new_counts = current_rep_counts.copy()
                    new_counts[rep_idx] = count
                    
                    res = backtrack(pat_idx + 1, state_pos, new_term, new_var, new_form, new_counts)
                    if res: return res
                return None
            else:
                res = match_element(p, current_pos, is_first=(pat_idx == 0))
                if not res: return None
                next_pos, arg_name, arg_val = res
                new_term = {k: list(v) if isinstance(v, list) else v for k, v in current_term_args.items()}
                new_var = {k: list(v) if isinstance(v, list) else v for k, v in current_var_args.items()}
                new_form = {k: list(v) if isinstance(v, list) else v for k, v in current_formula_args.items()}
                if arg_name:
                    
                    if arg_name.startswith('?u') and isinstance(arg_val, (Variable, DummyVariable)): return None
                    if arg_name.startswith('?t') or arg_name.startswith('?u'): new_term[arg_name] = arg_val
                    elif arg_name.startswith('?v'): new_var[arg_name] = arg_val
                    elif arg_name.startswith('?f'): new_form[arg_name] = arg_val
                return backtrack(pat_idx + 1, next_pos, new_term, new_var, new_form, current_rep_counts)
                
        res = backtrack(0, saved_pos, {}, {}, {}, {})
        if res is None:
            self.pos = saved_pos
            return None
            
        final_pos, final_term, final_var, final_form, final_counts = res
        self.pos = final_pos
        
        from backend.AST import LongTerm, LongFormula, Constant, Variable, DummyVariable, FormulaConstant, PropositionalVariable
        if expected_target == "term":
            return LongTerm(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern)
        elif expected_target == "term_short":
            if name in self.env.variables:
                return Variable(name=name)
            elif name in self.env.dummy_variables:
                return DummyVariable(name=name)
            return Constant(name=name)
        elif expected_target == "formula_short":
            return FormulaConstant(name=name)
        elif expected_target == "prop_short":
            return PropositionalVariable(name=name)
        else:
            return LongFormula(definition_name=name, term_placeholders=final_term, var_placeholders=final_var, formula_placeholders=final_form, repetition_counts=final_counts, pattern=pattern)

    def parse_expr(self, min_prec: int, target: str) -> Node:
        prefix_fmt = self.consume_formatting()
        
        t = self.peek()
        if not t:
            raise ParserError("Unexpected end of input")
            
        left = self.parse_prefix(target)
        left.prefix_formatting = prefix_fmt + left.prefix_formatting

        # Parse infix operators
        while True:
            post_left_fmt = self.consume_formatting()
            
            # Try infix long patterns first
            matched_infix = False
            for pat, name, target_ns, _ in self.infix_patterns:
                res = self.try_match_pattern(pat, target_ns, name, left_node=left)
                if res is not None:
                    res.prefix_formatting = prefix_fmt + res.prefix_formatting
                    left = res
                    matched_infix = True
                    break
                    
            if matched_infix:
                continue

            op = self.peek()
            if not op:
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            prec = self.get_precedence(op)
            if prec < min_prec or prec == 0:
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            if target == "term" and (op in ("=", "∈") or op in self.env.long_formulae or op in LOGICAL_CONNECTIVES):
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            self.consume() # consume operator
            op_fmt = self.consume_formatting()
            
            # Determine correct target type for the right-hand side
            if op in LOGICAL_CONNECTIVES:
                right_target = target
            elif op in ("=", "∈") or (op in self.env.long_formulae):
                right_target = "term"
            elif op in ("+", "*", "^") or (op in self.env.long_terms):
                right_target = "term"
            else:
                raise ParserError(f"Unknown binary operator '{op}'")
            
            right = self.parse_expr(prec + 1, right_target) # +1 for left-associativity
            right.prefix_formatting = op_fmt + right.prefix_formatting
            left.postfix_formatting = left.postfix_formatting + post_left_fmt
            
            # Build the node based on op with strict type assertions
            if op in LOGICAL_CONNECTIVES:
                if target == "term": break
                if not isinstance(left, FormulaNode):
                    raise ParserError(f"Left operand of connective '{op}' must be a formula, got term.")
                if not isinstance(right, FormulaNode):
                    raise ParserError(f"Right operand of connective '{op}' must be a formula, got term.")
                left = Connective(name=op, arity=2, arguments=[left, right])
            elif op in ("=", "∈") or (op in self.env.long_formulae):
                if not isinstance(left, TermNode):
                    raise ParserError(f"Left operand of relation '{op}' must be a term, got formula.")
                if not isinstance(right, TermNode):
                    raise ParserError(f"Right operand of relation '{op}' must be a term, got formula.")
                
                if op == "∈": op_name = "∈"
                else: op_name = op
                
                lf_def = self.env.long_formulae[op_name]
                left = LongFormula(definition_name=op_name, term_placeholders={"?t1": left, "?t2": right}, def_type=lf_def.def_type, pattern=lf_def.pattern)
            elif op in ("+", "*", "^") or (op in self.env.long_terms):
                if not isinstance(left, TermNode):
                    raise ParserError(f"Left operand of function '{op}' must be a term, got formula.")
                if not isinstance(right, TermNode):
                    raise ParserError(f"Right operand of function '{op}' must be a term, got formula.")
                
                lt_def = self.env.long_terms[op]
                left = LongTerm(definition_name=op, term_placeholders={"?t1": left, "?t2": right}, def_type=lt_def.def_type, pattern=lt_def.pattern)
            else:
                raise ParserError(f"Unknown binary operator '{op}'")

        # Validation: check if we successfully parsed the correct target type
        
        if target == "term" and not isinstance(left, TermNode):
            raise ParserError("Expected a term, but parsed a formula.")
        elif target in ("fol", "prop") and not isinstance(left, FormulaNode):
            # However, if we just parsed a term, we expect a relation to make it a formula.
            # E.g. input is just "x".
            raise ParserError("Expected a formula, but parsed a term.")
            
        return left

    def parse_prefix(self, target: str) -> Node:
        # Try prefix long patterns first
        for pat, name, target_ns, _ in self.prefix_patterns:
            res = self.try_match_pattern(pat, target_ns, name, left_node=None)
            if res is not None:
                return res

        t = self.peek()
        
        # Handle Brackets
        if t == '(':
            self.consume()
            inner_fmt = self.consume_formatting()
            node = self.parse_expr(0, target)
            node.prefix_formatting = [Bracket(name='(')] + inner_fmt + node.prefix_formatting
            
            post_inner_fmt = self.consume_formatting()
            if self.peek() != ')':
                raise ParserError("Expected closing bracket ')'")
            self.consume()
            node.postfix_formatting = node.postfix_formatting + post_inner_fmt + [Bracket(name=')')]
            return node
        if t == "{": print("DEBUG: failed to match { patterns. Prefix patterns:", self.prefix_patterns)
        if not isinstance(t, str):
            from backend.SubstitutionManager import clone_ast
            self.consume()
            return clone_ast(t)
        
        # Quantifiers
        if t in QUANTIFIERS:
            if target in ("term", "prop"):
                raise ParserError(f"Quantifier '{t}' not allowed in {target}.")
            return self.parse_quantifier()
            
        # Choice Operators
        if t in ("ε", "ι"):
            if target == "prop":
                raise ParserError(f"Choice operator '{t}' not allowed in {target}.")
            return self.parse_epsilon_iota(t)
            
        # Unary Connective
        if t == "¬":
            if target == "term":
                raise ParserError("Connective '¬' not allowed in terms.")
            self.consume()
            fmt = self.consume_formatting()
            right = self.parse_expr(45, target)
            right.prefix_formatting = fmt + right.prefix_formatting
            return Connective(name=t, arity=1, arguments=[right])
            
        # 0-ary Logical Constants
        if t in ("⊤", "⊥"):
            if target == "term":
                raise ParserError(f"Logical constant '{t}' not allowed in terms.")
            self.consume()
            return Connective(name=t, arity=0, arguments=[])
            
        # Environment Symbols
        self.consume()
        
        if t.startswith('?t') or t.startswith('?u') or (t.startswith('?(') and ')' in t and (t.split(')')[1].startswith('t') or t.split(')')[1].startswith('u'))):
            from backend.AST import TermPlaceholder
            allowed_capture = set()
            if t.startswith('?('):
                allowed_str = t[2:t.index(')')]
                if allowed_str:
                    allowed_capture = set(allowed_str.split(','))
                index = int(t.split(')')[1][1:])
            else:
                index = int(t[2:])
            node = TermPlaceholder(index=index, allowed_capture=allowed_capture)
            node.name = t
            return node

        if t.startswith('?f') or (t.startswith('?(') and ')' in t and t.split(')')[1].startswith('f')):
            from backend.AST import FormulaPlaceholder
            allowed_capture = set()
            if t.startswith('?('):
                allowed_str = t[2:t.index(')')]
                if allowed_str:
                    allowed_capture = set(allowed_str.split(','))
                index = int(t.split(')')[1][1:])
            else:
                index = int(t[2:])
            node = FormulaPlaceholder(index=index, allowed_capture=allowed_capture)
            if target == "fol": return node
            raise ParserError(f"Placeholder '{t}' parsed but target is {target}")
            
        if t.startswith('?v'):
            index = int(t[2:])
            node = VariablePlaceholder(index=index)
            return node
            
        if target == "prop":
            if t in self.env.propositional_variables:
                return PropositionalVariable(name=t)
            raise UnrecognizedSymbolError(f"Unrecognized propositional variable: '{t}'")
            
        # target is term or fol
        if t in self.env.variables:
            return Variable(name=t)
        elif t in self.env.dummy_variables:
            return DummyVariable(name=t)
        elif t in self.env.terms:
            term_def = self.env.terms[t]
            if isinstance(term_def, Constant):
                return Constant(name=t)
            else:
                return Constant(name=t) # User-defined macro fallback
        
        raise UnrecognizedSymbolError(f"Unrecognized symbol '{t}' for target {target}")

    def parse_quantifier(self) -> Node:
        q_str = self.consume()
        fmt_after_q = self.consume_formatting()
        
        var_str = self.peek()
        from backend.AST import Node, Variable, VariablePlaceholder
        if isinstance(var_str, Node):
            var_node = var_str
            self.consume()
        else:
            if not var_str or (isinstance(var_str, str) and var_str not in self.env.variables and not (var_str.startswith('?v') and var_str[2:].isdigit())):
                raise ParserError(f"Quantifier {q_str} must be followed by a defined variable, got '{var_str}'")
            self.consume()
            if var_str.startswith('?v') and var_str[2:].isdigit():
                var_node = VariablePlaceholder(index=int(var_str[2:]))
            else:
                var_node = Variable(name=var_str)
        
        var_node.prefix_formatting = fmt_after_q + var_node.prefix_formatting
        
        fmt_after_var = self.consume_formatting()
        
        next_t = self.peek()
        if next_t == '(':
            self.consume()
            inner_fmt = self.consume_formatting()
            scope_node = self.parse_expr(0, "fol")
            
            post_inner_fmt = self.consume_formatting()
            if self.peek() != ')':
                raise ParserError("Expected ')' to close quantifier scope")
            self.consume()
            
            scope_node.prefix_formatting = [Bracket(name='(')] + inner_fmt + scope_node.prefix_formatting
            scope_node.postfix_formatting = scope_node.postfix_formatting + post_inner_fmt + [Bracket(name=')')]
            scope_node.prefix_formatting = fmt_after_var + scope_node.prefix_formatting
        else:
            scope_node = self.parse_expr(0, "fol")
            scope_node.prefix_formatting = fmt_after_var + scope_node.prefix_formatting
            
        return Quantifier(name=q_str, variable=var_node, formula=scope_node)

    def parse_epsilon_iota(self, op: str) -> Node:
        self.consume()
        fmt_after_op = self.consume_formatting()
        
        var_str = self.peek()
        from backend.AST import Node, Variable, VariablePlaceholder
        if isinstance(var_str, Node):
            var_node = var_str
            self.consume()
        else:
            if not var_str or (isinstance(var_str, str) and var_str not in self.env.variables and not (var_str.startswith('?v') and var_str[2:].isdigit())):
                raise ParserError(f"Operator {op} must be followed by a defined variable, got '{var_str}'")
            self.consume()
            if var_str.startswith('?v') and var_str[2:].isdigit():
                var_node = VariablePlaceholder(index=int(var_str[2:]))
            else:
                var_node = Variable(name=var_str)
        var_node.prefix_formatting = fmt_after_op + var_node.prefix_formatting
        
        fmt_after_var = self.consume_formatting()
        
        next_t = self.peek()
        if next_t == '(':
            self.consume()
            inner_fmt = self.consume_formatting()
            scope_node = self.parse_expr(0, "fol")
            
            post_inner_fmt = self.consume_formatting()
            if self.peek() != ')':
                raise ParserError("Expected ')' to close operator scope")
            self.consume()
            
            scope_node.prefix_formatting = [Bracket(name='(')] + inner_fmt + scope_node.prefix_formatting
            scope_node.postfix_formatting = scope_node.postfix_formatting + post_inner_fmt + [Bracket(name=')')]
            scope_node.prefix_formatting = fmt_after_var + scope_node.prefix_formatting
        else:
            scope_node = self.parse_expr(0, "fol")
            scope_node.prefix_formatting = fmt_after_var + scope_node.prefix_formatting
            
        if op == "ε":
            return Epsilon(variable=var_node, formula=scope_node)
        else:
            return Iota(variable=var_node, formula=scope_node)


def reconstruct_string_raw(node: Node) -> str:
    """Reconstructs the exact input string from the AST without colors."""
    res = "".join(f.name for f in node.prefix_formatting)
    
    if isinstance(node, (LongTerm, LongFormula)):
        from backend.MacroExpander import parse_pattern_structure
        from backend.Parser import lex
        pat_tokens = node.pattern
        struct = parse_pattern_structure(pat_tokens)
        
        def process_struct(st, iter_idx_map):
            out = ""
            for el in st:
                if isinstance(el, tuple) and el[0] == 'rep':
                    _, scope, rep_idx = el
                    count = node.repetition_counts.get(rep_idx, 0)
                    for i in range(count):
                        new_idx_map = iter_idx_map.copy()
                        new_idx_map[rep_idx] = i
                        out += process_struct(scope, new_idx_map)
                else:
                    if el.startswith('?'):
                        import re as regex
                        m = regex.match(r'\?[tuvf]\(?([\w,]+)\)?(\d+)_', el) or regex.match(r'\?[tuvf](\d+)_', el)
                        is_iter = m is not None
                        val = None
                        if (el.startswith('?t') or el.startswith('?u')) and el in node.term_placeholders:
                            val = node.term_placeholders[el]
                        elif el.startswith('?v') and el in node.var_placeholders:
                            val = node.var_placeholders[el]
                        elif el.startswith('?f') and el in node.formula_placeholders:
                            val = node.formula_placeholders[el]
                        
                        if val is not None:
                            if is_iter:
                                idx = int(m.group(1) if len(m.groups()) == 1 else m.group(2))
                                if idx in iter_idx_map and iter_idx_map[idx] < len(val):
                                    out += reconstruct_string_raw(val[iter_idx_map[idx]])
                                else:
                                    out += el
                            else:
                                out += reconstruct_string_raw(val)
                        else:
                            out += el
                    else:
                        out += el
            return out
            
        res += process_struct(struct, {})
    elif isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable, Constant, TermPlaceholder, FormulaPlaceholder, VariablePlaceholder)):
        res += node.name
    elif isinstance(node, (Quantifier)):
        res += node.name
        res += reconstruct_string_raw(node.variable)
        res += " "
        res += reconstruct_string_raw(node.formula)
    elif isinstance(node, (Epsilon, Iota)):
        res += "("
        res += node.name + " "
        res += reconstruct_string_raw(node.variable)
        res += " "
        res += reconstruct_string_raw(node.formula)
        res += ")"
    elif isinstance(node, (LongTerm, LongFormula)):
        res_str = node.definition_name
        for p_name, p_val in node.term_placeholders.items():
            res_str = res_str.replace(p_name, reconstruct_string_raw(p_val))
        for p_name, p_val in node.var_placeholders.items():
            res_str = res_str.replace(p_name, reconstruct_string_raw(p_val))
        res += res_str
    elif isinstance(node, Connective):
        if node.arity == 1:
            if node.name in ["¬", "∀", "∃"]:
                res += node.name
                res += reconstruct_string_raw(node.arguments[0])
            else:
                res += node.name
                res += "("
                res += reconstruct_string_raw(node.arguments[0])
                res += ")"
        elif node.arity == 2:
            res += reconstruct_string_raw(node.arguments[0])
            res += f" {node.name} "
            res += reconstruct_string_raw(node.arguments[1])
        elif node.arity > 2:
            res += node.name
            res += "("
            res += ", ".join(reconstruct_string_raw(arg) for arg in node.arguments)
            res += ")"
        elif node.arity == 0:
            res += node.name
            
    res += "".join(f.name for f in node.postfix_formatting)
    return res

def reconstruct_string_html(node: Node, depth_ref: list, target_name: str = None, target_type: str = None, occ_map: dict = None) -> str:
    if occ_map is None: occ_map = {}
    colors = ["#008B8B", "#FF00FF", "#FFA500", "#00FF00", "#6495ED", "#FF4500"]
    res = ""
    
    for f in node.prefix_formatting:
        if isinstance(f, Bracket):
            if f.name in "([{":
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
                depth_ref[0] += 1
            elif f.name in ")]}":
                depth_ref[0] = max(0, depth_ref[0] - 1)
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
        else:
            res += f.name
            
    tooltip = ""
    if isinstance(node, Variable): tooltip = "Variable"
    elif isinstance(node, DummyVariable): tooltip = "Dummy Variable"
    elif isinstance(node, PropositionalVariable): tooltip = "Propositional Variable"
    elif isinstance(node, MetaVariable): tooltip = "Meta Variable"
    elif isinstance(node, Quantifier): tooltip = "Quantifier"
    elif isinstance(node, (Iota, Epsilon)): tooltip = "Choice Operator"
    elif isinstance(node, Connective): tooltip = "Connective"
    elif isinstance(node, Constant): tooltip = "Constant / Macro"
    elif isinstance(node, (LongTerm, LongFormula)): tooltip = f"Custom Notation: {' '.join(node.pattern)}"

    def get_occ(sym: str) -> int:
        if sym not in occ_map:
            occ_map[sym] = 1
        else:
            occ_map[sym] += 1
        return occ_map[sym]

    def wrap(text: str, is_symbol: bool = False, sym_name: str = None) -> str:
        classes = "itp-tooltip" if tooltip else ""
        if is_symbol and target_name:
            classes += " interactive-symbol"
            s = sym_name if sym_name else text
            occ = get_occ(s)
            t_attr = f' data-tooltip="{tooltip}"' if tooltip else ""
            return f'<span class="{classes.strip()}" data-target="{target_name}" data-symbol="{s}" data-occ="{occ}"{t_attr}>{text}</span>'
        else:
            if tooltip:
                return f'<span class="{classes.strip()}" data-tooltip="{tooltip}">{text}</span>'
            return text

    if isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable, Constant, TermPlaceholder, FormulaPlaceholder, VariablePlaceholder)):
        res += wrap(node.name, True)
    elif isinstance(node, Quantifier):
        op_str = wrap(node.name, True)
        res += op_str
        res += reconstruct_string_html(node.variable, depth_ref, target_name, target_type, occ_map)
        res += " "
        res += reconstruct_string_html(node.formula, depth_ref, target_name, target_type, occ_map)
    elif isinstance(node, (Iota, Epsilon)):
        color = colors[depth_ref[0] % len(colors)]
        res += f'<span style="color: {color}">(</span>'
        depth_ref[0] += 1
        
        op_str = wrap(node.name, True)
        res += op_str
        res += reconstruct_string_html(node.variable, depth_ref, target_name, target_type, occ_map)
        res += " "
        res += reconstruct_string_html(node.formula, depth_ref, target_name, target_type, occ_map)
        
        depth_ref[0] = max(0, depth_ref[0] - 1)
        color = colors[depth_ref[0] % len(colors)]
        res += f'<span style="color: {color}">)</span>'

    elif isinstance(node, (LongTerm, LongFormula)):
        from backend.MacroExpander import parse_pattern_structure
        from backend.Parser import lex
        pat_tokens = node.pattern
        struct = parse_pattern_structure(pat_tokens)
        
        def process_struct_html(st, iter_idx_map):
            out = ""
            for el in st:
                if isinstance(el, tuple) and el[0] == 'rep':
                    _, scope, rep_idx = el
                    count = node.repetition_counts.get(rep_idx, 0)
                    for i in range(count):
                        new_idx_map = iter_idx_map.copy()
                        new_idx_map[rep_idx] = i
                        out += process_struct_html(scope, new_idx_map)
                else:
                    if el.startswith('?'):
                        import re as regex
                        m = regex.match(r'\?[tuvf]\(?([\w,]+)\)?(\d+)_', el) or regex.match(r'\?[tuvf](\d+)_', el)
                        is_iter = m is not None
                        val = None
                        if (el.startswith('?t') or el.startswith('?u')) and el in node.term_placeholders:
                            val = node.term_placeholders[el]
                        elif el.startswith('?v') and el in node.var_placeholders:
                            val = node.var_placeholders[el]
                        elif el.startswith('?f') and el in node.formula_placeholders:
                            val = node.formula_placeholders[el]
                        
                        if val is not None:
                            if is_iter:
                                idx = int(m.group(1) if len(m.groups()) == 1 else m.group(2))
                                if idx in iter_idx_map and iter_idx_map[idx] < len(val):
                                    out += reconstruct_string_html(val[iter_idx_map[idx]], depth_ref, target_name, target_type, occ_map)
                                else:
                                    out += wrap(el)
                            else:
                                out += reconstruct_string_html(val, depth_ref, target_name, target_type, occ_map)
                        else:
                            out += wrap(el)
                    else:
                        out += wrap(el)
            return out
            
        res_str = process_struct_html(struct, {})
        res += wrap(res_str, is_symbol=True, sym_name=node.definition_name)
    elif isinstance(node, (  Connective)):
        if node.arity == 1:
            if node.name in ["¬", "∀", "∃"]:
                op_str = wrap(node.name, True)
                res += op_str
                if isinstance(node.arguments[0], Connective) and node.arguments[0].arity == 2:
                    color = colors[depth_ref[0] % len(colors)]
                    res += f'<span style="color: {color}">(</span>'
                    depth_ref[0] += 1
                    res += reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
                    depth_ref[0] = max(0, depth_ref[0] - 1)
                    color = colors[depth_ref[0] % len(colors)]
                    res += f'<span style="color: {color}">)</span>'
                else:
                    res += reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
            else:
                op_str = wrap(node.name, True)
                res += op_str
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">(</span>'
                depth_ref[0] += 1
                res += reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
                depth_ref[0] = max(0, depth_ref[0] - 1)
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">)</span>'
        elif node.arity == 2:
            op_str = wrap(node.name, True)
            left_str = reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
            right_str = reconstruct_string_html(node.arguments[1], depth_ref, target_name, target_type, occ_map)
            res += left_str
            res += f" {op_str} "
            res += right_str
        elif node.arity > 2:
            op_str = wrap(node.name, True)
            res += op_str
            color = colors[depth_ref[0] % len(colors)]
            res += f'<span style="color: {color}">(</span>'
            depth_ref[0] += 1
            
            args_res = [reconstruct_string_html(arg, depth_ref, target_name, target_type, occ_map) for arg in node.arguments]
            res += ", ".join(args_res)
            
            depth_ref[0] = max(0, depth_ref[0] - 1)
            color = colors[depth_ref[0] % len(colors)]
            res += f'<span style="color: {color}">)</span>'
        elif node.arity == 0:
            res += wrap(node.name, True)
            
    for f in node.postfix_formatting:
        if isinstance(f, Bracket):
            if f.name in "([{":
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
                depth_ref[0] += 1
            elif f.name in ")]}":
                depth_ref[0] = max(0, depth_ref[0] - 1)
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
        else:
            res += f.name
            
    return res

def reconstruct_string(node: Node, color_mode: str = "ansi", target_name: str = None, target_type: str = None) -> str:
    """Reconstructs the AST and applies depth-based colorization or HTML tooltips."""
    if color_mode == "html":
        return reconstruct_string_html(node, [0], target_name=target_name, target_type=target_type)
    raw = reconstruct_string_raw(node)
    if color_mode == "none":
        return raw
    return colorize_formula(raw, mode=color_mode)

def parse_term(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "term")

def parse_fol_formula(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "fol")

def parse_prop_formula(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "prop")

def colorize_formula(text: str, mode: str = "ansi") -> str:
    """Applies depth-based color cycling to brackets and inner contents."""
    if mode == "none":
        return text
        
    if mode == "ansi":
        colors = [
            "\033[31m", # Red
            "\033[33m", # Yellow/Brown
            "\033[32m", # Green
            "\033[36m", # Cyan
            "\033[34m", # Blue
            "\033[35m", # Magenta
        ]
        reset = "\033[0m"
        
        result = [colors[0]]
        depth = 0
        
        for char in text:
            if char in "([{":
                color = colors[depth % len(colors)]
                result.append(f"{color}{char}")
                depth += 1
                result.append(colors[depth % len(colors)])
            elif char in ")]}":
                depth = max(0, depth - 1)
                color = colors[depth % len(colors)]
                result.append(f"{color}{char}")
                result.append(colors[depth % len(colors)])
            else:
                result.append(char)
                    
        return "".join(result) + reset
        
    elif mode == "html":
        colors = ["#008B8B", "#FF00FF", "#FFA500", "#00FF00", "#6495ED", "#FF4500"]
        result = [f'<span style="color: {colors[0]}">']
        depth = 0
        
        for char in text:
            if char in "([{":
                result.append(f'</span><span style="color: {colors[depth % len(colors)]}">{char}</span>')
                depth += 1
                result.append(f'<span style="color: {colors[depth % len(colors)]}">')
            elif char in ")]}":
                result.append('</span>')
                depth = max(0, depth - 1)
                result.append(f'<span style="color: {colors[depth % len(colors)]}">{char}</span>')
                result.append(f'<span style="color: {colors[depth % len(colors)]}">')
            else:
                result.append(char)
                
        result.append('</span>')
        
        # We need to clean up empty spans that might have been created
        html = "".join(result)
        html = re.sub(r'<span style="color: [^>]+"></span>', '', html)
        return html

def strip_ansi(text: str) -> str:
    """Removes ANSI escape codes from a string."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def show_environment(env: Environment):
    """Prints a simplified, human-readable view of the environment objects for all environments in the chain."""
    # Collect all environments from ground to current active
    chain = []
    curr = env
    while curr is not None:
        chain.append(curr)
        curr = curr.parent
    chain.reverse()
    
    def _cyan(s): return f"\033[36m{s}\033[0m"
    def _blue(s): return f"\033[34m{s}\033[0m"
    def _green(s): return f"\033[32m{s}\033[0m"
    def _bold(s): return f"\033[1m{s}\033[0m"
    def _yellow(s): return f"\033[33m{s}\033[0m"
    def _grey(s): return f"\033[90m{s}\033[0m"
    def _magenta(s): return f"\033[35m{s}\033[0m"

    # 1. Top Banner (Goal Chain)
    banner_parts = []
    for e in chain:
        if e.parent is None:
            # Ground environment has no goal (or we just ignore it for the banner)
            continue
        
        orig = getattr(e, "original_goal_formula_name", e.goal_formula_name)
        curr_g = e.goal_formula_name
        and_right = getattr(e, "and_right_formula_name", None)
        
        part = f"{orig}"
        if curr_g and curr_g != orig:
            part += f" = {curr_g}"
        if and_right:
            part += f" ∧ {and_right}"
        
        banner_parts.append(part)
        
    banner_str = " > ".join(banner_parts) if banner_parts else "GROUND"
    print("\n" + _cyan("=" * 10 + f" > {banner_str} " + "=" * 10))

    # 2. Consolidated Symbols (Variables, Dummy, Prop)
    # Cycle colors: ground = yellow, depth 1 = magenta, depth 2 = yellow, etc.
    color_funcs = [_yellow, _magenta]
    
    all_consts = []
    all_vars = []
    all_dummy = []
    all_prop = []
    all_funcs = []
    all_rels = []

    for depth, e in enumerate(chain):
        color_func = color_funcs[depth % len(color_funcs)]
        
        consts = []
        for k, v in e.local_terms.items():
            if isinstance(v, Constant) and k == v.name:
                consts.append(k)
        if consts:
            all_consts.append(color_func(", ".join(consts)))
            
        if e.local_variables:
            all_vars.append(color_func(", ".join(e.local_variables.keys())))
        if e.local_dummy_variables:
            all_dummy.append(color_func(", ".join(e.local_dummy_variables.keys())))
        if e.local_propositional_variables:
            all_prop.append(color_func(", ".join(e.local_propositional_variables.keys())))
            
    if all_consts: print(f"{_blue(_bold('Constants:'))} " + " | ".join(all_consts))
    if all_vars: print(f"{_blue(_bold('Variables:'))} " + " | ".join(all_vars))
    if all_dummy: print(f"{_blue(_bold('Dummy Variables:'))} " + " | ".join(all_dummy))
    if all_prop: print(f"{_blue(_bold('Propositional Variables:'))} " + " | ".join(all_prop))

    # 3. Environment-wise Terms and Formulae
    for depth, e in enumerate(chain):
        has_items = False
        
        # Terms
        terms = []
        for k, v in e.local_terms.items():
            if not (isinstance(v, Constant) and k == v.name):
                fv_str = ""
                if k in e.local_free_vars_cache and e.local_free_vars_cache[k]:
                    fv_str = f"  (Free: {', '.join(sorted(e.local_free_vars_cache[k]))})"
                terms.append(f"  {_grey(k)}: {reconstruct_string(v, color_mode='ansi')}{fv_str}")
                
        for k, v in e.local_long_terms.items():
            fv_str = ""
            if k in e.local_free_vars_cache and e.local_free_vars_cache[k]:
                fv_str = f"  (Free: {', '.join(sorted(e.local_free_vars_cache[k]))})"
            pattern_str = "".join(v.pattern)
            if v.definition_tokens:
                def_str = "".join(v.definition_tokens)
                terms.append(f"  {_grey(k)}: {pattern_str} ≡ {def_str}{fv_str}")
            else:
                terms.append(f"  {_grey(k)}: {pattern_str}{fv_str}")
                
        # Propositional Formulae
        prop_forms = []
        # First order Formulae
        fol_forms = []
        
        for k, v in e.local_formulae.items():
            if True:
                # Is it propositional or first order?
                # We can check if it uses only prop variables and connectives
                # But actually the easiest way is if the user defines it as prop
                # Or we can just check if k is in e.local_propositional_variables? No, it's a formula.
                # Let's just say a formula is prop if it only contains PropositionalVariable and Connective?
                # Wait, the problem says "Propositional formulae names".
                # A propositional formula is constructed purely from PropVars.
                # Actually, any formula can be 1st order. Let's just check if it contains any relations or quantifiers.
                def is_prop(node):
                    if isinstance(node, PropositionalVariable): return True
                    if isinstance(node, Connective): return all(is_prop(arg) for arg in node.arguments)
                    return False
                    
                color_k = k
                if k == e.goal_formula_name or k == getattr(e, "and_right_formula_name", None):
                    color_k = _yellow(k)
                elif k in e.theorems:
                    color_k = k # standard terminal default
                else:
                    color_k = _grey(k)
                    
                fv_str = ""
                if k in e.local_free_vars_cache and e.local_free_vars_cache[k]:
                    fv_str = f"  (Free: {', '.join(sorted(e.local_free_vars_cache[k]))})"
                    
                if is_prop(v):
                    prop_forms.append(f"  {_grey(k)}: {reconstruct_string(v, color_mode='ansi')}{fv_str}")
                else:
                    fol_forms.append(f"  {color_k}: {reconstruct_string(v, color_mode='ansi')}{fv_str}")

        for k, v in e.local_long_formulae.items():
            color_k = k
            if k == e.goal_formula_name or k == getattr(e, "and_right_formula_name", None):
                color_k = _yellow(k)
            elif k in e.theorems:
                color_k = k
            else:
                color_k = _grey(k)
            fv_str = ""
            if k in e.local_free_vars_cache and e.local_free_vars_cache[k]:
                fv_str = f"  (Free: {', '.join(sorted(e.local_free_vars_cache[k]))})"
            pattern_str = "".join(v.pattern)
            if v.definition_tokens:
                def_str = "".join(v.definition_tokens)
                fol_forms.append(f"  {color_k}: {pattern_str} ≡ {def_str}{fv_str}")
            else:
                fol_forms.append(f"  {color_k}: {pattern_str}{fv_str}")

        if terms or prop_forms or fol_forms:
            print(f"\n{_blue(_bold(f'Depth {depth}:'))}")
            if terms:
                print(_green(_bold("Terms:")))
                for t in terms: print(t)
            if prop_forms:
                print(_green(_bold("Propositional Formulae:")))
                for f in prop_forms: print(f)
            if fol_forms:
                print(_green(_bold("1st Order Formulae:")))
                for f in fol_forms: print(f)

