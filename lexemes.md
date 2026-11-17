# LOLCODE Lexical Patterns — ITZ5

This document describes the patterns implemented in `lexical_analyzer.py`.
The lexer is handwritten in Python; it does not use Flex/Lex, YACC/Bison, PEG,
or a lexer generator.

## 1. Identifiers

| Lexeme class | Regular expression | Notes |
|---|---|---|
| Variable Identifier | `^[A-Za-z][A-Za-z0-9_]*$` | Starts with a letter; may contain letters, digits, underscores |
| Function Identifier | `^[A-Za-z][A-Za-z0-9_]*$` | Same spelling rule; classified by its position after `HOW IZ I` or `I IZ` |
| Loop Label | `^[A-Za-z][A-Za-z0-9_]*$` | Same spelling rule; classified by its position after `IM IN YR` or `IM OUTTA YR` |

## 2. Literals

| Lexeme class | Regular expression / form | Notes |
|---|---|---|
| NUMBR Literal | `^-?[0-9]+$` | Integer; a leading `+` is not allowed |
| NUMBAR Literal | `^-?[0-9]+\.[0-9]+$` | Decimal number with exactly one decimal point and digits on both sides |
| YARN Literal | `".*"` (scanned between paired double quotes) | Spaces are preserved; the quote delimiters are emitted as separate tokens |
| TROOF Literal | `^(WIN|FAIL)$` | Boolean literal |
| TYPE Literal | `^(TROOF|NOOB|NUMBR|NUMBAR|YARN)$` | Type names used by casting |

The YARN token representation remains compatible with the existing project:
`"` as `String Delimiter`, the string contents as `YARN Literal`, and the closing
`"` as `String Delimiter`.

## 3. Keywords and classifications

The lexer recognizes these exact, uppercase keyword spellings. Multi-word
keywords are matched before shorter keywords to avoid partial matches.

| Keyword | Classification |
|---|---|
| `HAI`, `KTHXBYE` | Code Delimiter |
| `WAZZUP`, `BUHBYE` | Variable Declaration Delimiter |
| `I HAS A` | Variable Declaration |
| `ITZ`, `R` | Variable Assignment |
| `SUM OF` | Addition Operation |
| `DIFF OF` | Subtraction Operation |
| `PRODUKT OF` | Multiplication Operation |
| `QUOSHUNT OF` | Division Operation |
| `MOD OF` | Modulo Operation |
| `BIGGR OF` | Max Operation |
| `SMALLR OF` | Min Operation |
| `AN` | Delimiter |
| `BOTH OF` | AND Operation |
| `EITHER OF` | OR Operation |
| `WON OF` | XOR Operation |
| `NOT` | NOT Operation |
| `ALL OF` | Infinite AND Operation |
| `ANY OF` | Infinite OR Operation |
| `BOTH SAEM` | Equality Operation |
| `DIFFRINT` | Inequality Operation |
| `SMOOSH` | String Concatenation |
| `MAEK` | Type Casting |
| `A` | Type Casting Qualifier |
| `IS NOW A` | Type Casting Operation |
| `VISIBLE` | Output Keyword |
| `GIMMEH` | Input Keyword |
| `+` | Concatenation Delimiter |
| `O RLY?` | Conditional Statement Delimiter |
| `YA RLY` | If |
| `MEBBE` | Else If |
| `NO WAI` | Else |
| `OIC` | Flow Control Delimiter |
| `WTF?` | Switch Case Delimiter |
| `OMG` | Case |
| `OMGWTF` | Default |
| `IM IN YR` | Loop Keyword |
| `IM OUTTA YR` | End of Loop Block |
| `UPPIN` | Increment |
| `NERFIN` | Decrement |
| `YR` | Loop Identifier |
| `TIL` | Until Loop |
| `WILE` | While Loop |
| `HOW IZ I` | Function Definition |
| `IF U SAY SO` | Function Delimiter |
| `FOUND YR` | Function Return Value |
| `GTFO` | Function Return |
| `I IZ` | Function Call |
| `MKAY` | End of Infinite Arity / Function Call |

## 4. Comments

| Form | Lexical behavior |
|---|---|
| `BTW comment` | Removes the comment from `BTW` to the end of that line |
| `statement BTW comment` | Keeps the statement and removes the trailing comment |
| `OBTW` on its own line | Begins a multiline comment |
| `TLDR` on its own line | Ends a multiline comment |

`OBTW` and `TLDR` may have a trailing `BTW` comment, but they cannot share
their line with a program statement. An unmatched `TLDR`, nested `OBTW`, or
unclosed `OBTW` block is rejected.

## 5. Lexical assumptions and boundaries

- One statement per line; newline separates statement rows.
- Indentation and leading/trailing whitespace are ignored.
- Keyword spelling is uppercase and exact.
- Keyword matches require a token boundary, so a keyword is not recognized
  as the prefix of a longer identifier.
- Spaces inside YARN literals are retained.
- The lexer identifies tokens. It does not decide whether a sequence of valid
  tokens forms a valid statement or whether variables are declared correctly;
  those checks belong to later phases.
- Function definitions may appear outside the `HAI`–`KTHXBYE` main-program
  region, as allowed by the project specification.

## 6. Error cases detected by the lexer

- Unterminated YARN literal.
- Invalid or unrecognized character/token.
- Malformed multiline comment delimiters.
- Missing, repeated, or reversed `HAI` / `KTHXBYE` delimiters.
- Non-function source content outside the main program region.

Grammar errors such as an orphan `MEBBE`, mismatched loop labels, or a variable
declaration outside `WAZZUP` are not lexical errors. The lexer still returns
those lexemes so the syntax analyzer can reject the structure.
