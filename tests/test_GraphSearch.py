from backend.AST import Variable
from main import get_default_env
from backend.Parser import parse_fol_formula, parse_prop_formula
from backend.GraphSearch import forward_search

def run_tests():
    env = get_default_env()

    # Test 1: x = x (Success with default limits)
    print("=== Test 1: Proving x = x ===")
    f1 = parse_fol_formula("x = x", env)
    env.formulae["f1"] = f1
    res1 = forward_search(env, "f1", time_limit=5.0, space_limit=100)
    assert res1 is True, "Should succeed in proving x = x"

    # Test 2: p => p (Success with default limits)
    print("\n=== Test 2: Proving p ⇒ p ===")
    f2 = parse_prop_formula("p ⇒ p", env)
    env.formulae["f2"] = f2
    res2 = forward_search(env, "f2", time_limit=5.0, space_limit=100)
    assert res2 is True, "Should succeed in proving p => p"

    # Test 3: Time limit exceeded
    print("\n=== Test 3: Time Limit Exceeded ===")
    f3 = parse_prop_formula("p ∧ q ⇒ p", env)
    env.formulae["f3"] = f3
    res3 = forward_search(env, "f3", time_limit=0.0, space_limit=1000)
    assert res3 is False, "Should fail due to time limit = 0.0"

    # Test 4: Space limit exceeded
    print("\n=== Test 4: Space Limit Exceeded ===")
    f4 = parse_prop_formula("p ∧ q ⇒ p", env)
    env.formulae["f4"] = f4
    # Set space limit to 2 (very low) to guarantee exceedance during formula generation
    res4 = forward_search(env, "f4", time_limit=5.0, space_limit=2)
    assert res4 is False, "Should fail due to space limit = 2"

    print("\nAll GraphSearch tests passed successfully!")

if __name__ == "__main__":
    run_tests()
