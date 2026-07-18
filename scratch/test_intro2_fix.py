from backend.Environment import Environment
from backend.CommandHandlers.transformation_handlers import handle_intro2
from backend.CommandHandlers.env_handlers import handle_ct, handle_cf
from backend.Parser import parse_fol_formula

env = Environment()

# Add constants A, B, C for testing
from backend.AST import Constant
env.local_constants['A'] = Constant('A')
env.local_constants['B'] = Constant('B')
env.local_constants['C'] = Constant('C')

# 1. Define schema f
handle_ct(env, 'f "f ?( ?t1_ )r1"')
print("Schema f:", env.long_terms['f'].pattern)

# 2. Define schema g
handle_ct(env, 'g "g ?( ?t1_ )r1"')

# 3. Create a target formula
f1 = parse_fol_formula("f A B C = f A B C", env)
env.formulae['target'] = f1
from backend.Parser import reconstruct_string
print("Target formula before:", reconstruct_string(f1))

# 4. Try intro2
handle_intro2(env, 'f g target')
print("Target formula after:", reconstruct_string(env.formulae['target']))

