# How to Use `interpreter.py`

## 1. Overview

`interpreter.py` is the main program used to run a LOLCODE source file
(`.lol`). It coordinates the project's three main components:

1.  **Lexical analyzer** -- identifies lexemes and their
    classifications.
2.  **Syntax analyzer** -- checks whether the source code follows the
    supported LOLCODE syntax.
3.  **Semantic analyzer / interpreter** -- evaluates and executes the
    program.

After a successful run, the interpreter displays the source code,
lexical analysis results, symbol table, and program output.

## 2. Requirements

Before running the interpreter, make sure that:

-   Python 3 is installed.
-   The project files are in the same project directory.
-   The LOLCODE source file you want to run has a `.lol` extension.

The interpreter uses Python's standard library and the project's own
Python modules. No additional third-party package installation is
required.

The following files must remain available in the project directory:

-   `interpreter.py`
-   `lexical_analyzer.py`
-   `syntax_analyzer.py`
-   `semantics.py`

The `lolcode_tests` folder contains sample LOLCODE programs that can be
used for testing.

## 3. Open the Project Directory

Open PowerShell or a terminal and navigate to the project directory.

Example using PowerShell:

``` powershell
cd "C:\Users\Admin\Pictures\bang\ITZ5_Lexical_Syntax_Semantic_Analyzer_Update"
```

Make sure that the terminal is currently inside the folder containing
`interpreter.py`.

## 4. Run the Interpreter

Use the following command:

``` powershell
python interpreter.py <filename.lol>
```

Replace `<filename.lol>` with the path or filename of the LOLCODE
program you want to execute.

### Example: Run a test file

``` powershell
python interpreter.py lolcode_tests/1.3_var_decl_no_initial_value.lol
```

Another example:

``` powershell
python interpreter.py lolcode_tests/25_arithmetic_statements.lol
```

You can also provide the path to a `.lol` file located elsewhere. If the
path contains spaces, enclose it in quotation marks:

``` powershell
python interpreter.py "C:\Users\Admin\Desktop\my program.lol"
```

## 5. Interpreter Output

When a LOLCODE file is processed, the interpreter displays the following
sections.

### A. Source Code

The complete contents of the selected `.lol` file are displayed first.

This allows the user to see which program is being processed.

### B. Lexical Analysis

The lexical analyzer identifies the lexemes in the source code and
assigns a classification to each one.

The displayed table contains:

  -----------------------------------------------------------------------
  Column                              Description
  ----------------------------------- -----------------------------------
  No.                                 The sequence number of the lexeme

  Lexeme                              The actual word, symbol, or literal
                                      found in the source code

  Classification                      The category assigned to the lexeme
  -----------------------------------------------------------------------

Examples of classifications include:

-   Code Delimiter
-   Variable Declaration
-   Variable Identifier
-   Variable Assignment
-   Output Keyword
-   NUMBR Literal
-   NUMBAR Literal
-   YARN Literal
-   TROOF Literal
-   Arithmetic and other operation classifications

If lexical analysis fails, the interpreter displays a lexical error and
stops processing the file.

### C. Syntax Analysis

The syntax analyzer checks whether the source code follows the grammar
rules supported by the project.

A successful syntax check displays:

``` text
Syntax Analysis: Syntax is valid
```

If the source code contains a syntax error, the interpreter displays the
error message and stops before semantic execution.

### D. Semantic Analysis

The semantic analyzer evaluates the program and checks for runtime or
semantic errors.

If semantic analysis succeeds, the interpreter displays:

``` text
Semantic analysis successful!
```

If an error occurs, the interpreter displays the runtime or semantic
error messages and stops before showing the final symbol table and
program output.

### E. Symbol Table

After successful execution, the interpreter displays the symbol table.

  Column       Description
  ------------ ------------------------------------------------------
  Identifier   The variable or identifier recorded during execution
  Value        Its value after the program has executed
  Type         Its current LOLCODE data type

The symbol table reflects the program's resulting state after execution.

### F. Program Output

The program's output is displayed last.

For example, statements using `VISIBLE` produce output in this section.
If the program has no output, the interpreter displays:

``` text
(No output)
```

## 6. Example Run

Command:

``` powershell
python interpreter.py lolcode_tests/25_arithmetic_statements.lol
```

The output is organized in this order:

``` text
========== SOURCE CODE ==========
[Contents of the selected LOLCODE file]

========== LEXICAL ANALYSIS ==========
No.   Lexeme                                  Classification
[Lexeme and classification rows]

Lexical analysis successful!

Syntax Analysis: Syntax is valid

Semantic analysis successful!

========== SYMBOL TABLE ==========
Identifier               Value               Type
[Identifier, value, and type rows]

========== PROGRAM OUTPUT ==========
[Program output]
```

The values and lexemes shown depend on the selected LOLCODE program.

## 7. Common Errors and Solutions

  ------------------------------------------------------------------------------------------------------
  Message or problem                                     Possible cause          What to do
  ------------------------------------------------------ ----------------------- -----------------------
  `Usage: python interpreter.py <filename.lol>`          No source-file argument Run the command again
                                                         was provided.           and include the `.lol`
                                                                                 file path.

  `Error: File '...' not found.`                         The filename or path is Check the file name and
                                                         incorrect, or the       location. Navigate to
                                                         terminal is in the      the project directory
                                                         wrong directory.        or provide the correct
                                                                                 path.

  `Error reading file: ...`                              The file could not be   Check that the file
                                                         read.                   exists and that you
                                                                                 have permission to
                                                                                 access it.

  `Lexical Error: Invalid token or malformed comment.`   The lexer encountered   Review the source code
                                                         an invalid token or     for invalid or
                                                         malformed comment.      incorrectly written
                                                                                 tokens and comments.

  `Syntax Error: ...`                                    The source code does    Review the reported
                                                         not follow the          syntax issue and
                                                         supported syntax.       correct the LOLCODE
                                                                                 statement.

  `Runtime/Semantic Error:`                              The program encountered Read the listed error
                                                         a semantic or runtime   messages and review the
                                                         problem during          relevant variables,
                                                         execution.              expressions, or
                                                                                 function calls.

  `python` is not recognized                             Python may not be       Install Python 3 or
                                                         installed or added to   configure the Python
                                                         the system PATH.        PATH, then reopen the
                                                                                 terminal.
  ------------------------------------------------------------------------------------------------------

## 8. Important Reminders

-   Run `interpreter.py` from the project directory, or provide the
    correct path to it.
-   Pass one LOLCODE source-file path as the command-line argument.
-   Keep `lexical_analyzer.py`, `syntax_analyzer.py`, and `semantics.py`
    in the project directory with `interpreter.py`.
-   Use a valid `.lol` source file as input.
-   The interpreter stops when lexical analysis, syntax analysis, or
    semantic execution reports an error.
-   The symbol table and program output are displayed only after
    successful semantic execution.

## 9. Quick Reference

``` powershell
# Navigate to the project directory
cd "C:\Users\Admin\Pictures\bang\ITZ5_Lexical_Syntax_Semantic_Analyzer_Update"

# Run a LOLCODE program
python interpreter.py lolcode_tests/25_arithmetic_statements.lol
```

**In short:** Open the project directory, run `python interpreter.py`
followed by the path to a `.lol` file, and review the analysis results,
symbol table, and program output in the terminal.
