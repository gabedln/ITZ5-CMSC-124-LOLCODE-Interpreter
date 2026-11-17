"""
LOLCODE lexical analyzer for the ITZ5 CMSC 124 project.

Public functions retained for compatibility:
    stripComments(code) -> cleaned source string, or None on malformed comments
    getLexemes(code) -> lexical table (one row per source line), or None on lexical error

Each token is represented as [lexeme, classification].
YARN literals retain the existing three-token representation:
    ['"', 'String Delimiter'], [contents, 'YARN Literal'], ['"', 'String Delimiter']
"""

import re


# Longest keywords must be checked first (e.g. "IM OUTTA YR" before "IM").
KEYWORDS = [
    # Program and declaration delimiters
    ("KTHXBYE", "Code Delimiter"),
    ("WAZZUP", "Variable Declaration Delimiter"),
    ("BUHBYE", "Variable Declaration Delimiter"),
    ("HAI", "Code Delimiter"),

    # Variable declarations and assignment
    ("I HAS A", "Variable Declaration"),
    ("ITZ", "Variable Assignment"),
    ("R", "Variable Assignment"),

    # Arithmetic
    ("PRODUKT OF", "Multiplication Operation"),
    ("QUOSHUNT OF", "Division Operation"),
    ("SMALLR OF", "Min Operation"),
    ("BIGGR OF", "Max Operation"),
    ("SUM OF", "Addition Operation"),
    ("DIFF OF", "Subtraction Operation"),
    ("MOD OF", "Modulo Operation"),

    # Boolean and comparison
    ("BOTH SAEM", "Equality Operation"),
    ("DIFFRINT", "Inequality Operation"),
    ("BOTH OF", "AND Operation"),
    ("EITHER OF", "OR Operation"),
    ("WON OF", "XOR Operation"),
    ("ANY OF", "Infinite OR Operation"),
    ("ALL OF", "Infinite AND Operation"),
    ("NOT", "NOT Operation"),

    # String and type conversion
    ("SMOOSH", "String Concatenation"),
    ("IS NOW A", "Type Casting Operation"),
    ("MAEK", "Type Casting"),
    ("A", "Type Casting Qualifier"),

    # Input/output
    ("VISIBLE", "Output Keyword"),
    ("GIMMEH", "Input Keyword"),

    # Conditional and switch
    ("O RLY?", "Conditional Statement Delimiter"),
    ("YA RLY", "If"),
    ("NO WAI", "Else"),
    ("MEBBE", "Else If"),
    ("WTF?", "Switch Case Delimiter"),
    ("OMGWTF", "Default"),
    ("OMG", "Case"),
    ("OIC", "Flow Control Delimiter"),

    # Loops
    ("IM OUTTA YR", "End of Loop Block"),
    ("IM IN YR", "Loop Keyword"),
    ("UPPIN", "Increment"),
    ("NERFIN", "Decrement"),
    ("TIL", "Until Loop"),
    ("WILE", "While Loop"),
    ("YR", "Loop Identifier"),

    # Functions
    ("HOW IZ I", "Function Definition"),
    ("IF U SAY SO", "Function Delimiter"),
    ("FOUND YR", "Function Return Value"),
    ("I IZ", "Function Call"),
    ("GTFO", "Function Return"),
    ("MKAY", "End of Infinite Arity / Function Call"),

    # Required operand separator
    ("AN", "Delimiter"),
]

KEYWORDS.sort(key=lambda item: len(item[0]), reverse=True)

