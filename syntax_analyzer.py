# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 2 - Syntax Analyzer

# Assumptions and Formatting Rules: (don't delete)
# 1) LOLCODE source files should have .lol extension
# 2) Should start with HAI and end in KTHXBYE, no need for version number
# 3) You may assume ONE LINE CONTAINS ONE STATEMENT ONLY
# 4) There is no need to support SOFT COMMAND BREAKS, EACH STATEMENT IS DELIMITED BY NEW LINE
# 5) Assume that there is only one whitespace in between keywords
# 6) Indentation is IRRELEVANT
# 7) Spaces inside YARN (string) should be RETAINED
# 8) Comments are NOT CONSIDERED STATEMENTS and MUST BE IGNORED!!
# 9) Keywords OBTW and TLDR MUST HAVE THEIR OWN LINES (bawal ung OBTW <comment> TLDR)
# 10) Variables are declared in WAZZUP BUHBYE ( so dapat after HAI, WAZZUP BUHBYE agad OR NONE AT ALL)
# 11) All variables must be declared inside the WAZZUP portion of the program. The WAZZUP clause is found at the beginning of the program, after HAI.
# 12) Operations are in PREFIX NOTATION (Important)

# HOW IT WORKS:
# - kinukuha natin yung lexical table (one row of tokens per line) galing sa lexical_analyzer.py
# - chinecheck natin kung tama yung grammar ng bawat statement
# - habang nagchecheck, ginagawa na rin natin yung SIMPLIFIED SYNTAX TREE na ipapasa sa semantics.py
#   para hindi na kailangan i-check ulit ng semantics yung syntax (ie-execute na lang niya)
# - kapag may error, ilalagay natin yung message sa syntax_error tapos -1 (or None) yung ibabalik
#
# FORMAT NG SYNTAX TREE:
#   expressions:
#     ["LITERAL", value]
#     ["VAR", name]
#     [operator, left, right]
#     ["NOT", operand]
#     ["ALL OF" / "ANY OF" / "SMOOSH", [operands]]
#     ["MAEK", expression, type]
#     ["I IZ", function_name, [arguments]]
#   statements:
#     ["DECLARE", name, expression or None]
#     ["VISIBLE", [expressions], add_newline]
#     ["GIMMEH", name]
#     ["ASSIGN", name, expression]
#     ["RECAST", name, type]              (IS NOW A)
#     ["EXPRESSION", expression]          (result goes to IT)
#     ["IF", if_block, [[mebbe_expression, mebbe_block], ...], else_block or None]
#     ["SWITCH", [[case_literal, case_block], ...], default_block or None]
#     ["LOOP", label, "UPPIN"/"NERFIN", variable, "TIL"/"WILE"/None, condition or None, loop_block]
#     ["GTFO"]
#     ["FOUND YR", expression]
#   program:
#     {"declarations": [...], "body": [...], "functions": {name: [parameters, function_block]}}

import lexical_analyzer # para makuha yung line numbers at error message ng lexical analyzer
from lexical_analyzer import getLexemes # we reuse the lexical analyzer

# -------- separate natin ung mga operations na may two arity and infinite arity --------
# ang logic dito is: kailangang mag match para alam kung ilang parameters ittake
two_arity = ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF",
"BOTH OF", "EITHER OF", "WON OF", "BOTH SAEM", "DIFFRINT", "BIGGR OF", "SMALLR OF"]
infinite_arity = ["ANY OF", "ALL OF"]
# ------------------------------------------------------------------------------------------

TYPES = ["NOOB", "TROOF", "NUMBR", "NUMBAR", "YARN"]

# mga keywords na hindi pwedeng mag-isa (dapat part sila ng if / switch / loop / function / program)
block_keywords = ["YA RLY", "MEBBE", "NO WAI", "OIC", "OMG", "OMGWTF", "IM OUTTA YR",
                  "IF U SAY SO", "WAZZUP", "BUHBYE", "HAI", "KTHXBYE"]

