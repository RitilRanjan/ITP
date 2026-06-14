import json
import sys
from Environment import Environment
from AST import (
    Variable, DummyVariable, PropositionalVariable, Function, FunctionType,
    Relation, RelationType
)
from Frontend import (
    parse_term, parse_fol_formula, parse_prop_formula, reconstruct_string,
    UnrecognizedSymbolError, ParserError
)

def get_dummy_env() -> Environment:
    """Initializes the environment with default data for testing."""
    env = Environment()
    
    # Standard Variables
    v_x = Variable(name="x")
    v_y = Variable(name="y")
    env.add_variable(v_x)
    env.add_variable(v_y)
    
    # Pre-defined function term S (arity 1) with argument x
    f_S = Function(name="S", arity=1, func_type=FunctionType.PRE_DEFINED, arguments=[v_x])
    env.add_term(f_S)
    
    # Pre-defined relation formula = (arity 2) with arguments [x, y]
    rel_eq = Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[v_x, v_y])
    env.add_formula(rel_eq)
    
    # Propositional Variables
    env.add_propositional_variable(PropositionalVariable("P"))
    env.add_propositional_variable(PropositionalVariable("Q"))
    
    return env

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

def main():
    print_header("Interactive Theorem Prover CLI")
    env = get_dummy_env()
    
    while True:
        # 1. Print Environment JSON
        print("\n--- Current Environment State ---")
        print(env.to_json())
        print("-" * 33)
        
        # 2. Offer options
        print("\nChoose an option:")
        print("  1. Parse & Register a Term")
        print("  2. Parse & Register a First-Order Logic (FOL) Formula")
        print("  3. Parse & Register a Propositional Formula")
        print("  4. Define/Declare a standard Variable")
        print("  5. Define/Declare a Dummy Variable")
        print("  6. Define/Declare a Propositional Variable")
        print("  7. Define/Declare a Function Symbol")
        print("  8. Define/Declare a Relation Symbol")
        print("  9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        if not choice:
            continue
            
        if choice == "9":
            print("\nExiting. Goodbye!")
            sys.exit(0)
            
        try:
            if choice == "1":
                inp = input("Enter term string (e.g. 'S x'): ").strip()
                ast = parse_term(inp, env)
                print(f"\n[SUCCESS] Reconstructed: '{reconstruct_string(ast)}'")
                
                name = input("Enter name to register this term in Environment (press Enter to auto-save): ").strip()
                if not name:
                    name = reconstruct_string(ast).replace(" ", "")
                env.terms[name] = ast
                print(f"Registered term '{name}' in Environment.")
                
            elif choice == "2":
                inp = input("Enter FOL formula string (e.g. 'x = y ∧ ∀ x ( x = y )'): ").strip()
                ast = parse_fol_formula(inp, env)
                print(f"\n[SUCCESS] Reconstructed: '{reconstruct_string(ast)}'")
                
                name = input("Enter name to register this formula in Environment (press Enter to auto-save): ").strip()
                if not name:
                    name = reconstruct_string(ast).replace(" ", "")
                env.formulae[name] = ast
                print(f"Registered formula '{name}' in Environment.")
                
            elif choice == "3":
                inp = input("Enter Propositional formula string (e.g. '¬ P ∨ Q'): ").strip()
                ast = parse_prop_formula(inp, env)
                print(f"\n[SUCCESS] Reconstructed: '{reconstruct_string(ast)}'")
                
                name = input("Enter name to register this formula in Environment (press Enter to auto-save): ").strip()
                if not name:
                    name = reconstruct_string(ast).replace(" ", "")
                env.formulae[name] = ast
                print(f"Registered formula '{name}' in Environment.")
                
            elif choice == "4":
                name = input("Enter standard variable name to define (e.g. 'z'): ").strip()
                if not name:
                    raise ValueError("Name cannot be empty.")
                env.add_variable(Variable(name=name))
                print(f"Defined variable '{name}'.")
                
            elif choice == "5":
                name = input("Enter dummy variable name to define (e.g. 'd'): ").strip()
                if not name:
                    raise ValueError("Name cannot be empty.")
                env.add_dummy_variable(DummyVariable(name=name))
                print(f"Defined dummy variable '{name}'.")
                
            elif choice == "6":
                name = input("Enter propositional variable name to define (e.g. 'R'): ").strip()
                if not name:
                    raise ValueError("Name cannot be empty.")
                env.add_propositional_variable(PropositionalVariable(name=name))
                print(f"Defined propositional variable '{name}'.")
                
            elif choice == "7":
                name = input("Enter function symbol name to define (e.g. '+'): ").strip()
                if not name:
                    raise ValueError("Name cannot be empty.")
                arity_str = input("Enter function arity (e.g. '2'): ").strip()
                arity = int(arity_str)
                print("Function types: 1. PRE_DEFINED, 2. USER_DEFINED, 3. IOTA_DEFINED")
                ft_choice = input("Enter type (1-3) [default: 2]: ").strip()
                ft = FunctionType.USER_DEFINED
                if ft_choice == "1":
                    ft = FunctionType.PRE_DEFINED
                elif ft_choice == "3":
                    ft = FunctionType.IOTA_DEFINED
                
                # Satisfy validation with dummy Variable arguments
                dummy = Variable("x")
                args = [dummy] * arity
                env.add_term(Function(name=name, arity=arity, func_type=ft, arguments=args))
                print(f"Defined function symbol '{name}' with arity {arity}.")
                
            elif choice == "8":
                name = input("Enter relation symbol name to define (e.g. '∈'): ").strip()
                if not name:
                    raise ValueError("Name cannot be empty.")
                arity_str = input("Enter relation arity (e.g. '2'): ").strip()
                arity = int(arity_str)
                print("Relation types: 1. PRE_DEFINED, 2. USER_DEFINED")
                rt_choice = input("Enter type (1-2) [default: 2]: ").strip()
                rt = RelationType.USER_DEFINED
                if rt_choice == "1":
                    rt = RelationType.PRE_DEFINED
                
                # Satisfy validation with dummy Variable arguments
                dummy = Variable("x")
                args = [dummy] * arity
                env.add_formula(Relation(name=name, arity=arity, rel_type=rt, arguments=args))
                print(f"Defined relation symbol '{name}' with arity {arity}.")
                
            else:
                print("Invalid option. Please choose 1-9.")
                
        except (UnrecognizedSymbolError, ParserError) as pe:
            print(f"\n[PARSER ERROR] {pe}")
        except ValueError as ve:
            print(f"\n[VALUE ERROR] {ve}")
        except Exception as e:
            print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()
