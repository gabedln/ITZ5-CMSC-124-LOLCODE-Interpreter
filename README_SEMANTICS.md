# ITZ5 Semantic Analyzer

## What it does

`semantics.py` is the runtime/semantic phase for the CMSC 124 LOLCODE interpreter. It consumes the line-based token table returned by `lexical_analyzer.getLexemes()` and executes the program.

Implemented behavior:

- Symbol table entries in `[identifier, value, data_type]` form, including implicit `IT`.
- `NOOB`, `TROOF`, `NUMBR`, `NUMBAR`, and `YARN` values with dynamic variable types.
- Literal and variable evaluation; prefix arithmetic, Boolean, and comparison operations.
- `SMOOSH`, `MAEK`, and `IS NOW A`.
- `VISIBLE` (concatenates operands without inserting spaces) and `GIMMEH`.
- `O RLY?`, `YA RLY`, `MEBBE`, `NO WAI`, and `OIC`.
- `WTF?`, `OMG`, `OMGWTF`, `GTFO`, and switch fall-through.
- `IM IN YR`, `UPPIN`, `NERFIN`, `TIL`, `WILE`, and `IM OUTTA YR`.
- Function definitions, local parameters, calls, return values, nested calls, and arity checks.
- Runtime errors for undeclared variables, invalid casts, division/modulo by zero, undefined functions, and invalid function argument counts.

## Run the semantic analyzer

From this directory:

```bash
python semantics.py
```

Run the semantic regression suite:

```bash
python test_semantics.py
```

## API for the GUI / other modules

```python
from semantics import runProgram

result = runProgram(source_code)

if result["success"]:
    print(result["output"])
else:
    print(result["errors"])

print(result["symbol_table"])
```

`runProgram` accepts optional test input values:

```python
result = runProgram(source_code, input_values=["Franz", "20"])
```

It returns a dictionary with:

- `success`: whether execution completed without a semantic/runtime error;
- `output`: list of console output lines;
- `symbol_table`: list of `[identifier, value, data_type]` rows;
- `errors`: list of error messages.

Compatibility helpers are also provided: `executeProgram`, `getSymbolTable`, and `getConsoleOutput`.

## Important phase boundary

The semantic analyzer is intended to receive a program that has already passed lexical and syntax analysis. It evaluates runtime meaning and values; it is not a replacement for the syntax analyzer. The current syntax analyzer in the project is still a separate component and should be connected before treating `runProgram` as the final end-to-end Execute button pipeline.

The project specification says `VISIBLE` concatenates operands and adds a newline. Therefore `VISIBLE "Hello" name` produces `Hellovalue`, not `Hello value`. Use a YARN literal containing a space when a space is needed.
