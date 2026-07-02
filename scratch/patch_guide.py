import re
with open("CommandHandlers/terminal_handlers.py", "r") as f:
    content = f.read()

replacement = r'''    print("  intro  [<target>] <term> [<out>] [<equiv>] Instantiates ∀/∃ premises or reduces goals")
    print("  intro2 <schema> <term/formula> [<target>] [<out>] [<equiv>] Instantiates a universally quantified schema goal")'''
content = content.replace('    print("  intro  [<target>] <term> [<out>] [<equiv>] Instantiates ∀/∃ premises or reduces goals")', replacement)

with open("CommandHandlers/terminal_handlers.py", "w") as f:
    f.write(content)
