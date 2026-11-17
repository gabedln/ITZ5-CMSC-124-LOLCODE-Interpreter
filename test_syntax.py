"""Syntax regression tests using the professor's silogegg test programs.
Run: python test_syntax.py
"""
from pathlib import Path
from syntax_analyzer import parseProgram

TEST_DIR = Path(__file__).parent / "lolcode_tests"
EXPECTED_SYNTAX_FAILURES = {
    "2_var_decl_outside_wazzup.lol",
    "6_elseif_without_if.lol",
    "7_else_without_if.lol",
    "8_nested_all_of_any_of.lol",
    "9_nested_smoosh.lol",
    "11_loop_mismatched_closing_name.lol",
    "13_obtw_not_on_own_line.lol",
    "20_function_call_missing_parameters.lol",
    "error_wrong_function_arguments.lol",
}

def main():
    passed = failed = 0
    for path in sorted(TEST_DIR.glob("*.lol")):
        valid, message = parseProgram(path.read_text(encoding="utf-8"))
        expected_valid = path.name not in EXPECTED_SYNTAX_FAILURES
        success = valid == expected_valid
        passed += success
        failed += not success
        print(f"{'PASS' if success else 'FAIL'}: {path.name} — {message}")
    print(f"\nSyntax regression: {passed}/{passed + failed} passed; {failed} failed.")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
