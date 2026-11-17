"""LOLCODE semantic analyzer / interpreter for CMSC 124 (ITZ5).

Consumes the token table produced by lexical_analyzer.getLexemes(). The lexer
represents each source line as a list of [lexeme, classification] pairs.
This module executes semantically valid, syntactically well-formed programs.
No lexer/parser generator or third-party dependency is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Any, Callable, Optional

try:
    from lexical_analyzer import getLexemes
except ImportError:  # permits package-style imports
    from .lexical_analyzer import getLexemes

TYPES = {"NOOB", "TROOF", "NUMBR", "NUMBAR", "YARN"}
ARITHMETIC = {"SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"}
BOOLEAN_BINARY = {"BOTH OF", "EITHER OF", "WON OF"}
BOOLEAN_INFINITE = {"ALL OF", "ANY OF"}
COMPARISON = {"BOTH SAEM", "DIFFRINT"}
OPERATORS = ARITHMETIC | BOOLEAN_BINARY | BOOLEAN_INFINITE | COMPARISON | {"NOT", "SMOOSH", "MAEK"}

class SemanticError(Exception):
    """A runtime/type/identifier error in a LOLCODE program."""

@dataclass
class Value:
    value: Any
    type: str

@dataclass
class Function:
    name: str
    parameters: list[str]
    body: list[list[list[str]]]

class ReturnSignal(Exception):
    def __init__(self, value: Value):
        self.value = value

class BreakSignal(Exception):
    pass


def infer_type(value: Any) -> str:
    if value is None: return "NOOB"
    if isinstance(value, bool): return "TROOF"
    if isinstance(value, int): return "NUMBR"
    if isinstance(value, float): return "NUMBAR"
    return "YARN"


def as_value(value: Any) -> Value:
    return value if isinstance(value, Value) else Value(value, infer_type(value))


def cast_value(source: Value, target: str, explicit: bool = False) -> Value:
    """Apply the project's typecasting table (specification pages 4-5)."""
    if target not in TYPES:
        raise SemanticError(f"unknown data type '{target}'")
    value, source_type = source.value, source.type
    if source_type == target:
        return Value(value, target)
    if target == "NOOB":
        if explicit: return Value(None, "NOOB")
        raise SemanticError(f"cannot implicitly typecast {source_type} to NOOB")
    if source_type == "NOOB":
        if target == "TROOF": return Value(False, "TROOF")
        if explicit:
            defaults = {"NUMBR": 0, "NUMBAR": 0.0, "YARN": ""}
            return Value(defaults[target], target)
        raise SemanticError(f"cannot implicitly typecast NOOB to {target}")
    if source_type == "TROOF":
        if target == "NUMBR": return Value(1 if value else 0, target)
        if target == "NUMBAR": return Value(1.0 if value else 0.0, target)
        if target == "YARN": return Value("WIN" if value else "FAIL", target)
    if source_type == "NUMBR":
        if target == "NUMBAR": return Value(float(value), target)
        if target == "YARN": return Value(str(value), target)
        if target == "TROOF": return Value(value != 0, target)
    if source_type == "NUMBAR":
        if target == "NUMBR": return Value(int(value), target)
        if target == "YARN":
            # Truncate (not round) to at most two decimal places.
            rendered = str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
            return Value(rendered, target)
        if target == "TROOF": return Value(value != 0.0, target)
    if source_type == "YARN":
        if target == "TROOF": return Value(value != "", target)
        if target in {"NUMBR", "NUMBAR"}:
            # The specification permits digits, hyphen and period only; the
            # resulting text must still be a valid number.
            import re
            if not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
                raise SemanticError(f"cannot typecast {value!r} to {target}")
            if target == "NUMBR": return Value(int(float(value)), target)
            return Value(float(value), target)
    raise SemanticError(f"cannot typecast {source_type} to {target}")


def _is_string_triplet(tokens: list[list[str]], i: int) -> bool:
    return (i + 2 < len(tokens) and tokens[i][1] == "String Delimiter"
            and tokens[i + 1][1] == "YARN Literal"
            and tokens[i + 2][1] == "String Delimiter")

