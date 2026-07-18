from backend.Environment import Environment
from backend.CommandHandlers.env_handlers import handle_ct
from backend.Parser import Parser, lex

env = Environment()
handle_ct(env, 'S "S ?t1" S ?t1')

parser = Parser(env)
print("prefix_patterns:", parser.prefix_patterns)