syntax_error = ""      # error message na ipapakita sa UI
function_arity = {}    # bilang ng parameters (para ma-check yung function calls)
functions = {}         # [parameters, function_block]
current_row = 0        # index ng row na chinecheck natin (para sa line number ng error)


# save the error message with the line number (first error lang yung tinatandaan)
def error(message):
    global syntax_error
    if syntax_error != "":
        return
    line = ""
    if current_row < len(lexical_analyzer.row_line_numbers):
        line = "Line " + str(lexical_analyzer.row_line_numbers[current_row]) + ": "
    syntax_error = line + message


# returns the first lexeme of row i (or None kapag wala na tayong rows)
def firstWord(rows, i):
    if i < len(rows):
        if len(rows[i]) > 0:
            return rows[i][0][0]
        else:
            return None
    else:
        return None


# para hindi lumampas sa dulo yung current_row (para sa line number ng error)
def setCurrentRow(rows, i):
    global current_row
    if i < len(rows):
        current_row = i
    else:
        current_row = len(rows) - 1


# ------------------------ parsing for values (literals) ---------------------------------------------------------------------------------
def parseValue(tokens, i): # returns [node, index of the next token], [None, i] kapag hindi value, [None, -1] kapag may error
    if i >= len(tokens): # if we go past and there is no value, then we just return None
        return None, i

    if tokens[i][1] == "NUMBR Literal": # NUMBR
        return ["LITERAL", int(tokens[i][0])], i + 1
    if tokens[i][1] == "NUMBAR Literal": # NUMBAR
        return ["LITERAL", float(tokens[i][0])], i + 1
    if tokens[i][1] == "TROOF Literal": # TROOF
        if tokens[i][0] == "WIN":
            return ["LITERAL", True], i + 1
        else:
            return ["LITERAL", False], i + 1

    if tokens[i][1] == "String Delimiter": # in our lexical table, YARN (string)  is made up of three parts (quotation, string literal, and quotation)
        if i + 2 < len(tokens) and tokens[i + 1][1] == "YARN Literal" and tokens[i + 2][1] == "String Delimiter":
            return ["LITERAL", tokens[i + 1][0]], i + 3
        else:
            error("Malformed YARN literal")
            return None, -1

    return None, i # anything else is not a value
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for expressions (prefix notation) ---------------------------------------------------------------------------------
# returns [node, index of the next token] or [None, -1] kapag may error
# inside_all_any / inside_smoosh = para ma-detect natin yung bawal na nesting
def parseExpression(tokens, i, inside_all_any=False, inside_smoosh=False):
    if i >= len(tokens):
        error("Expected an expression")
        return None, -1

    lexeme = tokens[i][0]
    classification = tokens[i][1]

    # literal (NUMBR, NUMBAR, TROOF, YARN)
    node, next_i = parseValue(tokens, i)
    if next_i == -1:
        return None, -1
    if node is not None:
        return node, next_i

    # variable (kasama si IT)
    if classification == "Variable Identifier":
        return ["VAR", lexeme], i + 1

    # binary operations: <operation> <x> AN <y>
    if lexeme in two_arity:
        left, i = parseExpression(tokens, i + 1, inside_all_any, inside_smoosh)
        if i == -1:
            return None, -1
        if i >= len(tokens): # the AN keyword is required to separate operands
            error(lexeme + " requires AN between its operands")
            return None, -1
        if tokens[i][0] != "AN":
            error(lexeme + " requires AN between its operands")
            return None, -1
        right, i = parseExpression(tokens, i + 1, inside_all_any, inside_smoosh)
        if i == -1:
            return None, -1
        return [lexeme, left, right], i

    # unary: NOT <x>
    if lexeme == "NOT":
        operand, i = parseExpression(tokens, i + 1, inside_all_any, inside_smoosh)
        if i == -1:
            return None, -1
        return ["NOT", operand], i

    # infinite arity: ALL OF / ANY OF <x> AN <y> ... MKAY
    if lexeme in infinite_arity:
        if inside_all_any == True: # ALL OF and ANY OF cannot be nested into each other and themselves
            error("ALL OF and ANY OF cannot be nested")
            return None, -1
        operands = []
        operand, i = parseExpression(tokens, i + 1, True, inside_smoosh)
        if i == -1:
            return None, -1
        operands.append(operand)
        while i < len(tokens) and tokens[i][0] == "AN": # keep taking operands habang may AN
            operand, i = parseExpression(tokens, i + 1, True, inside_smoosh)
            if i == -1:
                return None, -1
            operands.append(operand)
        if i >= len(tokens):
            error(lexeme + " is missing MKAY")
            return None, -1
        if tokens[i][0] != "MKAY":
            error(lexeme + " is missing MKAY")
            return None, -1
        return [lexeme, operands], i + 1

    # concatenation: SMOOSH <x> AN <y> ... (walang MKAY)
    if lexeme == "SMOOSH":
        if inside_smoosh == True: # SMOOSH cannot be nested
            error("SMOOSH cannot be nested")
            return None, -1
        operands = []
        operand, i = parseExpression(tokens, i + 1, inside_all_any, True)
        if i == -1:
            return None, -1
        operands.append(operand)
        while i < len(tokens) and tokens[i][0] == "AN":
            # kapag AN YR, para sa function arguments yun, hindi para sa SMOOSH
            if i + 1 < len(tokens) and tokens[i + 1][0] == "YR":
                break
            operand, i = parseExpression(tokens, i + 1, inside_all_any, True)
            if i == -1:
                return None, -1
            operands.append(operand)
        return ["SMOOSH", operands], i

    # explicit typecasting: MAEK <x> [A] <type>
    if lexeme == "MAEK":
        value, i = parseExpression(tokens, i + 1, inside_all_any, inside_smoosh)
        if i == -1:
            return None, -1
        if i < len(tokens) and tokens[i][0] == "A": # since A is optional.. pag may A move to the next token
            i = i + 1
        if i >= len(tokens):
            error("MAEK must be followed by a type (NOOB, TROOF, NUMBR, NUMBAR, YARN)")
            return None, -1
        if tokens[i][0] not in TYPES:
            error("MAEK must be followed by a type (NOOB, TROOF, NUMBR, NUMBAR, YARN)")
            return None, -1
        return ["MAEK", value, tokens[i][0]], i + 1

    # function call: I IZ <name> [YR <x> [AN YR <y> ...]] MKAY
    if lexeme == "I IZ":
        if i + 1 >= len(tokens):
            error("I IZ requires a function name")
            return None, -1
        if tokens[i + 1][1] != "Function Identifier":
            error("I IZ requires a function name")
            return None, -1
        name = tokens[i + 1][0]
        i = i + 2
        arguments = []
        if i < len(tokens) and tokens[i][0] == "YR":
            argument, i = parseExpression(tokens, i + 1, inside_all_any, inside_smoosh)
            if i == -1:
                return None, -1
            arguments.append(argument)
            while i < len(tokens) and tokens[i][0] == "AN":
                if i + 1 >= len(tokens):
                    error("Function arguments must be separated by AN YR")
                    return None, -1
                if tokens[i + 1][0] != "YR":
                    error("Function arguments must be separated by AN YR")
                    return None, -1
                argument, i = parseExpression(tokens, i + 2, inside_all_any, inside_smoosh)
                if i == -1:
                    return None, -1
                arguments.append(argument)
        if i >= len(tokens):
            error("Function call is missing MKAY")
            return None, -1
        if tokens[i][0] != "MKAY":
            error("Function call is missing MKAY")
            return None, -1
        # check kung tama yung bilang ng arguments (kapag defined yung function)
        if name in function_arity:
            if function_arity[name] != len(arguments):
                error("Function " + name + " expects " + str(function_arity[name]) + " argument(s), got " + str(len(arguments)))
                return None, -1
        return ["I IZ", name, arguments], i + 1

    error("Expected an expression, found " + lexeme)
    return None, -1


