"""Focused regression tests for the ITZ5 semantic analyzer.
Run: python test_semantics.py
"""
import unittest
from semantics import runProgram

class SemanticTests(unittest.TestCase):
    def run_lol(self, body, inputs=None):
        source = "HAI\n" + body + "\nKTHXBYE"
        result = runProgram(source, input_values=inputs)
        self.assertTrue(result["success"], result["errors"])
        return result

    def test_arithmetic_and_dynamic_assignment(self):
        r = self.run_lol('''WAZZUP
I HAS A n ITZ 5
BUHBYE
n R SUM OF n AN 2
VISIBLE n''')
        self.assertEqual(r["output"], ["7"])
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "n"), ["n", 7, "NUMBR"])

    def test_integer_division_and_float_result(self):
        r = self.run_lol('''WAZZUP
I HAS A a ITZ QUOSHUNT OF 7 AN 2
I HAS A b ITZ QUOSHUNT OF 7 AN 2.0
BUHBYE
VISIBLE a b''')
        self.assertEqual(r["output"], ["33.50"])
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "a")[2], "NUMBR")
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "b")[2], "NUMBAR")

    def test_boolean_comparison_and_it(self):
        r = self.run_lol('''WAZZUP
I HAS A flag ITZ WIN
BUHBYE
BOTH OF flag AN FAIL
VISIBLE IT
VISIBLE BOTH SAEM 3 AN 3''')
        self.assertEqual(r["output"], ["FAIL", "WIN"])

    def test_maek_does_not_change_original(self):
        r = self.run_lol('''WAZZUP
I HAS A n ITZ 12
BUHBYE
MAEK n A YARN
VISIBLE IT n''')
        self.assertEqual(r["output"], ["1212"])
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "n")[2], "NUMBR")

    def test_is_now_a_changes_original(self):
        r = self.run_lol('''WAZZUP
I HAS A n ITZ 12
BUHBYE
n IS NOW A NUMBAR
VISIBLE n''')
        self.assertEqual(r["output"], ["12.00"])
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "n")[2], "NUMBAR")

    def test_gimmeh_stores_yarn(self):
        r = self.run_lol('''WAZZUP
I HAS A name
BUHBYE
GIMMEH name
VISIBLE name''', ["Franz"])
        self.assertEqual(r["output"], ["Franz"])
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "name")[2], "YARN")

    def test_if_else(self):
        r = self.run_lol('''WAZZUP
I HAS A n ITZ 2
BUHBYE
BOTH SAEM n AN 1
O RLY?
YA RLY
VISIBLE "one"
NO WAI
VISIBLE "not one"
OIC''')
        self.assertEqual(r["output"], ["not one"])

    def test_mebbe(self):
        r = self.run_lol('''WAZZUP
I HAS A n ITZ 2
BUHBYE
BOTH SAEM n AN 1
O RLY?
YA RLY
VISIBLE "one"
MEBBE BOTH SAEM n AN 2
VISIBLE "two"
NO WAI
VISIBLE "other"
OIC''')
        self.assertEqual(r["output"], ["two"])

    def test_til_loop(self):
        r = self.run_lol('''WAZZUP
I HAS A i ITZ 0
BUHBYE
IM IN YR count UPPIN YR i TIL BOTH SAEM i AN 3
VISIBLE i
IM OUTTA YR count''')
        self.assertEqual(r["output"], ["0", "1", "2"])
        self.assertEqual(next(x for x in r["symbol_table"] if x[0] == "i")[1], 3)

    def test_switch_fallthrough(self):
        r = self.run_lol('''WAZZUP
I HAS A choice ITZ 2
BUHBYE
choice
WTF?
OMG 1
VISIBLE "one"
OMG 2
VISIBLE "two"
OMG 3
VISIBLE "three"
OMGWTF
VISIBLE "default"
OIC''')
        self.assertEqual(r["output"], ["two", "three", "default"])

    def test_function_call_and_return(self):
        r = self.run_lol('''WAZZUP
I HAS A answer
BUHBYE
HOW IZ I add YR a AN YR b
FOUND YR SUM OF a AN b
IF U SAY SO
answer R I IZ add YR 2 AN YR 3 MKAY
VISIBLE answer IT''')
        self.assertEqual(r["output"], ["55"])

    def test_nested_function_calls(self):
        r = self.run_lol('''WAZZUP
BUHBYE
HOW IZ I square YR n
FOUND YR PRODUKT OF n AN n
IF U SAY SO
HOW IZ I add YR a AN YR b
FOUND YR SUM OF a AN b
IF U SAY SO
VISIBLE I IZ add YR I IZ square YR 3 MKAY AN YR I IZ square YR 4 MKAY MKAY''')
        self.assertEqual(r["output"], ["25"])

    def test_undeclared_variable_fails(self):
        r = runProgram('HAI\nVISIBLE missing\nKTHXBYE')
        self.assertFalse(r["success"])
        self.assertIn("undeclared variable", r["errors"][0])

    def test_division_by_zero_fails(self):
        r = runProgram('HAI\nQUOSHUNT OF 5 AN 0\nKTHXBYE')
        self.assertFalse(r["success"])
        self.assertIn("division by zero", r["errors"][0])

    def test_wrong_function_arity_fails(self):
        source = '''HAI
WAZZUP
BUHBYE
HOW IZ I add YR a AN YR b
FOUND YR SUM OF a AN b
IF U SAY SO
VISIBLE I IZ add MKAY
KTHXBYE'''
        r = runProgram(source)
        self.assertFalse(r["success"])
        self.assertIn("expects 2 argument(s)", r["errors"][0])

if __name__ == "__main__":
    unittest.main(verbosity=2)
