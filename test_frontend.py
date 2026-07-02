import sys
from Environment import Environment
from AST import Variable
from Frontend import reconstruct_string, parse_fol_formula

env = Environment()
env.variables["x"] = Variable("x")
env.variables["y"] = Variable("y")
node = parse_fol_formula("∀x (x ∈ y)", env)
html = reconstruct_string(node, color_mode="html", target_name="f1", target_type="fol")
print(html)
