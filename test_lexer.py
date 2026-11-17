"""Regression tests for the ITZ5 LOLCODE lexical analyzer.

Run from this folder:
    python test_lexer.py

The professor's test files are copied into ./lolcode_tests.
Test 13 is intentionally lexically invalid because OBTW is not on its own line.
Other structurally invalid programs are expected to tokenize; syntax analysis
is responsible for rejecting their grammar.
"""

from pathlib import Path
from lexical_analyzer import getLexemes

TEST_DIR = Path(__file__).parent / "lolcode_tests"

EXPECTED_LEXICAL_FAILURES = {
    "13_obtw_not_on_own_line.lol",
}


def main():
    passed = 0
    failed = 0

    for path in sorted(TEST_DIR.glob("*.lol")):
        result = getLexemes(path.read_text(encoding="utf-8"))
        should_fail = path.name in EXPECTED_LEXICAL_FAILURES
        actual_fail = result is None
        ok = actual_fail == should_fail

        if ok:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"{status}: {path.name} "
              f"(expected {'LEXICAL ERROR' if should_fail else 'TOKENS'}, "
              f"got {'LEXICAL ERROR' if actual_fail else 'TOKENS'})")

    print(f"\nResult: {passed} passed, {failed} failed, "
          f"{passed + failed} total test files.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
