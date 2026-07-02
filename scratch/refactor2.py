import sys

def main():
    with open("app.py", "r") as f:
        lines = f.readlines()
        
    out = []
    
    # We want to insert `def render_prover_interface(is_game_mode=False):` right before `st.title("Interactive Theorem Prover")`
    # Let's find that line
    insert_idx = 0
    for i, l in enumerate(lines):
        if 'st.title("Interactive Theorem Prover")' in l:
            insert_idx = i
            break
            
    # lines to extract: 211 ("        # PROVER INTERFACE") to 1179 ("            st.rerun()")
    # We will search for `# PROVER INTERFACE` and `st.rerun()` that matches the block.
    start_idx = 0
    end_idx = 0
    for i, l in enumerate(lines):
        if '# PROVER INTERFACE' in l:
            start_idx = i
            break
            
    for i in range(start_idx, len(lines)):
        if 'with tab_games:' in lines[i]:
            end_idx = i - 1
            # Wait, `tab_games` might not exist yet because we restored app.py!
            # Let's search for `with tab_help:`
        elif 'with tab_help:' in lines[i]:
            end_idx = i - 1
            break
            
    # Walk backward from end_idx to find the `st.rerun()`
    while 'st.rerun()' not in lines[end_idx]:
        end_idx -= 1
        
    prover_code = lines[start_idx:end_idx+1]
    
    # Dedent prover code
    dedented_prover = []
    for l in prover_code:
        if l.startswith("        "): # 8 spaces
            dedented_prover.append(l[4:])
        else:
            dedented_prover.append(l) # shouldn't happen for the main body but just in case
            
    # Assemble
    final_lines = lines[:insert_idx]
    final_lines.append("def render_prover_interface(is_game_mode=False):\n")
    final_lines.extend(dedented_prover)
    final_lines.append("\n")
    final_lines.extend(lines[insert_idx:start_idx])
    final_lines.append("        render_prover_interface(is_game_mode=False)\n")
    final_lines.extend(lines[end_idx+1:])
    
    with open("app.py", "w") as f:
        f.writelines(final_lines)

if __name__ == "__main__":
    main()
