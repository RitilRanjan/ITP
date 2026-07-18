with open('backend/Parser.py', 'r') as f:
    c = f.read()

# Remove the incorrect breaks
c = c.replace('elif op in ("=", "∈") or (op in self.env.long_formulae):\n                if target == "term": break\n                right_target = "term"', 'elif op in ("=", "∈") or (op in self.env.long_formulae):\n                right_target = "term"')
c = c.replace('elif op in ("=", "∈") or (op in self.env.long_formulae):\n                if target == "term": break\n                if not isinstance(left, TermNode):', 'elif op in ("=", "∈") or (op in self.env.long_formulae):\n                if not isinstance(left, TermNode):')

# Add the break BEFORE self.consume()
search_str = """            prec = self.get_precedence(op)
            if prec < min_prec or prec == 0:
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            self.consume() # consume operator"""
            
replace_str = """            prec = self.get_precedence(op)
            if prec < min_prec or prec == 0:
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            if target == "term" and (op in ("=", "∈") or op in self.env.long_formulae):
                left.postfix_formatting = left.postfix_formatting + post_left_fmt
                break
                
            self.consume() # consume operator"""

c = c.replace(search_str, replace_str)

with open('backend/Parser.py', 'w') as f:
    f.write(c)
