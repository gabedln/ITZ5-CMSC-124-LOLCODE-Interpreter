
import sys

from lexical_analyzer import getLexemes
from syntax_analyzer import parseProgram
from semantics import runProgram


def display_source(source_code):
    print("\n========== SOURCE CODE ==========")
    print(source_code, end="" if source_code.endswith("\n") else "\n")
    print("=================================")


def display_lexemes(tokens):
    print("\n========== LEXICAL ANALYSIS ==========")
    print(f"{'No.':<6}{'Lexeme':<40}{'Classification'}")
    print("-" * 80)

    count = 0

    def print_tokens(items):
        nonlocal count

        for item in items:
            if isinstance(item, (list, tuple)):
                # A token is represented as [lexeme, classification].
                if (
                    len(item) >= 2
                    and isinstance(item[0], str)
                    and isinstance(item[1], str)
                ):
                    count += 1
                    print(f"{count:<6}{item[0]:<40}{item[1]}")
                else:
                    # Handle nested token lists.
                    print_tokens(item)

    print_tokens(tokens)

    if count == 0:
        print("No lexemes found.")

    print("-" * 80)


def display_symbol_table(symbol_table):
    print("\n========== SYMBOL TABLE ==========")
    print(f"{'Identifier':<25}{'Value':<20}{'Type'}")
    print("-" * 65)

    for entry in symbol_table:
        identifier = entry[0]
        value = entry[1]
        data_type = entry[2] if len(entry) > 2 else ""

        print(f"{identifier:<25}{str(value):<20}{data_type}")

    print("-" * 80)


def display_output(output):
    print("\n========== PROGRAM OUTPUT ==========")

    if not output:
        print("(No output)")
    else:
        for line in output:
            print(line)

    print("====================================")


def run_file(filename):
    # Read the LOLCODE source file.
    try:
        with open(filename, "r", encoding="utf-8") as file:
            source_code = file.read()

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    except OSError as error:
        print(f"Error reading file: {error}")
        return

    # 1. Display the source code.
    display_source(source_code)

    # 2. Perform lexical analysis.
    tokens = getLexemes(source_code)

    if tokens is None or isinstance(tokens, str):
        print("\nLexical Error: Invalid token or malformed comment.")
        return

    display_lexemes(tokens)
    print("Lexical analysis successful!")

    # 3. Perform syntax analysis.
    valid, message = parseProgram(source_code)

    print("\nSyntax Analysis:", message)

    if not valid:
        print("Syntax Error:", message)
        return

    # 4. Perform semantic analysis and execute the program.
    result = runProgram(tokens)

    if not result["success"]:
        print("\nRuntime/Semantic Error:")
        for error in result["errors"]:
            print("-", error)
        return

    print("\nSemantic analysis successful!")

    # 5. Display the symbol table.
    display_symbol_table(result["symbol_table"])

    # 6. Display the program output last.
    display_output(result["output"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <filename.lol>")
    else:
        run_file(sys.argv[1])
