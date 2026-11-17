
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "lolcode_tests"
INTERPRETER = BASE_DIR / "interpreter.py"

EXPECTED_ERRORS = {
    "13_obtw_not_on_own_line.lol",
    "2_var_decl_outside_wazzup.lol",
    "6_elseif_without_if.lol",
    "7_else_without_if.lol",
    "8_nested_all_of_any_of.lol",
    "9_nested_smoosh.lol",
    "11_loop_mismatched_closing_name.lol",
    "20_function_call_missing_parameters.lol",
}

for path in sorted(TEST_DIR.glob("*.lol")):
    if path.name in EXPECTED_ERRORS:
        continue

    input_data = "Franz\n" if path.name == "gimmeh_test.lol" else ""

    result = subprocess.run(
        [sys.executable, str(INTERPRETER), str(path)],
        capture_output=True,
        text=True,
        input=input_data,
        timeout=10
    )

    print("\n" + "=" * 55)
    print("FILE:", path.name)
    print("=" * 55)

    output = result.stdout

    if "=== PROGRAM OUTPUT ===" in output:
        program_output = output.split("=== PROGRAM OUTPUT ===", 1)[1]
        program_output = program_output.split("=== SYMBOL TABLE ===", 1)[0]
        print(program_output.strip())
    else:
        print("No program output or execution failed.")
        print(output)
        if result.stderr:
            print(result.stderr)
