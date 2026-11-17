"""Manual recursive-descent syntax analyzer for the ITZ5 LOLCODE project.

Public API retained: checkSyntax(code) -> bool
Additional API: parseProgram(code) -> (bool, error_message)

The parser consumes the [lexeme, classification] rows produced by
lexical_analyzer.getLexemes. It does not execute code or perform semantic checks.
"""
from lexical_analyzer import getLexemes

VALUE_CLASSES = {
    "NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "YARN Literal",
    "Variable Identifier", "Identifier", "Function Identifier", "Loop Label",
}
TYPE_NAMES = {"NOOB", "TROOF", "NUMBR", "NUMBAR", "YARN"}
BINARY_OPERATORS = {
    "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF",
    "BIGGR OF", "SMALLR OF", "BOTH OF", "EITHER OF", "WON OF",
    "BOTH SAEM", "DIFFRINT",
}
INFINITE_BOOLEAN = {"ALL OF", "ANY OF"}
ARITHMETIC = {"SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"}
BOOLEAN = {"BOTH OF", "EITHER OF", "WON OF", "NOT", "ALL OF", "ANY OF"}
COMPARISON = {"BOTH SAEM", "DIFFRINT"}

class SyntaxErrorLOL(Exception):
    pass

class ExpressionParser:
    def __init__(self, tokens, allow_smoosh=False, functions=None):
        self.tokens = tokens
        self.i = 0
        self.allow_smoosh = allow_smoosh
        self.functions = functions or {}

    def current(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def lex(self):
        t = self.current()
        return t[0] if t else None

    def cls(self):
        t = self.current()
        return t[1] if t else None

    def take(self, word=None, classification=None):
        t = self.current()
        if t is None:
            raise SyntaxErrorLOL("Unexpected end of statement")
        if word is not None and t[0] != word:
            raise SyntaxErrorLOL(f"Expected {word}, found {t[0]}")
        if classification is not None and t[1] != classification:
            raise SyntaxErrorLOL(f"Unexpected token {t[0]} ({t[1]})")
        self.i += 1
        return t

    def expression(self, inside_all_any=False, inside_smoosh=False):
        t = self.current()
        if t is None:
            raise SyntaxErrorLOL("Expected an expression")
        word, cls = t

        if cls == "String Delimiter":
            self.take(classification="String Delimiter")
            self.take(classification="YARN Literal")
            self.take('"', "String Delimiter")
            return
        if cls in VALUE_CLASSES or cls == "TYPE Literal":
            self.take()
            return

        if word in BINARY_OPERATORS:
            if inside_all_any and word in INFINITE_BOOLEAN:
                raise SyntaxErrorLOL("ALL OF and ANY OF cannot be nested")
            self.take()
            self.expression(inside_all_any=inside_all_any, inside_smoosh=inside_smoosh)
            self.take("AN", "Delimiter")
            self.expression(inside_all_any=inside_all_any, inside_smoosh=inside_smoosh)
            return

        if word == "NOT":
            self.take()
            self.expression(inside_all_any=inside_all_any, inside_smoosh=inside_smoosh)
            return

        if word in INFINITE_BOOLEAN:
            if inside_all_any:
                raise SyntaxErrorLOL("ALL OF and ANY OF cannot be nested")
            self.take()
            count = 0
            while self.lex() != "MKAY":
                if self.current() is None:
                    raise SyntaxErrorLOL(f"{word} is missing MKAY")
                if count:
                    self.take("AN", "Delimiter")
                self.expression(inside_all_any=True, inside_smoosh=inside_smoosh)
                count += 1
            if count < 2:
                raise SyntaxErrorLOL(f"{word} requires at least two operands")
            self.take("MKAY", "End of Infinite Arity / Function Call")
            return

        if word == "SMOOSH":
            if inside_smoosh:
                raise SyntaxErrorLOL("Nested SMOOSH is not supported")
            self.take()
            self.expression(inside_all_any=inside_all_any, inside_smoosh=True)
            while self.lex() == "AN":
                self.take("AN", "Delimiter")
                self.expression(inside_all_any=inside_all_any, inside_smoosh=True)
            return

        if word == "MAEK":
            self.take()
            self.expression(inside_all_any=inside_all_any, inside_smoosh=inside_smoosh)
            if self.lex() == "A":
                self.take("A", "Type Casting Qualifier")
            if self.lex() not in TYPE_NAMES:
                raise SyntaxErrorLOL("MAEK must be followed by a type")
            self.take()
            return

        if word == "I IZ":
            self.take()
            if self.cls() not in {"Function Identifier", "Variable Identifier", "Identifier"}:
                raise SyntaxErrorLOL("I IZ requires a function name")
            word_name = self.lex()
            self.take()
            argument_count = 0
            if self.lex() == "YR":
                self.take("YR", "Loop Identifier")
                self.expression(inside_all_any=inside_all_any, inside_smoosh=inside_smoosh)
                argument_count += 1
                while self.lex() == "AN":
                    self.take("AN", "Delimiter")
                    self.take("YR", "Loop Identifier")
                    self.expression(inside_all_any=inside_all_any, inside_smoosh=inside_smoosh)
                    argument_count += 1
            self.take("MKAY", "End of Infinite Arity / Function Call")
            if self.functions and word_name in self.functions and self.functions[word_name] != argument_count:
                raise SyntaxErrorLOL(f"Function {word_name} expects {self.functions[word_name]} argument(s), got {argument_count}")
            return

        raise SyntaxErrorLOL(f"Expected expression, found {word}")

    def complete(self):
        self.expression()
        if self.i != len(self.tokens):
            raise SyntaxErrorLOL(f"Unexpected token after expression: {self.lex()}")


def _parse_expr(tokens, functions=None):
    parser = ExpressionParser(tokens, functions=functions)
    parser.complete()


def _parse_output(tokens, functions=None):
    if len(tokens) < 2:
        raise SyntaxErrorLOL("VISIBLE requires at least one expression")
    p = ExpressionParser(tokens[1:], functions=functions)
    count = 0
    while p.i < len(p.tokens):
        p.expression()
        count += 1
        if p.i < len(p.tokens):
            if p.lex() == "+":
                p.take("+", "Concatenation Delimiter")
                if p.i >= len(p.tokens):
                    raise SyntaxErrorLOL("Trailing + in VISIBLE")
            # VISIBLE accepts adjacent expressions as separate operands.
            elif p.current()[1] in VALUE_CLASSES or p.lex() in BINARY_OPERATORS | INFINITE_BOOLEAN | {"NOT", "SMOOSH", "MAEK", "I IZ"}:
                pass
            else:
                raise SyntaxErrorLOL(f"Unexpected token in VISIBLE: {p.lex()}")
    if count == 0:
        raise SyntaxErrorLOL("VISIBLE requires an operand")


def _parse_declaration(tokens, functions=None):
    if len(tokens) < 2 or tokens[1][1] not in {"Variable Identifier", "Identifier"}:
        raise SyntaxErrorLOL("I HAS A requires a variable identifier")
    if len(tokens) == 2:
        return
    if tokens[2][0] != "ITZ":
        raise SyntaxErrorLOL("Unexpected token after declared variable")
    _parse_expr(tokens[3:], functions)


def _parse_assignment(tokens, functions=None):
    if len(tokens) < 3 or tokens[0][1] not in {"Variable Identifier", "Identifier"}:
        raise SyntaxErrorLOL("Assignment requires a variable on the left")
    if tokens[1][0] != "R":
        raise SyntaxErrorLOL("Expected R in assignment")
    _parse_expr(tokens[2:], functions)


def _parse_simple_statement(tokens, functions=None):
    if not tokens:
        return
    first = tokens[0][0]
    if first == "VISIBLE":
        _parse_output(tokens, functions)
    elif first == "GIMMEH":
        if len(tokens) != 2 or tokens[1][1] not in {"Variable Identifier", "Identifier"}:
            raise SyntaxErrorLOL("GIMMEH requires exactly one variable")
    elif first == "I HAS A":
        _parse_declaration(tokens)
    elif len(tokens) >= 3 and tokens[1][0] == "IS NOW A":
        if tokens[0][1] not in {"Variable Identifier", "Identifier"} or len(tokens) != 3 or tokens[2][0] not in TYPE_NAMES:
            raise SyntaxErrorLOL("Invalid IS NOW A typecast")
    elif len(tokens) >= 2 and tokens[1][0] == "R":
        _parse_assignment(tokens, functions)
    elif first in {"GTFO"}:
        if len(tokens) != 1:
            raise SyntaxErrorLOL("GTFO takes no operands")
    elif first == "FOUND YR":
        _parse_expr(tokens[1:], functions)
    elif first in {"O RLY?", "YA RLY", "NO WAI", "MEBBE", "OIC", "WTF?", "OMG", "OMGWTF", "IM IN YR", "IM OUTTA YR", "HOW IZ I", "IF U SAY SO"}:
        raise SyntaxErrorLOL(f"Misplaced block delimiter: {first}")
    else:
        _parse_expr(tokens, functions)


class ProgramParser:
    def __init__(self, rows):
        self.rows = rows
        self.i = 0
        self.declared = set()
        self.functions = {}

    def line(self):
        return self.rows[self.i] if self.i < len(self.rows) else None

    def word(self):
        row = self.line()
        return row[0][0] if row else None

    def advance(self):
        row = self.line()
        self.i += 1
        return row

    def parse(self):
        if not self.rows:
            raise SyntaxErrorLOL("Empty program")
        # Function definitions may precede HAI, as explicitly permitted.
        while self.word() == "HOW IZ I":
            self.parse_function()
        if self.word() != "HAI":
            raise SyntaxErrorLOL("Program must begin with HAI (after optional functions)")
        self.advance()

        # Optional WAZZUP/BUHBYE block must be immediately after HAI.
        if self.word() == "WAZZUP":
            self.advance()
            while self.word() != "BUHBYE":
                if self.line() is None:
                    raise SyntaxErrorLOL("Missing BUHBYE")
                row = self.advance()
                if not row or row[0][0] != "I HAS A":
                    raise SyntaxErrorLOL("Only variable declarations are allowed inside WAZZUP")
                _parse_declaration(row, self.functions)
                name = row[1][0]
                if name in self.declared:
                    raise SyntaxErrorLOL(f"Duplicate variable declaration: {name}")
                self.declared.add(name)
            self.advance()

        self.parse_block(stop={"KTHXBYE"}, context="program")
        if self.word() != "KTHXBYE":
            raise SyntaxErrorLOL("Missing KTHXBYE")
        self.advance()
        # Optional function definitions after KTHXBYE.
        while self.word() == "HOW IZ I":
            self.parse_function()
        if self.i != len(self.rows):
            raise SyntaxErrorLOL("Unexpected content after KTHXBYE")

    def parse_block(self, stop, context="block"):
        while self.line() is not None and self.word() not in stop:
            w = self.word()
            if w == "O RLY?":
                self.parse_if()
            elif w == "WTF?":
                self.parse_switch()
            elif w == "IM IN YR":
                self.parse_loop()
            elif w == "HOW IZ I":
                self.parse_function()
            else:
                row = self.advance()
                if row and row[0][0] == "I HAS A":
                    raise SyntaxErrorLOL("Variables must be declared inside WAZZUP")
                _parse_simple_statement(row, self.functions)

    def parse_if(self):
        self.advance()  # O RLY?
        if self.word() != "YA RLY":
            raise SyntaxErrorLOL("O RLY? must be followed by YA RLY")
        self.advance()
        self.parse_block({"MEBBE", "NO WAI", "OIC"}, "if")
        while self.word() == "MEBBE":
            row = self.advance()
            if len(row) < 2:
                raise SyntaxErrorLOL("MEBBE requires an expression")
            _parse_expr(row[1:], self.functions)
            self.parse_block({"MEBBE", "NO WAI", "OIC"}, "elseif")
        if self.word() == "NO WAI":
            self.advance()
            self.parse_block({"OIC"}, "else")
        if self.word() != "OIC":
            raise SyntaxErrorLOL("If statement is missing OIC")
        self.advance()

    def parse_switch(self):
        self.advance()  # WTF?
        saw_case = False
        saw_default = False
        while self.word() in {"OMG", "OMGWTF"}:
            w = self.word()
            row = self.advance()
            if w == "OMG":
                if saw_default:
                    raise SyntaxErrorLOL("OMG cannot follow OMGWTF")
                if len(row) != 2 or row[1][1] not in {"NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "YARN Literal"}:
                    # YARN may be represented by quote, content, quote.
                    if not (len(row) == 4 and row[1][1] == "String Delimiter" and row[2][1] == "YARN Literal" and row[3][1] == "String Delimiter"):
                        raise SyntaxErrorLOL("OMG requires one literal case value")
                saw_case = True
                self.parse_block({"OMG", "OMGWTF", "OIC"}, "case")
            else:
                if saw_default:
                    raise SyntaxErrorLOL("Only one OMGWTF is allowed")
                saw_default = True
                if len(row) != 1:
                    raise SyntaxErrorLOL("OMGWTF takes no value")
                self.parse_block({"OIC"}, "default case")
        if not saw_case:
            raise SyntaxErrorLOL("WTF? requires at least one OMG case")
        if self.word() != "OIC":
            raise SyntaxErrorLOL("Switch statement is missing OIC")
        self.advance()

    def parse_loop(self):
        row = self.advance()
        # IM IN YR label UPPIN|NERFIN YR variable [TIL|WILE expression]
        if len(row) < 5 or row[1][1] not in {"Loop Label", "Variable Identifier", "Identifier"}:
            raise SyntaxErrorLOL("Invalid IM IN YR loop header")
        if row[2][0] not in {"UPPIN", "NERFIN"} or row[3][0] != "YR" or row[4][1] not in {"Variable Identifier", "Identifier"}:
            raise SyntaxErrorLOL("Loop header must be: IM IN YR label UPPIN/NERFIN YR variable")
        if len(row) > 5:
            if row[5][0] not in {"TIL", "WILE"}:
                raise SyntaxErrorLOL("Expected TIL or WILE in loop header")
            _parse_expr(row[6:], self.functions)
        label = row[1][0]
        self.parse_block({"IM OUTTA YR"}, "loop")
        if self.word() != "IM OUTTA YR":
            raise SyntaxErrorLOL("Loop is missing IM OUTTA YR")
        end = self.advance()
        if len(end) != 2 or end[1][0] != label:
            raise SyntaxErrorLOL("IM OUTTA YR label does not match loop label")

    def parse_function(self):
        row = self.advance()
        if len(row) < 2 or row[1][1] not in {"Function Identifier", "Variable Identifier", "Identifier"}:
            raise SyntaxErrorLOL("HOW IZ I requires a function name")
        name = row[1][0]
        if name in self.functions:
            raise SyntaxErrorLOL(f"Duplicate function definition: {name}")
        params = []
        pos = 2
        while pos < len(row):
            if row[pos][0] != "YR" or pos + 1 >= len(row) or row[pos + 1][1] not in {"Variable Identifier", "Identifier"}:
                raise SyntaxErrorLOL("Invalid function parameter list")
            params.append(row[pos + 1][0])
            pos += 2
            if pos < len(row):
                if row[pos][0] != "AN" or pos + 1 >= len(row) or row[pos + 1][0] != "YR":
                    raise SyntaxErrorLOL("Function parameters must be separated by AN YR")
                pos += 1
        if len(params) != len(set(params)):
            raise SyntaxErrorLOL("Duplicate function parameter")
        self.functions[name] = len(params)
        self.parse_block({"IF U SAY SO"}, "function")
        if self.word() != "IF U SAY SO":
            raise SyntaxErrorLOL("Function definition is missing IF U SAY SO")
        end = self.advance()
        if len(end) != 1:
            raise SyntaxErrorLOL("IF U SAY SO takes no operands")


def parseProgram(code):
    """Return (is_valid, error_message)."""
    table = getLexemes(code)
    if table is None:
        return False, "Lexical analysis failed"
    try:
        ProgramParser(table).parse()
        return True, "Syntax is valid"
    except SyntaxErrorLOL as exc:
        return False, str(exc)
    except Exception as exc:
        return False, f"Parser error: {exc}"


def checkSyntax(code):
    """Compatibility API: return True for syntactically valid source."""
    return parseProgram(code)[0]


if __name__ == "__main__":
    import sys
    source = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else "HAI\nKTHXBYE"
    valid, message = parseProgram(source)
    print("Syntax valid" if valid else "Syntax error", "-", message)
