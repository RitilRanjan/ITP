import traceback
from main import get_default_env
from Environment import Function, Relation

try:
    env = get_default_env("NT")
    print("Variables:")
    for name in env.variables:
        pass
    print("Prop variables:")
    for name in env.propositional_variables:
        pass
    print("Dummy variables:")
    for name in env.dummy_variables:
        pass
    print("Functions:")
    print(env.terms.keys())
    for name, term in env.terms.items():
        if isinstance(term, Function) and name == term.name:
            pass
    print("Relations:")
    for name, formula in env.formulae.items():
        if isinstance(formula, Relation) and name == formula.name:
            pass
    print("All good!")
except Exception as e:
    traceback.print_exc()
