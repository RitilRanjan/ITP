import re

with open("app.py", "r") as f:
    app_code = f.read()

target = """                        } else if (obj_type === 'goal') {
                            cmds = ["intro2", "apply", "apply2", "apply3", "auto", "search", "backward_search", "advanced_search", "fold all", 'neg-', 'neg+', 'simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'rw'];
                        } else if (obj_type === 'proven') {
                            cmds = ['intro', 'apply', 'apply2', 'apply3', 'dt', 'and', 'left', 'right', 'imply', 'neg-', 'neg+', 'simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'rw', 'fold all'];"""
                            
repl = """                        } else if (obj_type === 'goal') {
                            cmds = ["intro2", "apply", "apply2", "apply3", "auto", "search", "backward_search", "advanced_search", "fold all", 'neg-', 'neg+', 'simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'rw', 'swap_eq', 'swap_bi'];
                        } else if (obj_type === 'proven') {
                            cmds = ['intro', 'apply', 'apply2', 'apply3', 'dt', 'and', 'left', 'right', 'imply', 'neg-', 'neg+', 'simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'rw', 'fold all', 'swap_eq', 'swap_bi'];"""

app_code = app_code.replace(target, repl)

with open("app.py", "w") as f:
    f.write(app_code)

print("Patched app.py cmds")
