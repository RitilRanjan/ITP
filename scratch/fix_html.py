import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Frontend import colorize_formula

def fix_proofs_html():
    path = "/Users/ritilranjan/ITP/proofs.html"
    if not os.path.exists(path):
        print("Not found")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out_lines = []
    for line in lines:
        if line.startswith("# Foundational") or line.startswith("**Format**") or line.startswith("---") or line.strip() == "":
            out_lines.append(line)
            continue
            
        clean_line = re.sub(r'<span[^>]*>', '', line)
        clean_line = clean_line.replace('</span>', '')
        
        if ' ⊢ ' not in clean_line:
            out_lines.append(clean_line)
            continue
            
        lhs, rhs = clean_line.split(' ⊢ ', 1)
        
        # fix rhs: name: formula   (justification)
        rhs_match = re.match(r'^([^:]+):\s*(.*?)\s\s(\(.*\))<br>', rhs)
        if rhs_match:
            r_name, r_form, r_just = rhs_match.groups()
            new_rhs = f"{r_name}: {colorize_formula(r_form, mode='html')}  {r_just}<br>\n"
        else:
            new_rhs = rhs
            
        # fix lhs: name1: form1, name2: form2
        # We can split by ', ' where the next part matches `word: `
        if lhs.strip() == "":
            out_lines.append(f" ⊢ {new_rhs}")
            continue
            
        # Find all name: formula pairs
        # They look like: "name: formula" separated by ", "
        # Regex to find name: up to next ", name:" or end of string
        matches = list(re.finditer(r'([A-Za-z0-9_]+):\s*', lhs))
        new_lhs_parts = []
        for i in range(len(matches)):
            name = matches[i].group(1)
            start_form = matches[i].end()
            end_form = matches[i+1].start() - 2 if i + 1 < len(matches) else len(lhs)
            form = lhs[start_form:end_form]
            new_lhs_parts.append(f"{name}: {colorize_formula(form, mode='html')}")
            
        new_lhs = ", ".join(new_lhs_parts)
        out_lines.append(f"{new_lhs} ⊢ {new_rhs}")
        
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)
    print("Done")

if __name__ == "__main__":
    fix_proofs_html()
