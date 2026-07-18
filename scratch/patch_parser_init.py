import re
with open('backend/Parser.py', 'r') as f:
    c = f.read()

old_init = '''        self.infix_patterns = []
        
        for name, long_def in env.long_terms.items():
            if len(long_def.pattern) == 0: continue
            if long_def.pattern[0].startswith('?'):
                self.infix_patterns.append((long_def.pattern, name, "term"))
            else:
                self.prefix_patterns.append((long_def.pattern, name, "term"))
                
        for name, long_def in env.long_formulae.items():
            if len(long_def.pattern) == 0: continue
            if long_def.pattern[0].startswith('?'):
                self.infix_patterns.append((long_def.pattern, name, "formula"))
            else:
                self.prefix_patterns.append((long_def.pattern, name, "formula"))
                
        # Sort by pattern length descending
        self.prefix_patterns.sort(key=lambda x: len(x[0]), reverse=True)
        self.infix_patterns.sort(key=lambda x: len(x[0]), reverse=True)'''

new_init = '''        self.infix_patterns = []
        
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
        self.infix_patterns.sort(key=lambda x: (x[3], len(x[0])), reverse=True)'''

c = c.replace(old_init, new_init)

with open('backend/Parser.py', 'w') as f:
    f.write(c)
