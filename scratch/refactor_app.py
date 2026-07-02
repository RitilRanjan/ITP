import sys

def main():
    with open("app.py", "r") as f:
        lines = f.readlines()
        
    out = []
    i = 0
    
    # Read until line 211 (0-indexed 210)
    while i < 210:
        out.append(lines[i])
        i += 1
        
    out.append("        render_prover_interface(is_game_mode=False)\n")
    
    # Lines 211 to 1179 are the prover interface
    prover_code = []
    while i < 1180:
        prover_code.append(lines[i])
        i += 1
        
    # The rest of the file
    rest_of_file = []
    while i < len(lines):
        rest_of_file.append(lines[i])
        i += 1
        
    # We will inject `def render_prover_interface(is_game_mode=False):` right after `init_session()` at line 127
    # Let's find `init_session()` in `out`
    inject_idx = 0
    for idx, l in enumerate(out):
        if "init_session()" in l:
            inject_idx = idx + 1
            break
            
    # Dedent the prover code by 8 spaces (since it was at `    else:` inside `with tab_programs:` -> 8 spaces)
    # Wait, the prover code starts at line 212: `        col_hdr1, ...` which has 8 spaces.
    # We want it to be 4 spaces inside `def render_prover_interface(...)`.
    # So we dedent by 4 spaces.
    dedented_prover = []
    for l in prover_code:
        if l.startswith("    "):
            dedented_prover.append(l[4:])
        else:
            dedented_prover.append(l)
            
    final_lines = out[:inject_idx] + ["\ndef render_prover_interface(is_game_mode=False):\n"] + dedented_prover + out[inject_idx:] + rest_of_file
    
    with open("app.py", "w") as f:
        f.writelines(final_lines)
        
if __name__ == "__main__":
    main()
