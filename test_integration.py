
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "lolcode_tests"
INTERPRETER = BASE_DIR / "interpreter.py"

# Files expected to fail lexical analysis
EXPECTED_LEXICAL_FAILURES = {
    "13_obtw_not_on_own_line.lol",
}

# Files expected to fail syntax analysis
EXPECTED_SYNTAX_FAILURES = {
    "2_var_decl_outside_wazzup.lol",
    "6_elseif_without_if.lol",
    "7_else_without_if.lol",
    "8_nested_all_of_any_of.lol",
    "9_nested_smoosh.lol",
    "11_loop_mismatched_closing_name.lol",
    "13_obtw_not_on_own_line.lol",
    "20_function_call_missing_parameters.lol",
}


def test_file(path):
    expected_lexical_failure = (
        path.name in EXPECTED_LEXICAL_FAILURES
    )

    expected_syntax_failure = (
        path.name in EXPECTED_SYNTAX_FAILURES
    )

    try:
        # Provide input for programs that use GIMMEH
        input_data = ""

        if path.name == "gimmeh_test.lol":
            input_data = "Franz\n"
            
        process = subprocess.run(
            [sys.executable, str(INTERPRETER), str(path)],
            capture_output=True,
            text=True,
            input=input_data,
            timeout=10
        )
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"

    output = process.stdout + process.stderr

    if path.name == "gimmeh_test.lol":
        if "Hello, Franz" not in output:
            return False, "GIMMEH output did not match expected result"

    if expected_lexical_failure:
        if "Lexical Error:" in output:
            return True, "Expected lexical error detected"
        return False, "Expected lexical error was not detected"

    if expected_syntax_failure:
        if "Syntax Error:" in output:
            return True, "Expected syntax error detected"
        return False, "Expected syntax error was not detected"

    if "Lexical analysis successful!" not in output:
        return False, "Unexpected lexical analysis failure"

    if "Syntax is valid" not in output:
        return False, "Unexpected syntax analysis failure"

    if "Semantic analysis successful!" not in output:
        return False, "Semantic/runtime execution failed"

    return True, "Program executed successfully"


def main():
    if not INTERPRETER.exists():
        print("ERROR: interpreter.py not found.")
        return 1

    if not TEST_DIR.exists():
        print("ERROR: lolcode_tests folder not found.")
        return 1

    test_files = sorted(TEST_DIR.glob("*.lol"))

    if not test_files:
        print("ERROR: No LOLCODE test files found.")
        return 1

    passed = 0
    failed = 0

    print("======================================")
    print("     ITZ5 INTEGRATION TEST RUNNER")
    print("======================================\n")

    for path in test_files:
        success, message = test_file(path)

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"{status}: {path.name}")
        print(f"       {message}\n")

    total = passed + failed

    print("======================================")
    print("           FINAL RESULTS")
    print("======================================")
    print(f"Total test files : {total}")
    print(f"Passed           : {passed}")
    print(f"Failed           : {failed}")

    if failed == 0:
        print("\nALL INTEGRATION CHECKS PASSED!")
    else:
        print("\nSOME INTEGRATION CHECKS FAILED.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
