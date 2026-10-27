import re
from dataclasses import dataclass


# Each detected lexeme will be stored as a Token
@dataclass
class Token:
   lexeme: str
   token_type: str
   line: int
   column: int


# LOLCODE keywords based on project specifications
KEYWORDS = [
   # Program structure and variable declarations
   "HAI", "KTHXBYE", "WAZZUP", "BUHBYE", "I HAS A", "ITZ", "R", "IS NOW A",
   "IT", "NOOB", "NUMBR", "NUMBAR", "YARN", "TROOF", "WIN", "FAIL",

   # Input and output
   "VISIBLE", "GIMMEH",

   # Arithmetic operations
   "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF",

   # String concatenation
   "SMOOSH",

   # Boolean operations
   "BOTH OF", "EITHER OF", "WON OF", "NOT", "ALL OF", "ANY OF",

   # Comparison operations
   "BOTH SAEM", "DIFFRINT",

   # Typecasting
   "MAEK", "A",

   # Conditional statements
   "O RLY?", "YA RLY", "MEBBE", "NO WAI", "OIC",

   # Switch-case statements
   "WTF?", "OMG", "OMGWTF", "GTFO",

   # Loops
   "IM IN YR", "IM OUTTA YR", "UPPIN", "NERFIN", "TIL", "WILE",

   # Functions
   "HOW IZ I", "IF U SAY SO", "FOUND YR", "I IZ", "YR", "AN"
]


# Match longer keywords before shorter keywords
KEYWORDS.sort(key=len, reverse=True)


# A keyword must not match part of a longer identifier
KEYWORD_PATTERN = re.compile(
   r"(?<![A-Za-z0-9_])(?:"
   + "|".join(
       re.escape(keyword).replace(r"\ ", r"\s+")
       for keyword in KEYWORDS
   )
   + r")(?![A-Za-z0-9_])",
   re.IGNORECASE,
)


# Match one lexeme at a time
TOKEN_PATTERN = re.compile(
   r'"[^"\n]*"'                # String literal
   r'|“[^”\n]*”'               # Curly-quoted string literal
   r'|[-]?\d+\.\d+'            # Floating-point number
   r'|[-]?\d+'                 # Integer
   r'|[A-Za-z][A-Za-z0-9_]*'   # Identifier
   r'|[^\s]',                  # Any other non-whitespace character
)


# Remove BTW comments without removing text inside strings
def remove_inline_comment(line):
   in_string = False
   quote = None
   i = 0


   while i < len(line):
       char = line[i]


       if char in ('"', '“', '”'):
           if not in_string:
               in_string = True
               quote = '”' if char == '“' else char
           elif char == quote:
               in_string = False
               quote = None


       if not in_string and line[i:i + 3].upper() == "BTW":
           before_ok = i == 0 or line[i - 1].isspace()
           after_ok = (i + 3 == len(line) or line[i + 3].isspace())


           if before_ok and after_ok:
               return line[:i]


       i += 1


   return line


# Determine the token type of a lexeme
def classify_lexeme(lexeme):
   if KEYWORD_PATTERN.fullmatch(lexeme):
       if lexeme.upper() == "IT":
           return "IMPLICIT_VARIABLE"
       return "KEYWORD"


   if (lexeme.startswith('"') and lexeme.endswith('"')) or (lexeme.startswith("“") and lexeme.endswith("”")):
       return "STRING_LITERAL"


   if re.fullmatch(r"-?\d+\.\d+", lexeme):
       return "FLOAT_LITERAL"


   if re.fullmatch(r"-?\d+", lexeme):
       return "INTEGER_LITERAL"


   if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", lexeme):
       return "IDENTIFIER"


   return "INVALID"

# Check whether a line contains a specific keyword
def is_comment_keyword(line, keyword):
    first_word = line.split()

    if len(first_word) == 0:
        return False

    return first_word[0].upper() == keyword


# Main lexical analyzer
def tokenize(source):
    tokens = []
    errors = []
    in_comment = False
    comment_start = 0

    # Read source code line by line
    lines = source.splitlines()

    for line_number, line in enumerate(lines, 1):

        # Skip lines inside multiline comments
        if in_comment:
            if is_comment_keyword(line, "TLDR"):
                in_comment = False
                # TLDR must be alone or followed by BTW comment
                remaining = line.lstrip()[4:].strip()

                if remaining and not remaining.upper().startswith("BTW"):
                    errors.append(
                        f"Line {line_number}: Invalid text after TLDR"
                    )

            continue

        # Remove single-line comments
        line = remove_inline_comment(line)

        # Skip empty lines
        if line.strip() == "":
            continue

        # Check for multiline comment start
        if is_comment_keyword(line, "OBTW"):
            in_comment = True
            comment_start = line_number
            continue

        # Detect TLDR without OBTW
        if is_comment_keyword(line, "TLDR"):
            errors.append(
                f"Line {line_number}: TLDR without OBTW"
            )
            continue

        # Scan characters in the current line
        position = 0

        while position < len(line):
            # Ignore whitespace
            if line[position].isspace():
                position += 1
                continue

            # Detect invalid multiline comment placement
            if re.match(r"OBTW\b|TLDR\b", line[position:], re.IGNORECASE):
                errors.append(
                    f"Line {line_number}, Column {position + 1}: "
                    "Multiline comment keyword must be on its own line"
                )
                break

            # Check for unterminated strings
            if line[position] in ('"', '“'):
                quote = '”' if line[position] == '“' else '"'
                if quote not in line[position + 1:]:
                    errors.append(
                        f"Line {line_number}, Column {position + 1}: "
                        "Untrminated string literal"
                        )
                    break

            # Match LOLCODE keywords first
            keyword_match = KEYWORD_PATTERN.match(line, position)

            if keyword_match:
                lexeme = keyword_match.group()
                token_type = classify_lexeme(lexeme)

                tokens.append(Token(lexeme, token_type, line_number, position + 1))

                position = keyword_match.end()
                continue

            # Match other lexemes
            match = TOKEN_PATTERN.match(line, position)

            if match:
                lexeme = match.group()
                token_type = classify_lexeme(lexeme)

                if token_type == "INVALID":
                    errors.append(
                    f"Line {line_number}, Column {position + 1}: "
                    f"Invalid lexeme '{lexeme}'"
                    )

                else:
                    tokens.append(Token(lexeme, token_type, line_number, position + 1))

                position = match.end()

            else:
                errors.append(
                    f"Line {line_number}, Column {position + 1}: "
                    "Unknown character"
                )

                position += 1

    # Check for unclosed multiline comments
    if in_comment:
        errors.append(
            f"Line {comment_start}: OBTW comment was not closed with TLDR"
        )

    return tokens, errors


# Test the lexical analyzer
if __name__ == "__main__":

    filename = "sample.lol"

    try:
        with open(filename, "r", encoding="utf-8") as file:
            source = file.read()

        tokens, errors = tokenize(source)

        print("\nLEXICAL ANALYSIS")
        print("-" * 70)

        print(f"{'LEXEME':<20} {'TOKEN TYPE':<22} {'LINE':<8} {'COLUMN'}")
        print("-" * 70)

        for token in tokens:
            print(
                f"{token.lexeme:<20} "
                f"{token.token_type:<22} "
                f"{token.line:<8} "
                f"{token.column}"
            )

        print("-" * 70)

        if len(errors) > 0:
            print("\nLEXICAL ERRORS:")

            for error in errors:
                print(error)

        else:
            print("\nNo lexical errors found.")
            
    except FileNotFoundError:
        print(f"Error: {filename} was not found.")