class SemanticAnalyzer:
    def __init__(self, input_values=None, input_func: Optional[Callable[[str], str]] = None):
        self.symbol_table: dict[str, Value] = {"IT": Value(None, "NOOB")}
        self.console_output: list[str] = []
        self.input_values = list(input_values or [])
        self.input_func = input_func
        self.functions: dict[str, Function] = {}
        self.call_depth = 0
        self.max_call_depth = 100
        self._errors: list[str] = []

    @property
    def errors(self): return list(self._errors)

    def _error(self, message):
        raise SemanticError(message)

    def _get_var(self, name: str) -> Value:
        if name not in self.symbol_table:
            self._error(f"undeclared variable '{name}'")
        return self.symbol_table[name]

    def _set_var(self, name: str, value: Value):
        if name != "IT" and name not in self.symbol_table:
            self._error(f"undeclared variable '{name}'")
        self.symbol_table[name] = Value(value.value, value.type)

    def _literal(self, token: list[str]) -> Value:
        lexeme, kind = token
        if kind == "NUMBR Literal": return Value(int(lexeme), "NUMBR")
        if kind == "NUMBAR Literal": return Value(float(lexeme), "NUMBAR")
        if kind == "TROOF Literal": return Value(lexeme == "WIN", "TROOF")
        if kind == "YARN Literal": return Value(lexeme, "YARN")
        self._error(f"'{lexeme}' is not a literal")

    def _truth(self, value: Value) -> bool:
        return cast_value(value, "TROOF").value

    def _as_number(self, value: Value) -> Value:
        if value.type in {"NUMBR", "NUMBAR"}: return value
        if value.type == "TROOF": return cast_value(value, "NUMBR")
        if value.type == "YARN":
            import re
            if re.fullmatch(r"-?\d+", value.value): return cast_value(value, "NUMBR")
            if re.fullmatch(r"-?\d+\.\d+", value.value): return cast_value(value, "NUMBAR")
        return cast_value(value, "NUMBAR")

    def _numeric_pair(self, a: Value, b: Value):
        return self._as_number(a), self._as_number(b)

    def _eval_operator(self, op: str, args: list[Value]) -> Value:
        if op in ARITHMETIC:
            a, b = self._numeric_pair(args[0], args[1])
            x, y = a.value, b.value
            if op == "SUM OF": result = x + y
            elif op == "DIFF OF": result = x - y
            elif op == "PRODUKT OF": result = x * y
            elif op == "QUOSHUNT OF":
                if y == 0: self._error("division by zero")
                result = int(x / y) if a.type == b.type == "NUMBR" else x / y
            elif op == "MOD OF":
                if y == 0: self._error("modulo by zero")
                result = x % y
            elif op == "BIGGR OF": result = max(x, y)
            else: result = min(x, y)
            # Preserve NUMBR only when both operands are NUMBR, except division
            # can produce a fractional value and therefore becomes NUMBAR.
            if a.type == b.type == "NUMBR" and op != "QUOSHUNT OF":
                return Value(int(result), "NUMBR")
            if op == "QUOSHUNT OF" and a.type == b.type == "NUMBR":
                return Value(int(result), "NUMBR")
            return Value(float(result), "NUMBAR")
        if op in BOOLEAN_BINARY:
            a, b = (self._truth(args[0]), self._truth(args[1]))
            if op == "BOTH OF": result = a and b
            elif op == "EITHER OF": result = a or b
            else: result = a != b
            return Value(result, "TROOF")
        if op == "NOT": return Value(not self._truth(args[0]), "TROOF")
        if op in BOOLEAN_INFINITE:
            truth_values = [self._truth(v) for v in args]
            result = all(truth_values) if op == "ALL OF" else any(truth_values)
            return Value(result, "TROOF")
        if op in COMPARISON:
            a, b = args
            if a.type != b.type and not (a.type in {"NUMBR", "NUMBAR"} and b.type in {"NUMBR", "NUMBAR"}):
                self._error(f"no automatic typecasting for {a.type} and {b.type} comparison")
            equal = a.value == b.value
            return Value(equal if op == "BOTH SAEM" else not equal, "TROOF")
        if op == "SMOOSH":
            return Value("".join(self._to_yarn(v) for v in args), "YARN")
        self._error(f"unsupported operator '{op}'")

    def _to_yarn(self, value: Value) -> str:
        return cast_value(value, "YARN").value

    def _parse_expr(self, tokens: list[list[str]], i: int, allow_maek=True, depth=0):
        if depth > 200: self._error("expression nesting is too deep")
        if i >= len(tokens): self._error("missing expression")
        tok = tokens[i]
        lex, kind = tok
        if _is_string_triplet(tokens, i):
            return Value(tokens[i + 1][0], "YARN"), i + 3
        if kind in {"NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "YARN Literal"}:
            return self._literal(tok), i + 1
        if kind == "Variable Identifier":
            return self._get_var(lex), i + 1
        if lex == "MAEK" and allow_maek:
            value, j = self._parse_expr(tokens, i + 1, depth=depth + 1)
            if j < len(tokens) and tokens[j][0] == "A": j += 1
            if j >= len(tokens) or tokens[j][0] not in TYPES:
                self._error("MAEK must be followed by a valid type")
            return cast_value(value, tokens[j][0], explicit=True), j + 1
        if lex == "I IZ":
            if i + 1 >= len(tokens): self._error("I IZ requires a function name")
            name = tokens[i + 1][0]
            j, arguments = i + 2, []
            while j < len(tokens) and tokens[j][0] != "MKAY":
                if tokens[j][0] == "YR": j += 1
                elif tokens[j][0] == "AN": j += 1; continue
                else: self._error("expected YR or AN in function call")
                argument, j = self._parse_expr(tokens, j, depth=depth + 1)
                arguments.append(argument)
            if j >= len(tokens) or tokens[j][0] != "MKAY": self._error("function call is missing MKAY")
            return self._call_function(name, arguments), j + 1
        if lex in ARITHMETIC | BOOLEAN_BINARY | COMPARISON:
            a, j = self._parse_expr(tokens, i + 1, depth=depth + 1)
            if j >= len(tokens) or tokens[j][0] != "AN": self._error(f"'{lex}' requires AN between operands")
            b, j = self._parse_expr(tokens, j + 1, depth=depth + 1)
            return self._eval_operator(lex, [a, b]), j
        if lex == "NOT":
            a, j = self._parse_expr(tokens, i + 1, depth=depth + 1)
            return self._eval_operator(lex, [a]), j
        if lex in BOOLEAN_INFINITE:
            values, j = [], i + 1
            while True:
                if j >= len(tokens): self._error(f"{lex} is missing MKAY")
                if tokens[j][0] == "MKAY":
                    if not values: self._error(f"{lex} requires at least one operand")
                    return self._eval_operator(lex, values), j + 1
                value, j = self._parse_expr(tokens, j, depth=depth + 1)
                values.append(value)
                if j < len(tokens) and tokens[j][0] == "AN": j += 1
                elif j < len(tokens) and tokens[j][0] != "MKAY":
                    self._error(f"expected AN or MKAY in {lex}")
        if lex == "SMOOSH":
            values, j = [], i + 1
            while j < len(tokens):
                if tokens[j][0] == "AN": j += 1; continue
                value, j = self._parse_expr(tokens, j, depth=depth + 1)
                values.append(value)
            if len(values) < 2: self._error("SMOOSH requires at least two operands")
            return self._eval_operator(lex, values), j
        if kind == "String Delimiter": self._error("malformed YARN literal")
        self._error(f"expected expression, found '{lex}'")

    def _parse_expr_exact(self, tokens: list[list[str]]) -> Value:
        value, end = self._parse_expr(tokens, 0)
        if end != len(tokens): self._error(f"unexpected token '{tokens[end][0]}' after expression")
        return value

    def _tokens(self, line):
        return [list(t) for t in line]

    def _collect_functions(self, lines):
        """Extract top-level function declarations; retain ordinary program lines."""
        output, i = [], 0
        while i < len(lines):
            row = self._tokens(lines[i])
            if row and row[0][0] == "HOW IZ I":
                if len(row) < 2 or row[1][1] != "Function Identifier": self._error("function name is missing")
                name = row[1][0]
                params, j = [], 2
                while j < len(row):
                    if row[j][0] != "YR" or j + 1 >= len(row): self._error(f"invalid parameter list in function '{name}'")
                    if row[j + 1][1] != "Variable Identifier": self._error("function parameter must be an identifier")
                    params.append(row[j + 1][0]); j += 2
                    if j < len(row):
                        if row[j][0] != "AN": self._error("expected AN between function parameters")
                        j += 1
                body, i = [], i + 1
                while i < len(lines) and not (lines[i] and lines[i][0][0] == "IF U SAY SO"):
                    body.append(lines[i]); i += 1
                if i >= len(lines): self._error(f"function '{name}' has no IF U SAY SO")
                if name in self.functions: self._error(f"function '{name}' is already defined")
                self.functions[name] = Function(name, params, body)
                i += 1
            else:
                output.append(lines[i]); i += 1
        return output

    def _execute_block(self, lines, start=0, stop_words=None, loop_label=None):
        stop_words = stop_words or set()
        i = start
        while i < len(lines):
            row = self._tokens(lines[i])
            if not row: i += 1; continue
            first = row[0][0]
            if first in stop_words: return i, first
            if first == "O RLY?": i = self._execute_if(lines, i); continue
            if first == "WTF?": i = self._execute_switch(lines, i); continue
            if first == "IM IN YR": i = self._execute_loop(lines, i); continue
            self._execute_statement(row)
            i += 1
        return i, None

    def _execute_statement(self, row):
        first = row[0][0]
        if first in {"WAZZUP", "BUHBYE"}: return
        if first == "I HAS A":
            if len(row) < 2: self._error("I HAS A requires a variable name")
            name = row[1][0]
            if name in self.symbol_table and name != "IT": self._error(f"variable '{name}' is already declared")
            if name == "IT": self._error("IT is reserved as the implicit variable")
            value = Value(None, "NOOB")
            if len(row) > 2:
                if row[2][0] != "ITZ": self._error("expected ITZ in variable declaration")
                value = self._parse_expr_exact(row[3:])
            self.symbol_table[name] = value
            return
        if first == "VISIBLE":
            args, j = [], 1
            while j < len(row):
                if row[j][0] == "+": j += 1; continue
                value, j = self._parse_expr(row, j)
                args.append(value)
            self.console_output.append("".join(self._to_yarn(v) for v in args))
            return
        if first == "GIMMEH":
            if len(row) != 2: self._error("GIMMEH requires exactly one variable")
            name = row[1][0]
            if name not in self.symbol_table: self._error(f"undeclared variable '{name}'")
            if self.input_values:
                entered = str(self.input_values.pop(0))
            elif self.input_func:
                entered = str(self.input_func(name))
            else:
                entered = input(f"{name}: ")
            self.symbol_table[name] = Value(entered, "YARN")
            return
        if first == "GTFO": raise BreakSignal()
        if first == "FOUND YR":
            value = self._parse_expr_exact(row[1:])
            raise ReturnSignal(value)
        if len(row) >= 2 and row[1][0] == "R":
            name = first
            if row[0][1] != "Variable Identifier": self._error("assignment target must be a variable")
            value = self._parse_expr_exact(row[2:])
            self._set_var(name, value)
            return
        if len(row) == 3 and row[1][0] == "IS NOW A":
            name = first
            if row[0][1] != "Variable Identifier": self._error("typecast target must be a variable")
            current = self._get_var(name)
            self.symbol_table[name] = cast_value(current, row[2][0], explicit=True)
            return
        # An expression statement stores its result in IT.
        self.symbol_table["IT"] = self._parse_expr_exact(row)

    def _execute_if(self, lines, start):
        """Execute YA RLY / zero or more MEBBE / optional NO WAI branches."""
        i = start + 1
        if i >= len(lines) or not lines[i] or lines[i][0][0] != "YA RLY":
            self._error("O RLY? must be followed by YA RLY")
        initial_condition = self._truth(self.symbol_table["IT"])
        branches = []
        branch_kind, branch_condition, body_start = "YA RLY", initial_condition, i + 1
        i = body_start
        while i < len(lines):
            row = self._tokens(lines[i])
            head = row[0][0] if row else ""
            if head in {"MEBBE", "NO WAI", "OIC"}:
                branches.append((branch_kind, branch_condition, body_start, i))
                if head == "OIC": break
                if head == "MEBBE":
                    if len(row) < 2: self._error("MEBBE requires a condition")
                    branch_kind = "MEBBE"
                    branch_condition = self._tokens(row[1:])
                else:
                    if len(row) != 1: self._error("NO WAI must be alone on its line")
                    branch_kind, branch_condition = "NO WAI", True
                body_start = i + 1
            i += 1
        if i >= len(lines) or not lines[i] or lines[i][0][0] != "OIC":
            self._error("O RLY? is missing OIC")
        if branch_kind != "NO WAI" or body_start <= i:
            # The final branch is not appended by the loop if OIC was reached.
            pass
        # The OIC branch was appended above when encountered; choose first true branch.
        for kind, condition, begin, finish in branches:
            if kind == "MEBBE":
                selected = self._truth(self._parse_expr_exact(condition))
            else:
                selected = condition
            if selected:
                self._execute_block(lines[begin:finish])
                break
        return i + 1

    def _execute_switch(self, lines, start):
        switch_value = self.symbol_table["IT"]
        i, default_start = start + 1, None
        cases = []
        while i < len(lines):
            row = self._tokens(lines[i])
            if not row:
                i += 1
                continue
            head = row[0][0]
            if head == "OIC": break
            if head == "OMGWTF":
                default_start = i + 1
                i += 1
                while i < len(lines) and (not lines[i] or lines[i][0][0] != "OIC"):
                    i += 1
                break
            if head != "OMG": self._error("expected OMG, OMGWTF, or OIC in switch")
            if len(row) < 2: self._error("OMG requires a literal")
            case_value = self._parse_expr_exact(row[1:])
            body_start = i + 1
            i = body_start
            while i < len(lines) and (not lines[i] or lines[i][0][0] not in {"OMG", "OMGWTF", "OIC"}):
                i += 1
            cases.append((case_value, body_start, i))
        if i >= len(lines) or not lines[i] or lines[i][0][0] != "OIC":
            self._error("WTF? is missing OIC")

        matched_index = None
        for index, (case_value, _, _) in enumerate(cases):
            if switch_value.type == case_value.type and switch_value.value == case_value.value:
                matched_index = index
                break
        broke = False
        if matched_index is not None:
            # LOLCODE switch cases fall through until GTFO or OIC.
            for _, begin, finish in cases[matched_index:]:
                try:
                    self._execute_block(lines[begin:finish])
                except BreakSignal:
                    broke = True
                    break
        if not broke and default_start is not None:
            try:
                self._execute_block(lines[default_start:i])
            except BreakSignal:
                pass
        return i + 1

    def _execute_loop(self, lines, start):
        header = self._tokens(lines[start])
        if len(header) < 5: self._error("invalid loop header")
        label, operation = header[1][0], header[2][0]
        if operation not in {"UPPIN", "NERFIN"}: self._error("loop operation must be UPPIN or NERFIN")
        if header[3][0] != "YR": self._error("expected YR in loop header")
        variable = header[4][0]
        if variable not in self.symbol_table: self._error(f"undeclared loop variable '{variable}'")
        condition_kind = header[5][0] if len(header) > 5 else None
        condition_tokens = header[6:] if condition_kind in {"TIL", "WILE"} else []
        if condition_kind not in {None, "TIL", "WILE"}: self._error("expected TIL or WILE in loop header")
        end = start + 1
        while end < len(lines) and not (lines[end] and lines[end][0][0] == "IM OUTTA YR"):
            end += 1
        if end >= len(lines): self._error(f"loop '{label}' is missing IM OUTTA YR")
        closing = self._tokens(lines[end])
        if len(closing) != 2 or closing[1][0] != label: self._error(f"loop label mismatch: expected '{label}'")
        body = lines[start + 1:end]
        iterations = 0
        while True:
            if condition_kind:
                condition = self._parse_expr_exact(condition_tokens)
                truth = self._truth(condition)
                if condition_kind == "TIL" and truth: break
                if condition_kind == "WILE" and not truth: break
            if iterations >= 100000: self._error("loop iteration limit exceeded")
            try:
                self._execute_block(body)
            except BreakSignal:
                break
            current = self._get_var(variable)
            number = cast_value(current, "NUMBR")
            self.symbol_table[variable] = Value(number.value + (1 if operation == "UPPIN" else -1), "NUMBR")
            iterations += 1
        return end + 1

    def _call_function(self, name, arguments):
        if name not in self.functions: self._error(f"undefined function '{name}'")
        function = self.functions[name]
        if len(arguments) != len(function.parameters):
            self._error(f"function '{name}' expects {len(function.parameters)} argument(s), got {len(arguments)}")
        if self.call_depth >= self.max_call_depth: self._error("maximum function call depth exceeded")
        saved = self.symbol_table
        local = {"IT": Value(None, "NOOB")}
        for parameter, argument in zip(function.parameters, arguments): local[parameter] = Value(argument.value, argument.type)
        self.symbol_table = local; self.call_depth += 1
        result = Value(None, "NOOB")
        try:
            self._execute_block(function.body)
        except ReturnSignal as signal:
            result = signal.value
        except BreakSignal:
            result = Value(None, "NOOB")
        finally:
            self.symbol_table = saved; self.call_depth -= 1
        # A function's return value is assigned to the caller's implicit IT.
        self.symbol_table["IT"] = Value(result.value, result.type)
        return result

    def execute(self, source_or_tokens):
        """Execute source text or a lexer token table. Returns a result dictionary."""
        self.symbol_table = {"IT": Value(None, "NOOB")}
        self.console_output = []; self.functions = {}; self._errors = []
        try:
            table = getLexemes(source_or_tokens) if isinstance(source_or_tokens, str) else source_or_tokens
            if table is None: self._error("lexical analysis failed")
            # Normalize the lexer's [line][token] structure; discard HAI/KTHXBYE.
            lines = []
            for line in table:
                row = self._tokens(line)
                if row and row[0][0] not in {"HAI", "KTHXBYE"}: lines.append(row)
            # Remove blank rows and declaration delimiters; declarations still execute.
            lines = [row for row in lines if row]
            # Extract functions before executing main body (spec permits definitions outside HAI/KTHXBYE).
            lines = self._collect_functions(lines)
            # Declarations are only valid in initial WAZZUP...BUHBYE section.
            if lines and lines[0][0][0] == "WAZZUP":
                try: end = next(i for i, row in enumerate(lines) if row and row[0][0] == "BUHBYE")
                except StopIteration: self._error("WAZZUP is missing BUHBYE")
                declaration_rows = lines[1:end]
                for row in declaration_rows: self._execute_statement(row)
                lines = lines[end + 1:]
            self._execute_block(lines)
            return {"success": True, "output": list(self.console_output), "symbol_table": self.get_symbol_table(), "errors": []}
        except (SemanticError, ReturnSignal, BreakSignal) as exc:
            message = str(exc) if isinstance(exc, SemanticError) else "control-flow statement used outside its valid context"
            self._errors.append(message)
            return {"success": False, "output": list(self.console_output), "symbol_table": self.get_symbol_table(), "errors": list(self._errors)}
        except Exception as exc:
            message = f"runtime error: {exc}"
            self._errors.append(message)
            return {"success": False, "output": list(self.console_output), "symbol_table": self.get_symbol_table(), "errors": list(self._errors)}

    def get_symbol_table(self):
        return [[name, value.value, value.type] for name, value in self.symbol_table.items()]

# Backward-compatible module-level API used by a GUI or other project modules.
symbol_table = []
console_output = []
_last_analyzer = None

def runProgram(code, input_values=None, input_func=None):
    global symbol_table, console_output, _last_analyzer
    analyzer = SemanticAnalyzer(input_values=input_values, input_func=input_func)
    result = analyzer.execute(code)
    _last_analyzer = analyzer
    symbol_table = analyzer.get_symbol_table()
    console_output = list(analyzer.console_output)
    return result

def executeProgram(code, input_values=None, input_func=None):
    return runProgram(code, input_values, input_func)

def getSymbolTable():
    return [row[:] for row in symbol_table]

def getConsoleOutput():
    return list(console_output)

def main():
    sample = '''HAI
WAZZUP
I HAS A x ITZ 5
I HAS A y ITZ 3
BUHBYE
VISIBLE SUM OF x AN y
KTHXBYE'''
    result = runProgram(sample)
    print("Output:", result["output"])
    print("Symbol table:", result["symbol_table"])
    if not result["success"]: print("Errors:", result["errors"])

if __name__ == "__main__":
    main()
