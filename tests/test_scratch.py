from backend.Environment import Environment
from backend.AST import Variable, Function, FunctionType
from backend.Parser import parse_fol_formula, reconstruct_string
from backend.SubstitutionManager import replace_structurally

env = Environment()
env.add_variable(Variable("x"))
env.add_variable(Variable("y"))
env.add_variable(Variable("z"))

dummy = Variable("x")
env.add_term(Function("S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))

f1 = parse_fol_formula("x = y ∨ x = y", env)
xy_node = parse_fol_formula("x = y", env)
sz_node2 = parse_fol_formula("S z = y", env)

f2 = replace_structurally(f1, xy_node, sz_node2, occurrence_idx=1)
print(f"Result: {reconstruct_string(f2)}")
