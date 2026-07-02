from Environment import Environment
from AST import Variable, Relation, RelationType, DummyVariable
from Frontend import parse_fol_formula
from CommandHandlers.transformation_handlers import handle_fold
import AST

env = Environment()
env.add_variable(Variable("x"))
dummy = DummyVariable("x")
env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

env.local_formulae["f1"] = parse_fol_formula("∀x x=x", env)
handle_fold(env, "∀ f1 f2 f3")
f3_node = env.formulae["f3"]

goal_str = "(∀x x=x) ⇔ ¬∃x ¬(x=x)"
goal_node = parse_fol_formula(goal_str, env)

def print_diff(n1, n2, path=""):
    if type(n1) != type(n2):
        print(f"{path}: {type(n1)} != {type(n2)}")
        return
    for k in n1.__dict__:
        if k in ('prefix_formatting', 'postfix_formatting'): continue
        v1 = getattr(n1, k)
        v2 = getattr(n2, k)
        if isinstance(v1, AST.Node):
            print_diff(v1, v2, path + f".{k}")
        elif isinstance(v1, list):
            if len(v1) != len(v2):
                print(f"{path}.{k}: len {len(v1)} != {len(v2)}")
            else:
                for i in range(len(v1)):
                    if isinstance(v1[i], AST.Node):
                        print_diff(v1[i], v2[i], path + f".{k}[{i}]")
                    elif v1[i] != v2[i]:
                        print(f"{path}.{k}[{i}]: {v1[i]} != {v2[i]}")
        elif v1 != v2:
            print(f"{path}.{k}: {v1} != {v2}")

print_diff(goal_node, f3_node)
