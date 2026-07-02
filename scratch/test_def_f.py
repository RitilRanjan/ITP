from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable, Function, FunctionType
from Frontend import parse_term, parse_fol_formula
from CommandHandlers.definition_handlers import handle_def_f
from CommandHandlers.transformation_handlers import handle_fold

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

# Define S
s_decl = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[DummyVariable(name="_1")])
env.terms["S"] = s_decl

# Execute def_f 1 add_2 x S S x
handle_def_f(env, "1 add_2 x S S x")

print(f"add_2 in env.user_functions? {'add_2' in env.user_functions}")
if 'add_2' in env.user_functions:
    print(env.user_functions['add_2'])

# Create a formula and unfold
env.local_formulae["f1"] = parse_fol_formula("add_2 x = S S x", env)
handle_fold(env, "add_2 f1 f2 goal")

print(f"goal generated? {'goal' in env.local_formulae}")
if 'goal' in env.local_formulae:
    print(f"goal: {env.local_formulae['goal']}")