# expression na dapat ubos yung buong tokens (right side ng R, ITZ, FOUND YR)
# returns the node or None kapag may error
def parseWholeExpression(tokens):
    node, i = parseExpression(tokens, 0)
    if i == -1:
        return None
    if i != len(tokens):
        error("Unexpected " + tokens[i][0] + " after expression")
        return None
    return node
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for I HAS A (declaration of variables) ---------------------------------------------------------------------------------
def parseDeclaration(tokens): # parse for I HAS A, returns the node or None kapag may error
    if len(tokens) < 2: # if there isn't a variable name
        error("I HAS A requires a variable name")
        return None
    if tokens[1][1] != "Variable Identifier": # if it isn't an identifier
        error("I HAS A requires a variable name")
        return None

    var_name = tokens[1][0]

    if len(tokens) == 2: # walang ITZ, uninitialized (NOOB)
        return ["DECLARE", var_name, None]

    # ITZ is optional, but if there is an ITZ we need to check if there is a corresponding value
    if tokens[2][0] != "ITZ":
        error("Expected ITZ after the variable name")
        return None
    if len(tokens) == 3:
        error("ITZ requires a value")
        return None
    value = parseWholeExpression(tokens[3:])
    if value is None:
        return None
    return ["DECLARE", var_name, value]
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for R (assignment) ---------------------------------------------------------------------------------
def parseAssignment(tokens):
    if tokens[0][1] != "Variable Identifier": # the left-hand side is always a receiving variable
        error("Left side of R must be a variable")
        return None
    if len(tokens) == 2:
        error("R requires a value")
        return None
    value = parseWholeExpression(tokens[2:])
    if value is None:
        return None
    return ["ASSIGN", tokens[0][0], value]
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for IS NOW A (recasting) ---------------------------------------------------------------------------------
def parseCasting(tokens):
    if tokens[0][1] != "Variable Identifier":
        error("Recasting must be: <variable> IS NOW A <type>")
        return None
    if len(tokens) != 3:
        error("Recasting must be: <variable> IS NOW A <type>")
        return None
    if tokens[2][0] not in TYPES:
        error("Recasting must be: <variable> IS NOW A <type>")
        return None
    return ["RECAST", tokens[0][0], tokens[2][0]]
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for VISIBLE (printing output) ---------------------------------------------------------------------------------
def parseOutput(tokens): # VISIBLE has infinite arity, meaning it can take n number of operands
    if len(tokens) < 2:
        error("VISIBLE requires at least one operand")
        return None

    expressions = []
    add_newline = True
    i = 1 # move past VISIBLE

    expression, i = parseExpression(tokens, i) # first operand
    if i == -1:
        return None
    expressions.append(expression)

    while i < len(tokens): # infinite arity, keep taking operands until there are no more
        if tokens[i][0] == "!": # for bonus! to be double checked pa (walang newline, dapat nasa dulo)
            if i != len(tokens) - 1:
                error("! must be at the end of VISIBLE")
                return None
            add_newline = False
            i = i + 1
        elif tokens[i][0] == "+": # each operand is separated by +
            if i + 1 >= len(tokens):
                error("Missing operand after + in VISIBLE")
                return None
            expression, i = parseExpression(tokens, i + 1)
            if i == -1:
                return None
            expressions.append(expression)
        else: # operands na walang + (allowed din sa original LOLCODE)
            expression, i = parseExpression(tokens, i)
            if i == -1:
                return None
            expressions.append(expression)

    return ["VISIBLE", expressions, add_newline]
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for GIMMEH (user input) ---------------------------------------------------------------------------------
def parseInput(tokens): # GIMMEH must always use a variable
    if len(tokens) != 2:
        error("GIMMEH requires exactly one variable")
        return None
    if tokens[1][1] != "Variable Identifier":
        error("GIMMEH requires exactly one variable")
        return None
    return ["GIMMEH", tokens[1][0]]
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for if-then (O RLY?) ---------------------------------------------------------------------------------
def parseConditional(rows, i, inside):
    i = i + 1 # move past O RLY? (we may assume O RLY?, YA RLY, NO WAI, and OIC are alone in their respective lines)

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "YA RLY":
        error("O RLY? must be followed by YA RLY")
        return None, -1

    # the if-clause starts at YA RLY and ends when MEBBE, NO WAI or OIC is encountered
    if_block, i = parseBlock(rows, i + 1, ["MEBBE", "NO WAI", "OIC"], inside + ["if"])
    if i == -1:
        return None, -1

    # for bonus! to be double checked pa (MEBBE/else-if)
    mebbe_list = []
    while firstWord(rows, i) == "MEBBE":
        setCurrentRow(rows, i)
        if len(rows[i]) < 2: # MEBBE should be followed by an expression in the same line
            error("MEBBE requires an expression")
            return None, -1
        condition = parseWholeExpression(rows[i][1:])
        if condition is None:
            return None, -1
        mebbe_block, i = parseBlock(rows, i + 1, ["MEBBE", "NO WAI", "OIC"], inside + ["if"])
        if i == -1:
            return None, -1
        mebbe_list.append([condition, mebbe_block])

    # the else-clause starts at NO WAI and ends when OIC is encountered
    else_block = None
    if firstWord(rows, i) == "NO WAI":
        else_block, i = parseBlock(rows, i + 1, ["OIC"], inside + ["if"])
        if i == -1:
            return None, -1

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "OIC":
        error("O RLY? is missing OIC")
        return None, -1

    return ["IF", if_block, mebbe_list, else_block], i + 1
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for switch-case (WTF?) ---------------------------------------------------------------------------------
def parseSwitch(rows, i, inside):
    i = i + 1 # move past WTF?

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "OMG":
        error("WTF? must be followed by at least one OMG case")
        return None, -1

    cases = []
    while firstWord(rows, i) == "OMG":
        setCurrentRow(rows, i)
        literal, next_i = parseValue(rows[i], 1) # the cases may be of any literal type
        if next_i == -1:
            return None, -1
        if literal is None:
            error("OMG must be followed by a literal value")
            return None, -1
        case_block, i = parseBlock(rows, i + 1, ["OMG", "OMGWTF", "OIC"], inside + ["switch"])
        if i == -1:
            return None, -1
        cases.append([literal, case_block])

    # the default case is specified by OMGWTF
    default_block = None
    if firstWord(rows, i) == "OMGWTF":
        default_block, i = parseBlock(rows, i + 1, ["OIC"], inside + ["switch"])
        if i == -1:
            return None, -1

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "OIC":
        error("WTF? is missing OIC")
        return None, -1

    return ["SWITCH", cases, default_block], i + 1
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for loops (IM IN YR) ---------------------------------------------------------------------------------
def parseLoop(rows, i, inside):
    row = rows[i]
    if len(row) < 2:
        error("IM IN YR requires a loop label")
        return None, -1
    if row[1][1] != "Loop Label":
        error("IM IN YR requires a loop label")
        return None, -1
    label = row[1][0]

    if len(row) < 5:
        error("Loop must be: IM IN YR <label> UPPIN/NERFIN YR <variable> [TIL/WILE <expression>]")
        return None, -1
    if row[2][0] != "UPPIN" and row[2][0] != "NERFIN": # the operation can either be UPPIN or NERFIN
        error("Loop operation must be UPPIN or NERFIN")
        return None, -1
    if row[3][0] != "YR":
        error("Expected YR after " + row[2][0])
        return None, -1
    if row[4][1] != "Variable Identifier":
        error("Expected a variable after YR")
        return None, -1
    operation = row[2][0]
    variable = row[4][0]

    condition_type = None # walang TIL/WILE, GTFO lang ang titigil sa loop
    condition = None
    if len(row) > 5:
        if row[5][0] != "TIL" and row[5][0] != "WILE":
            error("Expected TIL or WILE in loop header")
            return None, -1
        if len(row) == 6:
            error(row[5][0] + " requires an expression")
            return None, -1
        condition_type = row[5][0]
        condition = parseWholeExpression(row[6:])
        if condition is None:
            return None, -1

    # for bonus! to be double checked pa (loop nesting, kusang na-ha-handle ng parseBlock)
    loop_block, i = parseBlock(rows, i + 1, ["IM OUTTA YR"], inside + ["loop"])
    if i == -1:
        return None, -1

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "IM OUTTA YR":
        error("Loop " + label + " is missing IM OUTTA YR")
        return None, -1
    if len(rows[i]) != 2:
        error("IM OUTTA YR label does not match loop label " + label)
        return None, -1
    if rows[i][1][0] != label:
        error("IM OUTTA YR label does not match loop label " + label)
        return None, -1

    return ["LOOP", label, operation, variable, condition_type, condition, loop_block], i + 1
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for functions (HOW IZ I) ---------------------------------------------------------------------------------
def parseFunctionHeader(row):
    if len(row) < 2:
        error("HOW IZ I requires a function name")
        return None, None
    if row[1][1] != "Function Identifier":
        error("HOW IZ I requires a function name")
        return None, None
    name = row[1][0]

    parameters = []
    j = 2
    while j < len(row): # YR <parameter> [AN YR <parameter> ...]
        if row[j][0] != "YR":
            error("Invalid function parameter list (expected YR <parameter>)")
            return None, None
        if j + 1 >= len(row):
            error("Invalid function parameter list (expected YR <parameter>)")
            return None, None
        if row[j + 1][1] != "Variable Identifier":
            error("Invalid function parameter list (expected YR <parameter>)")
            return None, None
        parameters.append(row[j + 1][0])
        j = j + 2
        if j < len(row): # may kasunod pa na parameter, dapat AN YR
            if row[j][0] != "AN":
                error("Function parameters must be separated by AN YR")
                return None, None
            if j + 1 >= len(row):
                error("Function parameters must be separated by AN YR")
                return None, None
            if row[j + 1][0] != "YR":
                error("Function parameters must be separated by AN YR")
                return None, None
            j = j + 1

    return name, parameters


