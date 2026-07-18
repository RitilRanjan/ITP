from backend.Environment import Environment
from backend.CommandHandlers.transformation_handlers import handle_intro2
from backend.CommandHandlers.env_handlers import handle_ct, handle_cf
from backend.Parser import Parser

env = Environment()
# 1. Define schema f
handle_ct(env, 'f "f ?( ?t1_ )r1"')
print("Schema f:", env.long_terms['f'].pattern)

# 2. Define schema g
handle_ct(env, 'g "g ?( ?t1_ )r1"')

# 3. Create a target formula
parser = Parser(env)
f1 = parser.parse_expr(0, "f A B C = f A B C")
env.formulae['target'] = f1

print("Target formula before:", f1)

# 4. Try intro2
handle_intro2(env, 'f g target')
print("Target formula after:", env.formulae['target'])
