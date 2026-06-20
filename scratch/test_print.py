import builtins
import re

original_print = builtins.print

def custom_print(*args, **kwargs):
    if "file" in kwargs:
        original_print(*args, **kwargs)
        return
        
    text = " ".join(str(a) for a in args)
    
    if "\033[" in text or "\x1b[" in text:
        original_print(*args, **kwargs)
        return
        
    if text.startswith("ITP") or text.startswith("\nITP") or text.startswith("Interactive Theorem Prover REPL") or text.startswith("Enter a command or") or text.startswith("Enable foundational proof logging") or text.startswith("Proof logging disabled"):
        original_print(*args, **kwargs)
        return
        
    if text == "":
        original_print(*args, **kwargs)
        return
        
    def replacer(match):
        return f"\033[34m{match.group(0)}\033[36m"
        
    subbed = re.sub(r"'[^']*'", replacer, text)
    colored_text = f"\033[36m{subbed}\033[0m"
    original_print(colored_text, **kwargs)

builtins.print = custom_print

print("Hello 'world'!")
print("Error: Formula 'P1' not found.")
print("ITP 1> show")
print("\033[33mAlready colored\033[0m")
