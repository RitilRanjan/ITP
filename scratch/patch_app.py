import re
with open('app.py', 'r') as f:
    c = f.read()

# Update terms rendering
old_terms = """                    for name, long_term in env.local_long_terms.items():
                        pattern_str = " ".join(long_term.pattern)
                        def_str = " ".join(long_term.definition_tokens)
                        term_html = f'<span style="color: #FFB6C1">{pattern_str}</span> ≡ <span style="color: #FFB6C1">{def_str}</span>'"""
new_terms = """                    for name, long_term in env.local_long_terms.items():
                        pattern_str = " ".join(long_term.pattern)
                        if long_term.definition_tokens:
                            def_str = " ".join(long_term.definition_tokens)
                            term_html = f'<span style="color: #FFB6C1">{pattern_str}</span> ≡ <span style="color: #FFB6C1">{def_str}</span>'
                        else:
                            term_html = f'<span style="color: #FFB6C1">{pattern_str}</span>'"""

c = c.replace(old_terms, new_terms)

old_forms = """                    for name, long_form in env.local_long_formulae.items():
                        pattern_str = " ".join(long_form.pattern)
                        def_str = " ".join(long_form.definition_tokens)
                        form_html = f'<span style="color: #FFB6C1">{pattern_str}</span> ≡ <span style="color: #FFB6C1">{def_str}</span>'"""
new_forms = """                    for name, long_form in env.local_long_formulae.items():
                        pattern_str = " ".join(long_form.pattern)
                        if long_form.definition_tokens:
                            def_str = " ".join(long_form.definition_tokens)
                            form_html = f'<span style="color: #FFB6C1">{pattern_str}</span> ≡ <span style="color: #FFB6C1">{def_str}</span>'
                        else:
                            form_html = f'<span style="color: #FFB6C1">{pattern_str}</span>'"""

c = c.replace(old_forms, new_forms)

with open('app.py', 'w') as f:
    f.write(c)
