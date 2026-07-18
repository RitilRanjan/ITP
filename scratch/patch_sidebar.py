with open("app.py", "r") as f:
    code = f.read()

target = 'st.set_page_config(page_title="Interactive Theorem Prover", layout="wide")'
repl = 'st.set_page_config(page_title="Interactive Theorem Prover", layout="wide", initial_sidebar_state="collapsed")'

code = code.replace(target, repl)

with open("app.py", "w") as f:
    f.write(code)

print("Patched app.py sidebar")
