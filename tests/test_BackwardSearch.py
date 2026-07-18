import unittest
from backend.AST import (
    Variable, DummyVariable, PropositionalVariable, Function, FunctionType,
    Relation, RelationType, Quantifier, Connective
)
from backend.Environment import Environment
from backend.SubstitutionManager import clone_ast
from backend.BackwardSearch import (
    eliminate_implications, to_nnf, skolemize, distribute_or_over_and,
    process_to_cnf, unify, backward_search, get_literal_core, resolve,
    advanced_search, subsumes, one_way_match, paramodulate, is_term_greater
)

class TestBackwardSearch(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.x = Variable("x")
        self.y = Variable("y")
        self.z = Variable("z")
        self.p = PropositionalVariable("P")
        self.q = PropositionalVariable("Q")
        self.r = PropositionalVariable("R")
        self.f_x = Function("f", 1, FunctionType.USER_DEFINED, [self.x])
        self.P_x = Relation("P", 1, RelationType.USER_DEFINED, [self.x])
        self.P_y = Relation("P", 1, RelationType.USER_DEFINED, [self.y])
        self.Q_x = Relation("Q", 1, RelationType.USER_DEFINED, [self.x])
        
    def test_eliminate_implications(self):
        # P ⇒ Q  ->  ¬P ∨ Q
        imp = Connective("⇒", 2, [self.p, self.q])
        res = eliminate_implications(imp)
        self.assertEqual(res.name, "∨")
        self.assertEqual(res.arguments[0].name, "¬")
        self.assertEqual(res.arguments[0].arguments[0].name, "P")
        self.assertEqual(res.arguments[1].name, "Q")
        
    def test_to_nnf(self):
        # ¬(P ∧ Q) -> ¬P ∨ ¬Q
        formula = Connective("¬", 1, [Connective("∧", 2, [self.p, self.q])])
        res = to_nnf(formula)
        self.assertEqual(res.name, "∨")
        self.assertEqual(res.arguments[0].name, "¬")
        self.assertEqual(res.arguments[1].name, "¬")
        
        # ¬∀x P(x) -> ∃x ¬P(x)
        formula = Connective("¬", 1, [Quantifier("∀", self.x, self.P_x)])
        res = to_nnf(formula)
        self.assertEqual(res.name, "∃")
        self.assertEqual(res.variable.name, "x")
        self.assertEqual(res.formula.name, "¬")
        
    def test_skolemize(self):
        # ∀x ∃y R(x, y)
        R_xy = Relation("R", 2, RelationType.USER_DEFINED, [self.x, self.y])
        exists_y = Quantifier("∃", self.y, R_xy)
        forall_x = Quantifier("∀", self.x, exists_y)
        
        res = skolemize(forall_x)
        self.assertEqual(res.name, "∀")
        self.assertEqual(res.variable.name, "x")
        # Inside should be R(x, sk_n(x))
        inner_rel = res.formula
        self.assertEqual(inner_rel.name, "R")
        self.assertEqual(inner_rel.arguments[0].name, "x")
        self.assertIsInstance(inner_rel.arguments[1], Function)
        self.assertTrue(inner_rel.arguments[1].name.startswith("sk_"))
        self.assertEqual(len(inner_rel.arguments[1].arguments), 1)
        self.assertEqual(inner_rel.arguments[1].arguments[0].name, "x")

    def test_distribute_or_over_and(self):
        # P ∨ (Q ∧ R) -> (P ∨ Q) ∧ (P ∨ R)
        and_qr = Connective("∧", 2, [self.q, self.r])
        or_p_qr = Connective("∨", 2, [self.p, and_qr])
        res = distribute_or_over_and(or_p_qr)
        self.assertEqual(res.name, "∧")
        self.assertEqual(res.arguments[0].name, "∨")
        self.assertEqual(res.arguments[1].name, "∨")

    def test_unify_success(self):
        # P(x) and P(f(y))
        subst = {}
        P_fy = Relation("P", 1, RelationType.USER_DEFINED, [Function("f", 1, FunctionType.USER_DEFINED, [self.y])])
        self.assertTrue(unify(self.P_x, P_fy, subst))
        self.assertIn("x", subst)
        self.assertEqual(subst["x"].name, "f")
        
    def test_unify_occurs_check(self):
        # P(x) and P(f(x)) -> should fail
        subst = {}
        P_fx = Relation("P", 1, RelationType.USER_DEFINED, [Function("f", 1, FunctionType.USER_DEFINED, [self.x])])
        self.assertFalse(unify(self.P_x, P_fx, subst))

    def test_backward_search_propositional(self):
        # Modus Ponens: P, P => Q |- Q
        self.env.theorems["P"] = self.p
        imp = Connective("⇒", 2, [self.p, self.q])
        self.env.theorems["P_imp_Q"] = imp
        
        self.env.formulae["Goal_Q"] = self.q
        
        success = backward_search(self.env, "Goal_Q", time_limit=5.0)
        self.assertTrue(success)
        self.assertIn("Goal_Q", self.env.theorems)
        
    def test_backward_search_first_order(self):
        # Syllogism: ∀x(H(x) => M(x)), H(s) |- M(s)
        # We need a constant s. We'll use a 0-ary function 's'
        s = Function("s", 0, FunctionType.USER_DEFINED, [])
        H_x = Relation("H", 1, RelationType.USER_DEFINED, [self.x])
        M_x = Relation("M", 1, RelationType.USER_DEFINED, [self.x])
        
        # ∀x(H(x) => M(x))
        imp = Connective("⇒", 2, [H_x, M_x])
        forall = Quantifier("∀", self.x, imp)
        self.env.theorems["All_H_is_M"] = forall
        
        # H(s)
        H_s = Relation("H", 1, RelationType.USER_DEFINED, [s])
        self.env.theorems["H_s"] = H_s
        
        # Goal: M(s)
        M_s = Relation("M", 1, RelationType.USER_DEFINED, [s])
        self.env.formulae["Goal_M_s"] = M_s
        
        success = backward_search(self.env, "Goal_M_s", time_limit=5.0)
        self.assertTrue(success)
        self.assertIn("Goal_M_s", self.env.theorems)

    def test_subsumption(self):
        # P(x) subsumes P(f(y))
        c1 = [Relation("P", 1, RelationType.USER_DEFINED, [self.x])]
        c2 = [Relation("P", 1, RelationType.USER_DEFINED, [Function("f", 1, FunctionType.USER_DEFINED, [self.y])])]
        self.assertTrue(subsumes(c1, c2))
        self.assertFalse(subsumes(c2, c1))
        
        # P(x) subsumes P(a) v Q(b)
        c3 = [c2[0], Relation("Q", 1, RelationType.USER_DEFINED, [self.x])]
        self.assertTrue(subsumes(c1, c3))

    def test_paramodulation(self):
        # g(x) = f(y) and P(g(x)) -> P(f(y))
        f_y = Function("f", 1, FunctionType.USER_DEFINED, [self.y])
        g_x = Function("g", 1, FunctionType.USER_DEFINED, [self.x])
        eq = Relation("=", 2, RelationType.USER_DEFINED, [g_x, f_y])
        c1 = [eq]
        
        c2 = [Relation("P", 1, RelationType.USER_DEFINED, [g_x])]
        
        resolvents = paramodulate(c1, c2)
        # Should yield P(f(y_new))
        self.assertTrue(len(resolvents) > 0)
        found = False
        for r in resolvents:
            if len(r) == 1 and r[0].name == "P":
                if isinstance(r[0].arguments[0], Function) and r[0].arguments[0].name == "f":
                    found = True
        self.assertTrue(found)

    def test_advanced_search_propositional(self):
        self.env.theorems.clear()
        self.env.theorems["P"] = self.p
        imp = Connective("⇒", 2, [self.p, self.q])
        self.env.theorems["P_imp_Q"] = imp
        self.env.formulae["Goal_Q"] = self.q
        
        flags = {"sos": True, "unit": True, "subsumption": True, "paramodulation": False}
        success = advanced_search(self.env, "Goal_Q", time_limit=5.0, flags=flags)
        self.assertTrue(success)

    def test_term_ordering(self):
        # f(x) > x
        f_x = Function("f", 1, FunctionType.USER_DEFINED, [self.x])
        self.assertTrue(is_term_greater(f_x, self.x))
        self.assertFalse(is_term_greater(self.x, f_x))
        
        # f(f(x)) > f(x)
        ff_x = Function("f", 1, FunctionType.USER_DEFINED, [f_x])
        self.assertTrue(is_term_greater(ff_x, f_x))
        
        # Variable check constraint: f(x) and y -> y contains a variable not in f(x), so not greater
        self.assertFalse(is_term_greater(f_x, self.y))
        
    def test_ordered_paramodulation(self):
        # c1: g(x) = f(x) (since g > f alphabetically, we only paramodulate g(x) -> f(x))
        # c2: P(g(y))
        f_x = Function("f", 1, FunctionType.USER_DEFINED, [self.x])
        g_x = Function("g", 1, FunctionType.USER_DEFINED, [self.x])
        eq = Relation("=", 2, RelationType.USER_DEFINED, [g_x, f_x])
        c1 = [eq]
        
        g_y = Function("g", 1, FunctionType.USER_DEFINED, [self.y])
        c2 = [Relation("P", 1, RelationType.USER_DEFINED, [g_y])]
        
        # Ordering enabled: should produce P(f(y)) (replacing g(y) with f(y) because g(y) > f(y))
        resolvents_ordered = paramodulate(c1, c2, use_ordering=True)
        self.assertTrue(len(resolvents_ordered) > 0)
        
        # Verification that the substitution went in the correct direction: g(y) replaced by f(y)
        found_g = False
        found_f = False
        for r in resolvents_ordered:
            if len(r) == 1 and r[0].name == "P":
                arg = r[0].arguments[0]
                if isinstance(arg, Function) and arg.name == "f":
                    found_f = True
                if isinstance(arg, Function) and arg.name == "g":
                    found_g = True
        self.assertTrue(found_f)
        self.assertFalse(found_g) # should not have replaced f(y) -> g(y) because f is not greater than g

def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBackwardSearch)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise Exception("BackwardSearch tests failed")

if __name__ == '__main__':
    run_tests()