# HOW IZ I ... IF U SAY SO, returns the index after IF U SAY SO (-1 kapag may error)
def parseFunction(rows, i):
    name, parameters = parseFunctionHeader(rows[i])
    if name is None:
        return -1

    function_block, i = parseBlock(rows, i + 1, ["IF U SAY SO"], ["function"])
    if i == -1:
        return -1

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "IF U SAY SO":
        error("Function " + name + " is missing IF U SAY SO")
        return -1

    functions[name] = [parameters, function_block]
    return i + 1
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for one statement ---------------------------------------------------------------------------------
# inside = list ng mga blocks kung saan nakalagay yung statement
# returns [node, index of the next row], node is None for function definitions (nasa functions dict sila)
# returns [None, -1] kapag may error
def parseStatement(rows, i, inside):
    global current_row
    current_row = i
    tokens = rows[i]
    word = tokens[0][0]

    if word == "O RLY?":
        return parseConditional(rows, i, inside)

    if word == "WTF?":
        return parseSwitch(rows, i, inside)

    if word == "IM IN YR":
        return parseLoop(rows, i, inside)

    if word == "HOW IZ I":
        next_i = parseFunction(rows, i)
        return None, next_i

    if word == "I HAS A": # lahat ng variable ay dapat declared sa WAZZUP only
        error("Variables must be declared inside WAZZUP")
        return None, -1

    if word == "GTFO":
        return ["GTFO"], i + 1

    if word in block_keywords: # MEBBE / NO WAI / OIC na walang O RLY?
        error("Misplaced " + word + " (no matching block)")
        return None, -1

    if word == "VISIBLE":
        node = parseOutput(tokens)
    elif word == "GIMMEH":
        node = parseInput(tokens)
    elif word == "FOUND YR":
        if len(tokens) < 2:
            error("FOUND YR requires an expression")
            return None, -1
        value = parseWholeExpression(tokens[1:])
        if value is None:
            node = None
        else:
            node = ["FOUND YR", value]
    elif len(tokens) >= 2 and tokens[1][0] == "R": # assignment: <variable> R <expression>
        node = parseAssignment(tokens)
    elif len(tokens) >= 2 and tokens[1][0] == "IS NOW A": # recasting: <variable> IS NOW A <type>
        node = parseCasting(tokens)
    else: # expression statement (the result will be stored in IT)
        value = parseWholeExpression(tokens)
        if value is None:
            node = None
        else:
            node = ["EXPRESSION", value]

    if node is None: # may error sa statement
        return None, -1
    return node, i + 1


