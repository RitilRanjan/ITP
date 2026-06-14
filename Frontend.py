import re
from typing import List, Optional, Any
from AST import (
    Node, TermNode, FormulaNode, Variable, DummyVariable, Function, FunctionType,
    PropositionalVariable, Relation, RelationType, Connective, Quantifier, MetaVariable,
    Bracket, Whitespace
)
from Environment import Environment

class UnrecognizedSymbolError(Exception): pass
class ParserError(Exception): pass

LOGICAL_CONNECTIVES = {"¬", "∧", "∨", "⇒", "⇔"}
QUANTIFIERS = {"∀", "∃", "∃!"}

def lex(input_str: str) -> List[str]:
    """Tokenize the input string into a flat list of strings, preserving whitespaces and brackets."""
    tokens = re.split(r'(\s+|\(|\))', input_str)
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
            right = self.parse_expr(70, target)
            right.prefix_formatting = fmt + right.prefix_formatting
            return Connective(name=t, arity=1, arguments=[right])
            
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
        elif t in self.env.terms and isinstance(self.env.terms[t], Function):
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


def reconstruct_string(node: Node) -> str:
    """Reconstructs the exact input string from the AST."""
    res = "".join(f.name for f in node.prefix_formatting)
    
    if isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable)):
        res += node.name
    elif isinstance(node, Quantifier):
        res += node.name
        res += reconstruct_string(node.variable)
        res += reconstruct_string(node.formula)
    elif isinstance(node, (Function, Relation, Connective)):
        if node.arity == 1:
            res += node.name
            res += reconstruct_string(node.arguments[0])
        elif node.arity == 2:
            res += reconstruct_string(node.arguments[0])
            res += node.name
            res += reconstruct_string(node.arguments[1])
        elif node.arity > 2:
            res += node.name
            for arg in node.arguments:
                res += reconstruct_string(arg)
        elif node.arity == 0:
            res += node.name
            
    res += "".join(f.name for f in node.postfix_formatting)
    return res

def parse_term(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "term")

def parse_fol_formula(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "fol")

def parse_prop_formula(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "prop")
