import re

# 1. Update backend/Environment.py
with open("backend/Environment.py", "r") as f:
    env_code = f.read()

# Replace the unconditional long_terms initialization with conditional
target_env = """            # Inject Number Theory Constants and Predefined Functions
            self.local_terms["0"] = Constant("0")
            
            self.local_long_terms["S"] = LongDefinition(name="S", pattern=["S", "?t1"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            self.local_long_terms["+"] = LongDefinition(name="+", pattern=["?t1", "+", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            self.local_long_terms["*"] = LongDefinition(name="*", pattern=["?t1", "*", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            self.local_long_terms["^"] = LongDefinition(name="^", pattern=["?t1", "^", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            
            self.local_long_formulae["="] = LongDefinition(name="=", pattern=["?t1", "=", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            self.local_long_formulae["in"] = LongDefinition(name="in", pattern=["?t1", "∈", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)"""

replacement_env = """            self.local_long_formulae["="] = LongDefinition(name="=", pattern=["?t1", "=", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            
            if self.theory == "ZFC":
                self.local_long_formulae["∈"] = LongDefinition(name="∈", pattern=["?t1", "∈", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
            elif self.theory == "NT":
                self.local_terms["0"] = Constant("0")
                self.local_long_terms["S"] = LongDefinition(name="S", pattern=["S", "?t1"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
                self.local_long_terms["+"] = LongDefinition(name="+", pattern=["?t1", "+", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
                self.local_long_terms["*"] = LongDefinition(name="*", pattern=["?t1", "*", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)
                self.local_long_terms["^"] = LongDefinition(name="^", pattern=["?t1", "^", "?t2"], definition_tokens=[], def_type=DefinitionType.PRE_DEFINED)"""

if target_env in env_code:
    env_code = env_code.replace(target_env, replacement_env)
    with open("backend/Environment.py", "w") as f:
        f.write(env_code)
    print("Patched Environment.py")

# 2. Update main.py
with open("main.py", "r") as f:
    main_code = f.read()

target_main = """    dummy = Variable("x")
    # Pre-defined relation symbol = (equality, arity 2)
    env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    
    if theory == "ZFC":
        env.add_term(Constant("∅"))
        env.add_term(Constant("U"))
        env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
    elif theory == "NT":
        env.add_term(Constant("0"))
        env.add_term(Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[dummy]))
        env.add_term(Function(name="+", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
        env.add_term(Function(name="*", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))
        env.add_term(Function(name="^", arity=2, func_type=FunctionType.PRE_DEFINED, arguments=[dummy, dummy]))"""

replacement_main = """    pass"""

if target_main in main_code:
    main_code = main_code.replace(target_main, replacement_main)
    with open("main.py", "w") as f:
        f.write(main_code)
    print("Patched main.py")

# 3. Rename 'in' to '∈' in other files
def replace_in_file(filepath, old, new):
    with open(filepath, "r") as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Patched {filepath}")

replace_in_file("backend/DefinitionExpander.py", 'definition_name="in"', 'definition_name="∈"')
replace_in_file("backend/ZFC_Rules.py", 'definition_name != "in"', 'definition_name != "∈"')
replace_in_file("backend/Parser.py", 'if op == "∈": op_name = "in"', 'if op == "∈": op_name = "∈"')