# parse statements until we see one of the stop_words (like OIC, KTHXBYE)
# returns [list of statements, index of the stop word] or [None, -1] kapag may error
def parseBlock(rows, i, stop_words, inside):
    global current_row
    block = []
    while i < len(rows) and firstWord(rows, i) not in stop_words:
        # nakita na yung KTHXBYE pero wala pang OIC
        if len(inside) > 0 and firstWord(rows, i) in block_keywords:
            current_row = i
            error("Expected " + " / ".join(stop_words) + " before " + firstWord(rows, i))
            return None, -1
        node, i = parseStatement(rows, i, inside)
        if i == -1:
            return None, -1
        if node is not None:
            block.append(node)
    return block, i
# --------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ code for checking syntax ---------------------------------------------------------------------------------
#returns [syntax tree, message], syntax tree is None kapag may error
def parseProgram(lexical_table):
    global syntax_error, function_arity, functions, current_row
    syntax_error = ""
    function_arity = {}
    functions = {}
    current_row = 0

    if lexical_table is None: # error from lexical analyzer
        syntax_error = "Lexical analysis failed"
        return None, syntax_error

    rows = lexical_table

    #kunin muna lahat ng function names at bilang ng parameters
    # para ma-check yung function calls kahit nauna yung call bago yung definition
    for index in range(len(rows)):
        if firstWord(rows, index) == "HOW IZ I":
            current_row = index
            name, parameters = parseFunctionHeader(rows[index])
            if name is None:
                return None, syntax_error
            function_arity[name] = len(parameters)

    i = 0

    # function definitions may come before HAI
    while firstWord(rows, i) == "HOW IZ I":
        current_row = i
        i = parseFunction(rows, i)
        if i == -1:
            return None, syntax_error

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "HAI":
        error("Program must start with HAI")
        return None, syntax_error
    i = i + 1

    # since kailangan ng WAZZUP at BUHBYE for variable declaration; titignan if meron (if wala, okay lang, pero bawal na mag declare ng variables)
    declarations = []
    if firstWord(rows, i) == "WAZZUP":
        i = i + 1 # move past WAZZUP
        while firstWord(rows, i) != "BUHBYE": # while we haven't seen BUHBYE;
            setCurrentRow(rows, i)
            if i >= len(rows): # if we reach the end and we don't see BUHBYE
                error("WAZZUP is missing BUHBYE")
                return None, syntax_error
            if firstWord(rows, i) != "I HAS A": # only I HAS A is allowed inside WAZZUP
                error("Only variable declarations (I HAS A) are allowed inside WAZZUP")
                return None, syntax_error
            declaration = parseDeclaration(rows[i]) # parse declarations (e.g I HAS A var)
            if declaration is None:
                return None, syntax_error
            declarations.append(declaration)
            i = i + 1
        i = i + 1 # move past the block

    # parse remaining statements until KTHXBYE
    body, i = parseBlock(rows, i, ["KTHXBYE"], [])
    if i == -1:
        return None, syntax_error

    setCurrentRow(rows, i)
    if firstWord(rows, i) != "KTHXBYE":
        error("Program must end with KTHXBYE")
        return None, syntax_error
    i = i + 1

    # function definitions may come after KTHXBYE
    while firstWord(rows, i) == "HOW IZ I":
        current_row = i
        i = parseFunction(rows, i)
        if i == -1:
            return None, syntax_error

    if i < len(rows): # nothing after KTHXBYE except functions
        current_row = i
        error("Only function definitions are allowed after KTHXBYE")
        return None, syntax_error

    tree = {"declarations": declarations, "body": body, "functions": functions}
    return tree, "Syntax is valid"


def checkSyntax(code): # function that returns True if syntax is valid; else returns False
    lexical_table = getLexemes(code) # we use lexical analysis from previous milestone (use getLexemes function)
    tree, message = parseProgram(lexical_table)
    if tree is None:
        return False
    else:
        return True
# -------------------------------------------------------------------------------------------------------------------------------------
