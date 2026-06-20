import unittest
from AST import Variable, Bracket, Whitespace, Connective, Relation, Quantifier, SetBuilder
from Frontend import parse_term, reconstruct_string, ParserError
from Environment import Environment
from DefinitionExpander import expand_set_builder_in_formula

class TestSetBuilder(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.add_variable(Variable("x"))
        self.env.add_variable(Variable("y"))
        self.env.add_variable(Variable("A"))
        self.env.add_variable(Variable("B"))
        # Add basic symbols
        from AST import Relation, RelationType, Function, FunctionType
        dummy = Variable("x")
        self.env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
        self.env.add_formula(Relation(name="∈", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))

    def test_parse_set_builder(self):
        # { x ∈ A | x = y }
        term_str = "{ x ∈ A | x = y }"
        node = parse_term(term_str, self.env)
        self.assertIsInstance(node, SetBuilder)
        self.assertEqual(node.variable.name, "x")
        self.assertEqual(node.base_set.name, "A")
        self.assertIsInstance(node.formula, Relation)
        self.assertEqual(node.formula.name, "=")
        
        # Test reconstruction handles whitespaces correctly
        self.assertEqual(reconstruct_string(node), term_str)

    def test_parse_set_builder_irregular_spacing(self):
        term_str = "{x∈A|x=y}"
        node = parse_term(term_str, self.env)
        self.assertEqual(reconstruct_string(node), term_str)

        term_str2 = " {  x ∈ A|  x=y }  "
        node2 = parse_term(term_str2, self.env)
        self.assertEqual(reconstruct_string(node2), term_str2)

    def test_parse_set_builder_errors(self):
        # Unknown base set
        with self.assertRaises(ParserError):
            parse_term("{x ∈ C | x = y}", self.env)
        
        # Missing pipe
        with self.assertRaises(ParserError):
            parse_term("{x ∈ A  x = y}", self.env)

    def test_expand_set_builder(self):
        # Φ: {x ∈ A | x = x} = B
        from Frontend import parse_fol_formula
        formula = parse_fol_formula("{x ∈ A | x = x} = B", self.env)
        
        expanded = expand_set_builder_in_formula(self.env, formula, 1, "u")
        expanded_str = reconstruct_string(expanded)
        print("Expanded:", expanded_str)
        self.assertTrue(expanded_str.startswith("∃u"))
        self.assertIn("∀x", expanded_str.replace(" ", ""))
        self.assertIn("x∈u", expanded_str.replace(" ", ""))
        self.assertIn("x∈A", expanded_str.replace(" ", ""))

if __name__ == '__main__':
    unittest.main()
