from main import get_default_env
env = get_default_env("ZFC")
print("Long Formulae:")
for k, v in env.long_formulae.items():
    print(f"  {k}: {' '.join(v.pattern)}")
print("Terms:")
for k in env.terms:
    print(f"  {k}")
print("Formulae:")
for k in env.formulae:
    print(f"  {k}")
