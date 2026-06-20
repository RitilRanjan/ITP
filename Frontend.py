import re
from typing import List, Optional, Any
from AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, Function, FunctionType,
    PropositionalVariable, Relation, RelationType, Connective, Quantifier, MetaVariable,
    Bracket, Whitespace, SetBuilder
)
from Environment import Environment

class UnrecognizedSymbolError(Exception): pass
class ParserError(Exception): pass

LOGICAL_CONNECTIVES = {"¬", "∧", "∨", "⇒", "⇔"}
QUANTIFIERS = {"∀", "∃", "∃!"}

def lex(input_str: str) -> List[str]:
    """Tokenize the input string into a flat list of strings, preserving whitespaces, brackets, and logical symbols."""
    pattern = r'(⇔|⇒|∃!|\s+|[\?\w]+|[^\s\?\w])'
    tokens = re.split(pattern, input_str)
    return [t for t in tokens if t]

class Parser:
    def __init__(self, env: Environment):
        self.env = env
        self.tokens = []
        self.pos = 0

    def parse(self, input_str: str, target: str) -> Node:
        self.tokens = lex(input_str)
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

    def consume_formatting(self) -> List[Node]:
        fmt = []
        while True:
            t = self.peek()
            if not t:
                break
            if t.isspace():
                fmt.append(Whitespace(name=t))
                self.consume()
            else:
                break
        return fmt

    def get_precedence(self, op: str) -> int:
        if op in ("⇔",): return 10
        if op in ("⇒",): return 20
        if op in ("∨",): return 30
        if op in ("∧",): return 40
        if op in ("=", "∈") or (op in self.env.formulae and isinstance(self.env.formulae[op], Relation) and self.env.formulae[op].arity == 2):
            return 50
        if op in self.env.terms and isinstance(self.env.terms[op], Function) and self.env.terms[op].arity == 2:
            return 60
        return 0

    def parse_expr(self, min_prec: int, target: str) -> Node:
        prefix_fmt = self.consume_formatting()
        
        t = self.peek()
        if not t:
            raise ParserError("Unexpected end of input")
            
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
            
            node.prefix_formatting = prefix_fmt + node.prefix_formatting
            left = node
        else:
            left = self.parse_prefix(target)
            left.prefix_formatting = prefix_fmt + left.prefix_formatting

        # Parse infix operators
        while True:
            post_left_fmt = self.consume_formatting()
            op = self.peek()
            if not op:
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            prec = self.get_precedence(op)
            if prec < min_prec or prec == 0:
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            self.consume() # consume operator
            op_fmt = self.consume_formatting()
            
            # Determine correct target type for the right-hand side
            if op in LOGICAL_CONNECTIVES:
                right_target = target
            elif op in ("=", "∈") or (op in self.env.formulae and isinstance(self.env.formulae[op], Relation)):
                right_target = "term"
            elif op in self.env.terms and isinstance(self.env.terms[op], Function):
                right_target = "term"
            else:
                raise ParserError(f"Unknown binary operator '{op}'")
            
            right = self.parse_expr(prec + 1, right_target) # +1 for left-associativity
            right.prefix_formatting = op_fmt + right.prefix_formatting
            left.postfix_formatting = left.postfix_formatting + post_left_fmt
            
            # Build the node based on op with strict type assertions
            if op in LOGICAL_CONNECTIVES:
                if target == "term": raise ParserError(f"Logical connective '{op}' not allowed in terms.")
                if not isinstance(left, FormulaNode):
                    raise ParserError(f"Left operand of connective '{op}' must be a formula, got term.")
                if not isinstance(right, FormulaNode):
                    raise ParserError(f"Right operand of connective '{op}' must be a formula, got term.")
                left = Connective(name=op, arity=2, arguments=[left, right])
            elif op in ("=", "∈") or (op in self.env.formulae and isinstance(self.env.formulae[op], Relation)):
                if target == "term": raise ParserError(f"Relation '{op}' not allowed in terms.")
                if not isinstance(left, TermNode):
                    raise ParserError(f"Left operand of relation '{op}' must be a term, got formula.")
                if not isinstance(right, TermNode):
                    raise ParserError(f"Right operand of relation '{op}' must be a term, got formula.")
                if op in ("=", "∈"):
                    rel_type = RelationType.PRE_DEFINED
                else:
                    rel_type = self.env.formulae[op].rel_type
                left = Relation(name=op, arity=2, rel_type=rel_type, arguments=[left, right])
            elif op in self.env.terms and isinstance(self.env.terms[op], Function):
                if not isinstance(left, TermNode):
                    raise ParserError(f"Left operand of function '{op}' must be a term, got formula.")
                if not isinstance(right, TermNode):
                    raise ParserError(f"Right operand of function '{op}' must be a term, got formula.")
                f_def = self.env.terms[op]
                left = Function(name=op, arity=2, func_type=f_def.func_type, arguments=[left, right])
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
        t = self.peek()
        
        # Set Builder
        if t == '{':
            if target == "prop":
                raise ParserError(f"Set builder '{{' not allowed in {target}.")
            start_pos = self.pos
            self.consume()
            fmt_after_brace = self.consume_formatting()
            
            var_str = self.peek()
            if not var_str or var_str not in self.env.variables:
                raise ParserError(f"Set builder must start with a defined variable, got '{var_str}'")
            self.consume()
            var_node = Variable(name=var_str)
            var_node.prefix_formatting = fmt_after_brace + var_node.prefix_formatting
            
            fmt_after_var = self.consume_formatting()
            var_node.postfix_formatting = var_node.postfix_formatting + fmt_after_var
            
            in_sym = self.peek()
            if in_sym != '∈':
                raise ParserError(f"Expected '∈' in set builder, got '{in_sym}'")
            self.consume()
            
            fmt_after_in = self.consume_formatting()
            
            term_start_pos = self.pos
            pipe_indices = [i for i in range(term_start_pos, len(self.tokens)) if self.tokens[i] == '|']
            if not pipe_indices:
                raise ParserError("Expected '|' in set builder")
                
            last_err = None
            for pipe_idx in pipe_indices:
                self.pos = term_start_pos
                saved_tokens = self.tokens
                
                try:
                    self.tokens = saved_tokens[:pipe_idx]
                    try:
                        base_set_node = self.parse_expr(0, "term")
                        base_set_node.prefix_formatting = fmt_after_in + base_set_node.prefix_formatting
                        fmt_after_base = self.consume_formatting()
                        base_set_node.postfix_formatting = base_set_node.postfix_formatting + fmt_after_base
                    except ParserError as e:
                        raise ParserError(f"Failed parsing term: {e}")
                    
                    if self.pos != pipe_idx:
                        raise ParserError("Term did not consume all tokens up to '|'.")
                except ParserError as e:
                    last_err = e
                    self.tokens = saved_tokens
                    continue
                finally:
                    self.tokens = saved_tokens
                    
                self.pos = pipe_idx
                self.consume() # Consume '|'
                
                fmt_after_pipe = self.consume_formatting()
                
                try:
                    formula_node = self.parse_expr(0, "fol")
                    formula_node.prefix_formatting = fmt_after_pipe + formula_node.prefix_formatting
                    
                    fmt_after_formula = self.consume_formatting()
                    brace_close = self.peek()
                    if brace_close != '}':
                        raise ParserError(f"Expected '}}' to close set builder, got '{brace_close}'")
                    self.consume()
                    
                    node = SetBuilder(variable=var_node, base_set=base_set_node, formula=formula_node)
                    node.postfix_formatting = fmt_after_formula + [Bracket(name="}")] + node.postfix_formatting
                    return node
                except ParserError as e:
                    last_err = e
                    continue
            
            self.pos = start_pos
            raise ParserError(f"Failed to parse set builder. Last error: {last_err}")
            
        # Quantifiers
        if t in QUANTIFIERS:
            if target in ("term", "prop"):
                raise ParserError(f"Quantifier '{t}' not allowed in {target}.")
            return self.parse_quantifier()
            
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
        
        if target == "prop":
            if t in self.env.propositional_variables:
                return PropositionalVariable(name=t)
            raise UnrecognizedSymbolError(f"Unrecognized propositional variable: '{t}'")
            
        # target is term or fol
        if t in self.env.variables:
            return Variable(name=t)
        elif t in self.env.dummy_variables:
            return DummyVariable(name=t)
        elif t in self.env.terms and isinstance(self.env.terms[t], Function) and self.env.terms[t].name == t:
            f_def = self.env.terms[t]
            if f_def.arity == 0:
                return Function(name=t, arity=0, func_type=f_def.func_type, arguments=[])
            elif f_def.arity == 1:
                fmt = self.consume_formatting()
                right = self.parse_expr(80, "term")
                right.prefix_formatting = fmt + right.prefix_formatting
                return Function(name=t, arity=1, func_type=f_def.func_type, arguments=[right])
            elif f_def.arity > 2:
                args = []
                for _ in range(f_def.arity):
                    fmt = self.consume_formatting()
                    arg = self.parse_expr(0, "term")
                    arg.prefix_formatting = fmt + arg.prefix_formatting
                    args.append(arg)
                return Function(name=t, arity=f_def.arity, func_type=f_def.func_type, arguments=args)
            elif f_def.arity == 2:
                raise ParserError(f"Binary function '{t}' cannot be used as prefix.")
        elif t in self.env.formulae and isinstance(self.env.formulae[t], Relation) and self.env.formulae[t].name == t:
            r_def = self.env.formulae[t]
            if r_def.arity == 0:
                if target == "term": raise ParserError(f"Relation '{t}' not allowed in terms.")
                return Relation(name=t, arity=0, rel_type=r_def.rel_type, arguments=[])
            elif r_def.arity == 1:
                if target == "term": raise ParserError(f"Relation '{t}' not allowed in terms.")
                fmt = self.consume_formatting()
                right = self.parse_expr(80, "term")
                right.prefix_formatting = fmt + right.prefix_formatting
                return Relation(name=t, arity=1, rel_type=r_def.rel_type, arguments=[right])
            elif r_def.arity > 2:
                if target == "term": raise ParserError(f"Relation '{t}' not allowed in terms.")
                args = []
                for _ in range(r_def.arity):
                    fmt = self.consume_formatting()
                    arg = self.parse_expr(0, "term")
                    arg.prefix_formatting = fmt + arg.prefix_formatting
                    args.append(arg)
                return Relation(name=t, arity=r_def.arity, rel_type=r_def.rel_type, arguments=args)
            elif r_def.arity == 2:
                raise ParserError(f"Binary relation '{t}' cannot be used as prefix.")
        
        raise UnrecognizedSymbolError(f"Unrecognized symbol '{t}' for target {target}")

    def parse_quantifier(self) -> Node:
        q_str = self.consume()
        fmt_after_q = self.consume_formatting()
        
        var_str = self.peek()
        if not var_str or var_str not in self.env.variables:
            raise ParserError(f"Quantifier {q_str} must be followed by a defined variable, got '{var_str}'")
        self.consume()
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


