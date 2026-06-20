import sys

def extract():
    with open('/Users/ritilranjan/ITP/main.py', 'r') as f:
        lines = f.readlines()
        
    fold_lines = lines[2208:2776]
    simp_lines = lines[2776:2961]
    neg_lines = lines[2961:3151]
    
    # We need to de-indent by 8 spaces (2 tabs or 8 spaces)
    def clean_lines(lines, indent_to_remove=8):
        cleaned = []
        for line in lines:
            if not line.strip():
                cleaned.append("\n")
            elif line.startswith(" " * indent_to_remove):
                cleaned.append(line[indent_to_remove:])
            else:
                cleaned.append(line)
        return cleaned

    fold_body = clean_lines(fold_lines)
    simp_body = clean_lines(simp_lines)
    neg_body = clean_lines(neg_lines)

    # Note: 'continue' needs to become 'return'
    def replace_continue(lines):
        return [line.replace("continue\n", "return\n") if line.strip() == "continue" else line for line in lines]

    fold_body = replace_continue(fold_body)
    simp_body = replace_continue(simp_body)
    neg_body = replace_continue(neg_body)
    
    with open('/Users/ritilranjan/ITP/CommandHandlers/transformation_handlers.py', 'w') as f:
        f.write("from typing import Callable, Optional, Tuple, Any\n")
        f.write("from AST import Variable, Quantifier, Connective, Node, SetBuilder, Relation, Function, FunctionType\n")
        f.write("from Environment import Environment\n")
        f.write("from Frontend import lex, reconstruct_string\n")
        f.write("from SubstitutionManager import clone_ast, substitute_free\n")
        f.write("from Expansions import *\n")
        f.write("from ProofLogger import proof_logger\n")
        f.write("from Rewriting import apply_rewrite\n")
        f.write("\n")
        
        f.write("def handle_fold(env: Environment, args_str: str, validate_new_name: Callable, get_target_resolutions: Callable, handle_variable_capture_interactive: Callable) -> None:\n")
        # Remove the `elif cmd == "fold":` and outdent
        fold_body = fold_body[1:]
        fold_body = clean_lines(fold_body, 4)
        for line in fold_body:
            f.write("    " + line)
        f.write("\n")
        
        f.write("def handle_simp(env: Environment, args_str: str, cmd: str, validate_new_name: Callable) -> None:\n")
        simp_body = simp_body[1:]
        simp_body = clean_lines(simp_body, 4)
        for line in simp_body:
            f.write("    " + line)
        f.write("\n")
        
        f.write("def handle_neg(env: Environment, args_str: str, cmd: str, validate_new_name: Callable) -> None:\n")
        neg_body = neg_body[1:]
        neg_body = clean_lines(neg_body, 4)
        for line in neg_body:
            f.write("    " + line)
        f.write("\n")

if __name__ == "__main__":
    extract()
