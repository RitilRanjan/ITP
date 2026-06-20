import re

def lex(input_str: str):
    pattern = r'(\s+|\(|\)|⇔|⇒|∃!|∀|∃|¬|∧|∨|∈|=)'
    tokens = re.split(pattern, input_str)
    return [t for t in tokens if t]

print(lex("¬∃B∀A A∈B"))
print(lex("∀ x ( x ∈ R ⇔ ¬ ( x ∈ x ) )"))
print(lex("A_1=B_2"))
print(lex("∃!x Ψ(x)"))
print(lex("∃!x(x=x)"))
print(lex("∃!x_1 x_1=x_1"))