KEYWORD_SET = {word for word, _ in KEYWORDS}
TYPE_NAMES = {"TROOF", "NOOB", "NUMBR", "NUMBAR", "YARN"}
TROOF_VALUES = {"WIN", "FAIL"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
NUMBR_RE = re.compile(r"^-?[0-9]+$")
NUMBAR_RE = re.compile(r"^-?[0-9]+\.[0-9]+$")


def _keyword_at(text, position):
    """Return (keyword, classification) if a keyword begins at position."""
    for keyword, classification in KEYWORDS:
        end = position + len(keyword)
        if text[position:end] != keyword:
            continue

        # Keywords consisting of letters/spaces must end at a token boundary.
        if keyword[-1].isalnum() or keyword[-1] == "?":
            if end < len(text) and (text[end].isalnum() or text[end] == "_"):
                continue
        return keyword, classification
    return None


def stripComments(code):
    """
    Remove BTW comments and OBTW...TLDR blocks.

    BTW may follow a statement. OBTW and TLDR must be standalone lines;
    an optional BTW comment may follow either delimiter.
    Returns None for malformed or unterminated block comments.
    """
    if not isinstance(code, str):
        return None

    output = []
    in_block = False

    for original_line in code.splitlines():
        line = original_line.strip()

        if not line:
            output.append("")
            continue

        # Locate BTW only when it occurs outside a quoted YARN.
        def remove_btw_comment(source):
            in_string = False
            i = 0
            while i < len(source):
                if source[i] == '"':
                    in_string = not in_string
                    i += 1
                    continue
                if not in_string and source.startswith("BTW", i):
                    before_ok = i == 0 or source[i - 1].isspace()
                    after = i + 3
                    after_ok = after == len(source) or source[after].isspace()
                    if before_ok and after_ok:
                        return source[:i].rstrip()
                i += 1
            return source.rstrip()

        line_without_btw = remove_btw_comment(line).strip()

        if in_block:
            if line_without_btw == "TLDR":
                in_block = False
            elif line_without_btw.startswith("TLDR "):
                # TLDR must be alone, except for a BTW comment.
                return None
            elif "OBTW" in line_without_btw or line_without_btw == "TLDR":
                return None
            output.append("")
            continue

        if line_without_btw == "OBTW":
            in_block = True
            output.append("")
            continue

        if line_without_btw == "TLDR" or line_without_btw.startswith("TLDR "):
            return None

        # OBTW anywhere else is invalid: it cannot share a statement line.
        if re.search(r"(?<![A-Za-z0-9_])OBTW(?![A-Za-z0-9_])", line_without_btw):
            return None

        output.append(line_without_btw)

    if in_block:
        return None

    return "\n".join(output)


def _classify_word(word, previous_tokens):
    """Classify a non-keyword, non-string token."""
    if NUMBR_RE.fullmatch(word):
        return "NUMBR Literal"
    if NUMBAR_RE.fullmatch(word):
        return "NUMBAR Literal"
    if word in TROOF_VALUES:
        return "TROOF Literal"
    if word in TYPE_NAMES:
        return "TYPE Literal"
    if IDENTIFIER_RE.fullmatch(word):
        if previous_tokens:
            previous_lexeme = previous_tokens[-1][0]
            if previous_lexeme in ("HOW IZ I", "I IZ"):
                return "Function Identifier"
            if previous_lexeme in ("IM IN YR", "IM OUTTA YR"):
                return "Loop Label"
        if word in KEYWORD_SET:
            return None
        return "Variable Identifier"
    return None


def _tokenize_line(line):
    """Tokenize one source line. Return a list of tokens or None."""
    tokens = []
    i = 0
    length = len(line)

    while i < length:
        if line[i].isspace():
            i += 1
            continue

        # YARN: keep every character between the paired double quotes.
        if line[i] == '"':
            closing = line.find('"', i + 1)
            if closing == -1:
                return None
            tokens.append(['"', "String Delimiter"])
            tokens.append([line[i + 1:closing], "YARN Literal"])
            tokens.append(['"', "String Delimiter"])
            i = closing + 1
            continue

        # The VISIBLE concatenation operator is a separate token.
        if line[i] == "+":
            tokens.append(["+", "Concatenation Delimiter"])
            i += 1
            continue

        keyword_match = _keyword_at(line, i)
        if keyword_match:
            lexeme, classification = keyword_match
            tokens.append([lexeme, classification])
            i += len(lexeme)
            continue

        # Read a whitespace-delimited atom. Punctuation not defined by the
        # language remains part of the atom and will fail classification.
        start = i
        while i < length and not line[i].isspace() and line[i] != '"':
            if line[i] == "+":
                break
            i += 1

        if i == start:
            return None

        atom = line[start:i]
        classification = _classify_word(atom, tokens)
        if classification is None:
            return None
        tokens.append([atom, classification])

    return tokens


def getLexemes(code):
    """
    Return the lexical table as rows of [lexeme, classification] tokens.

    The first HAI and final KTHXBYE are retained as their own rows.
    Function definitions before HAI are permitted by the project specs.
    This phase checks lexical validity, not statement grammar or semantics.
    """
    cleaned = stripComments(code)
    if cleaned is None:
        return None

    source_lines = cleaned.splitlines()
    # Keep non-empty meaningful lines while preserving each source statement
    # as a separate row. Blank/comment-only lines do not produce rows.
    meaningful = [(number, line.strip())
                  for number, line in enumerate(source_lines, start=1)
                  if line.strip()]

    if not meaningful:
        return None

    # Find the single main-program HAI...KTHXBYE region.
    hai_positions = [idx for idx, (_, line) in enumerate(meaningful) if line == "HAI"]
    kthx_positions = [idx for idx, (_, line) in enumerate(meaningful) if line == "KTHXBYE"]

    if len(hai_positions) != 1 or len(kthx_positions) != 1:
        return None

    hai_index = hai_positions[0]
    kthx_index = kthx_positions[0]
    if hai_index >= kthx_index:
        return None

    # Anything outside HAI...KTHXBYE must be a function definition region.
    # The lexer recognizes the tokens; detailed function placement/grammar
    # is left to the syntax analyzer.
    table = []
    for index, (line_number, line) in enumerate(meaningful):
        if line == "HAI":
            table.append([["HAI", "Code Delimiter"]])
            continue
        if line == "KTHXBYE":
            table.append([["KTHXBYE", "Code Delimiter"]])
            continue

        row = _tokenize_line(line)
        if row is None:
            return None
        table.append(row)

    # Reject non-function tokens outside the main program. This is only a
    # lexical envelope check; function-body grammar is handled by the parser.
    function_depth = 0
    for index, (_, line) in enumerate(meaningful):
        row = table[index]
        if index < hai_index or index > kthx_index:
            if row and row[0][0] == "HOW IZ I":
                function_depth += 1
            elif row and row[0][0] == "IF U SAY SO":
                if function_depth == 0:
                    return None
                function_depth -= 1
            elif function_depth == 0:
                return None
    if function_depth != 0:
        return None

    return table


if __name__ == "__main__":
    sample = """HAI
WAZZUP
I HAS A message ITZ "Hello, world!"
BUHBYE
VISIBLE message
KTHXBYE"""
    result = getLexemes(sample)
    if result is None:
        print("Lexical error.")
    else:
        print("----------- Lexical Table -----------")
        for row in result:
            for lexeme, classification in row:
                print(f"{lexeme:<20} | {classification}")
        print("------------------------------------")
