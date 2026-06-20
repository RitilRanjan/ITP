import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock pytest to avoid installing external dependencies in a network-less environment
class MockPytest:
    class raises:
        def __init__(self, expected_exception):
            self.expected_exception = expected_exception
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                raise AssertionError(f"Expected exception {self.expected_exception} was not raised")
            if not issubclass(exc_type, self.expected_exception):
                raise exc_val
            return True

sys.modules['pytest'] = MockPytest

import test_AST
import test_Frontend
import test_Substitution
import test_ZFC
import test_Abstraction
import test_TruthEvaluator
import test_SequentEvaluator
import test_DeductiveSystem
import test_Definitions
import test_Iota
import test_DefinitionExpander
import test_Missions
import test_Storage
import test_AutoProver
import test_Contradiction
import test_GraphSearch
import test_BackwardSearch
import test_InlineDefinitions

def run_all():
    failed = False
    
    print("Running AST tests...")
    test_funcs_ast = [getattr(test_AST, name) for name in dir(test_AST) if name.startswith("test_")]
    for func in test_funcs_ast:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True

    print("\nRunning Frontend tests...")
    test_funcs_fe = [getattr(test_Frontend, name) for name in dir(test_Frontend) if name.startswith("test_")]
    for func in test_funcs_fe:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True

    print("\nRunning Substitution tests...")
    test_funcs_sub = [getattr(test_Substitution, name) for name in dir(test_Substitution) if name.startswith("test_")]
    for func in test_funcs_sub:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning ZFC Axioms tests...")
    test_funcs_zfc = [getattr(test_ZFC, name) for name in dir(test_ZFC) if name.startswith("test_")]
    for func in test_funcs_zfc:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Propositional Abstraction tests...")
    test_funcs_abs = [getattr(test_Abstraction, name) for name in dir(test_Abstraction) if name.startswith("test_")]
    for func in test_funcs_abs:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Truth Evaluator tests...")
    test_funcs_te = [getattr(test_TruthEvaluator, name) for name in dir(test_TruthEvaluator) if name.startswith("test_")]
    for func in test_funcs_te:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Sequent Evaluator tests...")
    test_funcs_se = [getattr(test_SequentEvaluator, name) for name in dir(test_SequentEvaluator) if name.startswith("test_")]
    for func in test_funcs_se:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Deductive System tests...")
    test_funcs_ds = [getattr(test_DeductiveSystem, name) for name in dir(test_DeductiveSystem) if name.startswith("test_")]
    for func in test_funcs_ds:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Definition tests...")
    test_funcs_def = [getattr(test_Definitions, name) for name in dir(test_Definitions) if name.startswith("test_")]
    for func in test_funcs_def:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Iota and Name Validation tests...")
    test_funcs_iota = [getattr(test_Iota, name) for name in dir(test_Iota) if name.startswith("test_")]
    for func in test_funcs_iota:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True

    print("\nRunning Epsilon tests...")
    import test_Epsilon
    test_funcs_epsilon = [getattr(test_Epsilon, name) for name in dir(test_Epsilon) if name.startswith("test_")]
    for func in test_funcs_epsilon:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Definition Expander tests...")
    test_funcs_exp = [getattr(test_DefinitionExpander, name) for name in dir(test_DefinitionExpander) if name.startswith("test_")]
    for func in test_funcs_exp:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Nested Scopes/Missions tests...")
    test_funcs_miss = [getattr(test_Missions, name) for name in dir(test_Missions) if name.startswith("test_")]
    for func in test_funcs_miss:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Storage tests...")
    test_funcs_store = [getattr(test_Storage, name) for name in dir(test_Storage) if name.startswith("test_")]
    for func in test_funcs_store:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Auto Prover tests...")
    test_funcs_auto = [getattr(test_AutoProver, name) for name in dir(test_AutoProver) if name.startswith("test_")]
    for func in test_funcs_auto:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True

    print("\nRunning Contradiction (contra) tests...")
    test_funcs_contra = [getattr(test_Contradiction, name) for name in dir(test_Contradiction) if name.startswith("test_")]
    for func in test_funcs_contra:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    print("\nRunning Graph Search tests...")
    try:
        test_GraphSearch.run_tests()
        print("  [PASS] test_GraphSearch")
    except Exception as e:
        print(f"  [FAIL] test_GraphSearch: {e}")
        import traceback
        traceback.print_exc()
        traceback.print_exc()
        failed = True

    print("\nRunning Backward Search tests...")
    try:
        test_BackwardSearch.run_tests()
        print("  [PASS] test_BackwardSearch")
    except Exception as e:
        print(f"  [FAIL] test_BackwardSearch: {e}")
        import traceback
        traceback.print_exc()
        failed = True
    print("\nRunning Inline Definitions tests...")
    test_funcs_inline = [getattr(test_InlineDefinitions, name) for name in dir(test_InlineDefinitions) if name.startswith("test_")]
    for func in test_funcs_inline:
        try:
            func()
            print(f"  [PASS] {func.__name__}")
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    if failed:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_all()
