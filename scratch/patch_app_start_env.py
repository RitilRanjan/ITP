with open('app.py', 'r') as f:
    content = f.read()

content = content.replace(
    'env.add_formula(Relation(name=r_def["name"], arity=r_def["arity"], rel_type=RelationType.PRE_DEFINED, arguments=[dummy]*r_def["arity"]))                                if level_data.get("start_env_commands"):',
    'env.add_formula(Relation(name=r_def["name"], arity=r_def["arity"], rel_type=RelationType.PRE_DEFINED, arguments=[dummy]*r_def["arity"]))\n                                if level_data.get("start_env_commands"):'
)

with open('app.py', 'w') as f:
    f.write(content)
