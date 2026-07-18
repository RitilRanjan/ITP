import sys
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Environment import Environment

env = Environment()
handle_ct(env, 'S "S ?t1" S ?t1')

args_str = "1 add_2 S S ?t1"
sub_parts = args_str.split()
priority = 0
name_idx = 0
if len(sub_parts) > 2:
    try:
        priority = int(sub_parts[0])
        name_idx = 1
    except ValueError:
        pass
        
name = sub_parts[name_idx]
expr = " ".join(sub_parts[name_idx+1:])

print("sub_parts:", sub_parts)
print("name:", name)
print("expr:", expr)

from backend.Parser import parse_term
try:
    parse_term(expr, env)
except Exception as e:
    print(e)