def reconstruct_string_raw(node: Node) -> str:
    """Reconstructs the exact input string from the AST without colors."""
    res = "".join(f.name for f in node.prefix_formatting)
    
    if isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable)):
        res += node.name
    elif isinstance(node, Quantifier):
        res += node.name
        res += reconstruct_string_raw(node.variable)
        res += " "
        res += reconstruct_string_raw(node.formula)
    elif isinstance(node, SetBuilder):
        res += node.name
        res += reconstruct_string_raw(node.variable)
        res += "∈"
        res += reconstruct_string_raw(node.base_set)
        res += "|"
        res += reconstruct_string_raw(node.formula)
    elif isinstance(node, (Function, Relation, Connective)):
        if node.arity == 1:
            if node.name in ["¬", "∀", "∃"]:
                res += node.name
                if isinstance(node.arguments[0], Relation) and node.arguments[0].arity == 2:
                    res += "("
                    res += reconstruct_string_raw(node.arguments[0])
                    res += ")"
                else:
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

def reconstruct_string(node: Node, color_mode: str = "ansi") -> str:
    """Reconstructs the AST and applies depth-based colorization."""
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
        colors = ["#00FFFF", "#FF00FF", "#FFA500", "#00FF00", "#6495ED", "#FF4500"]
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

    # 2. Consolidated Symbols (Variables, Dummy, Prop, Functions, Relations)
    # Cycle colors: ground = yellow, depth 1 = magenta, depth 2 = yellow, etc.
    color_funcs = [_yellow, _magenta]
    
    all_vars = []
    all_dummy = []
    all_prop = []
    all_funcs = []
    all_rels = []

    for depth, e in enumerate(chain):
        color_func = color_funcs[depth % len(color_funcs)]
        
        if e.local_variables:
            all_vars.append(color_func(", ".join(e.local_variables.keys())))
        if e.local_dummy_variables:
            all_dummy.append(color_func(", ".join(e.local_dummy_variables.keys())))
        if e.local_propositional_variables:
            all_prop.append(color_func(", ".join(e.local_propositional_variables.keys())))
            
        funcs = []
        for k, v in e.local_terms.items():
            if isinstance(v, Function) and k == v.name:
                if k in e.local_user_functions:
                    arity, df = e.local_user_functions[k]
                    funcs.append(f"{k} {arity} = {reconstruct_string(df)}")
                else:
                    funcs.append(f"{k} {v.arity}")
        if funcs:
            all_funcs.append(color_func(", ".join(funcs)))
            
        rels = []
        for k, v in e.local_formulae.items():
            if isinstance(v, Relation) and k == v.name:
                if k in e.local_user_relations:
                    arity, df = e.local_user_relations[k]
                    rels.append(f"{k} {arity} ⇔ {reconstruct_string(df)}")
                else:
                    rels.append(f"{k} {v.arity}")
        if rels:
            all_rels.append(color_func(", ".join(rels)))

    if all_vars: print(f"{_blue(_bold('Variables:'))} " + " | ".join(all_vars))
    if all_dummy: print(f"{_blue(_bold('Dummy Variables:'))} " + " | ".join(all_dummy))
    if all_prop: print(f"{_blue(_bold('Propositional Variables:'))} " + " | ".join(all_prop))
    if all_funcs: print(f"{_blue(_bold('Functions:'))} " + " | ".join(all_funcs))
    if all_rels: print(f"{_blue(_bold('Relations:'))} " + " | ".join(all_rels))

    # 3. Environment-wise Terms and Formulae
    for depth, e in enumerate(chain):
        has_items = False
        
        # Terms
        terms = []
        for k, v in e.local_terms.items():
            if not (isinstance(v, Function) and k == v.name):
                terms.append(f"  {_grey(k)}: {reconstruct_string(v)}")
                
        # Propositional Formulae
        prop_forms = []
        # First order Formulae
        fol_forms = []
        
        for k, v in e.local_formulae.items():
            if not (isinstance(v, Relation) and k == v.name):
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
                    
                if is_prop(v):
                    prop_forms.append(f"  {_grey(k)}: {reconstruct_string(v, color_mode='ansi')}")
                else:
                    fol_forms.append(f"  {color_k}: {reconstruct_string(v, color_mode='ansi')}")

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

