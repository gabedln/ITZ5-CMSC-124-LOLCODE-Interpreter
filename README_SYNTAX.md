# ITZ5 LOLCODE Syntax Analyzer

## Files
- `lexical_analyzer.py` — lexical analysis; returns rows of `[lexeme, classification]` tokens.
- `syntax_analyzer.py` — manual recursive-descent syntax analyzer.
- `lexemes.md` — lexical patterns and token classifications.
- `test_lexer.py` — lexical regression tests.
- `test_syntax.py` — syntax regression tests.
- `lolcode_tests/` — professor-provided test programs.

## Run the syntax analyzer
From this directory:

```bash
python syntax_analyzer.py path/to/program.lol
```

Or use the API:

```python
from syntax_analyzer import checkSyntax, parseProgram

valid = checkSyntax(source_code)              # bool
valid, message = parseProgram(source_code)    # bool and explanation
```

## Run regression tests

```bash
python test_lexer.py
python test_syntax.py
```

The parser is handwritten Python code and does not use Flex/Lex, YACC/Bison, PEG, or parser generators.

## Scope
The syntax analyzer validates program delimiters, optional WAZZUP/BUHBYE declaration section, declarations, assignments, expressions, output/input, typecasting statements, if-then, switch-case, loops, and function definitions/calls. It reports syntax validity only; runtime behavior, variable existence/types, and evaluation belong to semantic analysis.
