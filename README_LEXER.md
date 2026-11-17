# ITZ5 — Updated LOLCODE Lexical Analyzer

This folder contains the updated lexical-analysis phase and the professor-provided
LOLCODE test programs.

## Files

- `lexical_analyzer.py` — handwritten comment stripper and tokenizer.
- `lexemes.md` — regular-expression and token-classification reference.
- `test_lexer.py` — regression test runner.
- `lolcode_tests/` — the 29 `.lol` files from `silogegg.zip`.

## Run the lexer tests

Use Python 3.8+:

```bash
python test_lexer.py
```

Expected result for the supplied test set: **29 passed, 0 failed**.

Test 13 (`13_obtw_not_on_own_line.lol`) is expected to return a lexical error:
the project specification requires `OBTW` and `TLDR` to be on their own lines.
The other test files should produce tokens at the lexical phase. Some of them
contain syntax errors by design; those must be rejected by the syntax analyzer,
not by the lexer.

## Use from the existing project

Keep `lexical_analyzer.py` in the same folder as the other project modules:

```python
from lexical_analyzer import getLexemes

table = getLexemes(source_code)
if table is None:
    print("Lexical error")
else:
    for row in table:
        for lexeme, classification in row:
            print(lexeme, classification)
```

The public function names `stripComments()` and `getLexemes()` are preserved.
Tokens retain the `[lexeme, classification]` representation, grouped by source
line. YARN literals retain the project's existing three-token representation
(opening delimiter, contents, closing delimiter).

## Scope

This update completes the lexical phase and prepares its output for later
syntax-analysis work. It does not implement or repair the parser, semantic
analyzer, or GUI. In particular, syntax validation (variable declaration
placement, orphan conditional branches, matching loop labels, operation arity,
and function argument counts) belongs to the syntax analyzer.
