# Sources:
# https://github.com/amtuazon4/PyGUI/blob/main/source%20code/check_semantics.py
# Project Requirement # 3 - Semantics

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

#SEMANTICS CHECKLIST/THINGS TO CONSIDER

#1. State & Program Structure (p. 2-3)
# a. Variables
# - remember variables current type and value
#   (var -> type, value)
# - variables are dynamically typed
# - NOOB is default datatype
# - check for redeclared/undeclared variables
# - all variables must be inside WAZZUP (checked na ng syntax analyzer)

# b. IT (p. 2, 6)
# - implicit variable, always exists
# - initial type and value = NOOB, NONE
# - sasalo ng result ng expression na walang variable
# - O RLY? and WTF? reads IT
# - MAEK and function return values go to IT

# c. Declaration (p. 2)
# - I HAS A x -> NOOB, None
# - I HAS A x ITZ "some" -> store value and type
# - I HAS A x ITZ y -> copy y's value and type
# - I HAS A x ITZ SUM OF 5 AN 4 -> evaluate muna bago store

#2. Data Types (p. 3, 5)
# a. Data types
# - NOOB, TROOF, NUMBR, NUMBAR, YARN
# - variables can change datatype depending on assigned value

# b. Typecasting
# - implicit = automatic conversion
# - explicit = MAEK/IS NOW A
# - MAEK -> result goes to IT, di nababago si var
# - IS NOW A -> nababago si var
# - NOOB can only be implicitly cast to TROOF
# - explicit casting of NOOB is allowed

#3. Operations (p. 3-5)
# a. Arithmetic
# - SUM, DIFF, PRODUKT, QUOSHUNT, MOD, BIGGR, SMALLR
# - evaluate operands first
# - if not NUMBR/NUMBAR, implicitly!!! typecast
# - if both NUMBR -> result is NUMBR
# - if at least one NUMBAR -> result is NUMBAR
# - check division by 0 -> add a error checker

# b. Boolean
# - BOTH OF, EITHER OF, WON OF, NOT
# - ALL OF and ANY OF can have multiple operands
# - ALL OF/ANY OF read operands until MKAY
# - convert operands to TROOF first and result is always TROOF
# - ALL OF and ANY OF can't be nested (checked na ng syntax analyzer)
# - can contain other bool

# c. Comparison
# - BOTH SAEM, DIFFRINT
# - no automatic typecasting, e.g. yarn to numbr/numbar
# - NUMBR comparison uses integer math
# - NUMBAR comparison uses floating-point math

#4. Statements (p. 3, 5-6)
# a. VISIBLE
# - operands to YARN
# - concatenate all operands with +
# - automatically adds newline

# 5. Flow Control (p. 6-7)
# a. O RLY -> IT is important
# b. WTF? -> IT is important
# c. loops -> UPPIN/NERFIN, TIL/WILE, GTFO

# 6. Functions (p. 8)
# - functions cannot access variables outside of it (sariling symbol table)
# - arguments are pass-by-value
# - FOUND YR returns a value, GTFO returns NOOB, walang return = NOOB
# - return value goes to IT

# HOW IT WORKS:
# - hindi na natin binabasa yung raw lexeme table, yung SYNTAX TREE na galing sa syntax_analyzer.py yung ine-execute natin
#   (yung format ng tree nasa taas ng syntax_analyzer.py)
# - values are stored as python values, yung data type ay kinukuha sa getDataType()
#   None = NOOB, True/False = TROOF, int = NUMBR, float = NUMBAR, str = YARN

import re  # import regex
from decimal import ROUND_DOWN, Decimal  # for exact truncation of NUMBAR -> YARN

symbol_table = [] #[identifier, value, data_type] -> ["a", 10, "NUMBR"]
console_output = [] #para sa console (6) ng GUI
functions = {} # function name -> [parameters, function_block] (galing sa syntax tree)

input_function = input   # GIMMEH, papalitan ng GUI ng dialog box
output_function = None   # VISIBLE, kapag may value, tatawagin agad para makita agad sa GUI console


# simple exception para pag may semantic/runtime error, titigil agad yung program
class LOLSemanticError(Exception):
    pass


def error(message):
    raise LOLSemanticError(message)


#find variable by variable name
def findVar(var_name):
    for i in range(len(symbol_table)): #skim the semantic table/symbol table
        if symbol_table[i][0] == var_name:
            return i #if found return the index number
    return -1 #if not found return -1

#gets the data type of a value
def getDataType(value):
    if value is None: #laging NOOB if no value
        return "NOOB"
    if isinstance(value, bool): #always check bool before int
        return "TROOF"
    if isinstance(value, int):
        return "NUMBR"
    if isinstance(value, float):
        return "NUMBAR"
    return "YARN" #all not stated is automatically a string

#store the value given a variable name and its value
def storeVal(var_name, val):
    i = findVar(var_name)
    if i == -1: #if the variable is not existing, append to list (new variable)
        symbol_table.append([var_name, val, getDataType(val)])
    else: #update the value on the table if already existing (existing variable)
        symbol_table[i][1]= val
        symbol_table[i][2] = getDataType(val) #data could change if a new value if assigned

#get the value of a variable (error kapag undeclared)
def getVal(var_name):
    i = findVar(var_name)
    if i == -1: #if not found then undeclared var siya
        error("undeclared variable " + var_name)
    else:
        return symbol_table[i][1]

# TYPECASTING RULES
# implicit - automatic casting
# explicit - could be done using the MAEK operator or IS NOW A
# error() na para tumigil agad yung program
def typecast(val, new_data_type, explicit=False):
    #NOOBs can be implicitly typecast into TROOF. Implicit typecasting to any other type
    #except TROOF will result in an error. Explicit typecasting of NOOBs is allowed and results to empty/zero values (SPECS)
    data_type = getDataType(val) #get the current data type

    if data_type == new_data_type: #data type is already correct
        return val

    if new_data_type == "NOOB": #casting to NOOB is only through MAEK, basically bawal implicit typecasting
        if explicit:
            return None
        else:
            error("cannot implicitly typecast " + data_type + " to NOOB")

    #NOOB TYPECASTING RULES
    if data_type == "NOOB":
        if new_data_type == "TROOF": #allowed for implicit and explicit, stated in the specs
            return False
        if explicit:
            if new_data_type == "NUMBR":
                return 0
            if new_data_type == "NUMBAR":
                return 0.0
            if new_data_type == "YARN":
                return ""
        else:
            error("cannot implicitly typecast NOOB to " + new_data_type + " (variable has no value)")

    #TROOF TYPECASTING RULES
    if data_type == "TROOF":
        if new_data_type == "NUMBR":
            if val == True:
                return 1
            else:
                return 0

        if new_data_type == "NUMBAR":
            if val == True:
                return 1.0
            else:
                return 0.0

        if new_data_type == "YARN":
            if val == True:
                return "WIN"
            else:
                return "FAIL"

    #NUMBAR TYPECASTING RULES
    if data_type == "NUMBAR":
        #truncate decimal if numbar to nmbr
        if new_data_type == "NUMBR":
            return int(val)
        #if yarn, convert the value to string of characters
        if new_data_type == "YARN":
            return str(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)) # truncate to 2 decimal places
        #consider troof also, kapag 0 false, other value true
        if new_data_type == "TROOF":
            return val != 0

    #NUMBR TYPE CASTING RULES
    if data_type == "NUMBR":
        #convert to floating point
        if new_data_type == "NUMBAR":
            return float(val)
        #convert to string
        if new_data_type == "YARN":
            return str(val)
        #consider troof also, kapag 0 false, other value true
        if new_data_type == "TROOF":
            return val != 0

    #YARN TYPECASTING RULES
    if data_type == "YARN":
        if new_data_type == "TROOF":
            #empty string are cast to fail
            return val != ""

        if new_data_type == "NUMBR" or new_data_type == "NUMBAR":
            for char in val:
                #can be successfully cast if it contains non-numerical, non-hyphen, non-period characs
                if not char.isdigit() and char != "-" and char != ".":
                    error("cannot typecast YARN '" + val + "' to " + new_data_type)

            if not re.match(r'^-?[0-9]+(\.[0-9]+)?$', val):
                error("cannot typecast YARN '" + val + "' to " + new_data_type)
            if new_data_type == "NUMBR":
                return int(float(val))
            return float(val)

    error("cannot typecast " + data_type + " to " + new_data_type)

# for bonus! to be double checked pa
# special characters inside YARN:  :) newline, :> tab, :o bell, :" quote, :: colon
def convertSpecialCharacters(text):
    result = ""
    i = 0
    while i < len(text):
        if text[i] == ":" and i + 1 < len(text):
            next_char = text[i + 1]
            if next_char == ")":
                result = result + "\n"
                i = i + 2
            elif next_char == ">":
                result = result + "\t"
                i = i + 2
            elif next_char == "o":
                result = result + "\a"
                i = i + 2
            elif next_char == '"':
                result = result + '"'
                i = i + 2
            elif next_char == ":":
                result = result + ":"
                i = i + 2
            else: #hindi special character, isama lang yung :
                result = result + text[i]
                i = i + 1
        else:
            result = result + text[i]
            i = i + 1
    return result

#EXPRESSIONS
ARITHMETIC = ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]
BOOLEAN = ["BOTH OF", "EITHER OF", "WON OF", "NOT", "ALL OF", "ANY OF"]
COMPARISON = ["BOTH SAEM", "DIFFRINT"]
TYPES = ["NOOB", "TROOF", "NUMBR", "NUMBAR", "YARN"]

def evalArithmetic(operator, op1, op2):
    op1_type = getDataType(op1)
    op2_type = getDataType(op2)

    #TROOF is cast to NUMBR (WIN = 1, FAIL = 0)
    if op1_type not in ["NUMBR", "NUMBAR"]:
        if (op1_type == "YARN" and "." not in op1) or (op1_type == "TROOF"):
            op1 = typecast(op1, "NUMBR")
        else:
            op1 = typecast(op1, "NUMBAR")

    if op2_type not in ["NUMBR", "NUMBAR"]:
        if (op2_type == "YARN" and "." not in op2) or (op2_type == "TROOF"):
            op2 = typecast(op2, "NUMBR")
        else:
            op2 = typecast(op2, "NUMBAR")

    # kapag may isang NUMBAR, gawing NUMBAR yung dalawa (para tama yung BIGGR OF / SMALLR OF)
    if getDataType(op1) == "NUMBAR" or getDataType(op2) == "NUMBAR":
        op1 = float(op1)
        op2 = float(op2)

    if operator == "SUM OF":
        return op1 + op2
    elif operator == "DIFF OF":
        return op1 - op2
    elif operator == "PRODUKT OF":
        return op1 * op2

    elif operator == "QUOSHUNT OF":
        if op2 == 0:
            error("division by zero")
        #kapag parehong NUMBR, NUMBR din ang result
        if getDataType(op1) == "NUMBR" and getDataType(op2) == "NUMBR":
            return int(op1 / op2)
        else:
            return op1 / op2

    elif operator == "MOD OF":
        if op2 == 0:
            error("division by zero")
        return op1 % op2

    elif operator == "BIGGR OF":
        return max(op1, op2)

    elif operator == "SMALLR OF":
        return min(op1, op2)

def evalBoolean(operator, op1, op2):
    # loop through x in op1 because 'all of' handles a list, then if there is one considered false
    #in the operands, return false, else if all are true, return true
    if operator == "ALL OF":
        for x in op1:
            if typecast(x, "TROOF") == False:
                return False
        return True

    #same logic as all of, only find a one operand with true value and then return true immediately
    if operator == "ANY OF":
        for x in op1:
            if typecast(x, "TROOF") == True:
                return True
        return False

    #typecase troof into NOT so the op1 gets its bool value and then use pythons 'not' to negate
    if operator == "NOT":
        op1 = typecast(op1, "TROOF")
        return op1 != True

    #we typecast it both operands to troof for lolcode boolean
    op1 = typecast(op1, "TROOF")
    op2 = typecast(op2, "TROOF")

    #use pythons 'and' which is equivalent to both of of lolcode
    if operator == "BOTH OF":
        return op1 and op2

    #use pythons 'or' which is equilvalent to either of of lolcode
    if operator == "EITHER OF":
        return op1 or op2

    #use pythons 'not equal' to which is equivalent to won of in lol code
    if operator == "WON OF":
        return op1 != op2

def evalComparison(operator, op1, op2):
    # - BOTH SAEM, DIFFRINT
    # - no automatic typecasting, e.g. yarn to numbr/numbar
    # - NUMBR comparison uses integer math
    # - NUMBAR comparison uses floating-point math

    #check if both are numeric
    if (getDataType(op1) == "NUMBR" or getDataType(op1) == "NUMBAR") and (getDataType(op2) == "NUMBR" or getDataType(op2) == "NUMBAR"):
        pass
    elif getDataType(op1) != getDataType(op2): # no automatic typecasting
        error("no automatic typecasting for " + getDataType(op1) + " '" + str(op1) + "' and " + getDataType(op2) + " '" + str(op2) + "'")

    if operator == "BOTH SAEM":
        return op1 == op2
    elif operator == "DIFFRINT":
        return op1 != op2

#evaluate an expression node from the syntax tree, returns the python value
def evalExpression(node):
    kind = node[0]

    #if literal, kunin yung value (nasa tree na yung python value)
    if kind == "LITERAL":
        if getDataType(node[1]) == "YARN": #for bonus! YARN literal, convert special characters
            return convertSpecialCharacters(node[1])
        else:
            return node[1]

    #if var, find its value in the symbol table
    if kind == "VAR":
        return getVal(node[1])

    #if arithmetic operator, evaluate the 2 operands first
    if kind in ARITHMETIC:
        op1 = evalExpression(node[1])
        op2 = evalExpression(node[2])
        return evalArithmetic(kind, op1, op2)

    if kind in COMPARISON:
        op1 = evalExpression(node[1])
        op2 = evalExpression(node[2])
        return evalComparison(kind, op1, op2)

    #these need 2 operands
    if kind == "BOTH OF" or kind == "EITHER OF" or kind == "WON OF":
        op1 = evalExpression(node[1])
        op2 = evalExpression(node[2])
        return evalBoolean(kind, op1, op2)

    #1 operand lang
    if kind == "NOT":
        op1 = evalExpression(node[1])
        return evalBoolean("NOT", op1, None)

    #take all operands then pass as a list
    if kind == "ALL OF" or kind == "ANY OF":
        operands = []
        for operand in node[1]:
            operands.append(evalExpression(operand))
        return evalBoolean(kind, operands, None)

    #concatenate all operands after casting them to YARN
    if kind == "SMOOSH":
        result = ""
        for operand in node[1]:
            value = evalExpression(operand)
            result = result + typecast(value, "YARN")
        return result

    #maek expression a type, hindi nababago yung variable
    if kind == "MAEK":
        value = evalExpression(node[1])
        return typecast(value, node[2], True)

    #function call
    if kind == "I IZ":
        return callFunction(node[1], node[2])

def callFunction(name, argument_nodes):
    global symbol_table

    if name not in functions:
        error("undefined function " + name)
    parameters = functions[name][0]
    function_block = functions[name][1]

    #the expressions must be executed first before executing the function body
    arguments = []
    for node in argument_nodes:
        arguments.append(evalExpression(node))

    #functions cannot access identifiers outside of it, so sariling symbol table
    saved_table = symbol_table
    symbol_table = [["IT", None, "NOOB"]]
    for k in range(len(parameters)):
        storeVal(parameters[k], arguments[k]) #pass by value

    result = exec_cond_block(function_block)
    symbol_table = saved_table #ibalik yung symbol table ng caller

    #walang return or GTFO = NOOB
    if result is not None and result != "GTFO":
        return_value = result[1] #FOUND YR <value>
    else:
        return_value = None

    storeVal("IT", return_value) #return values are stored in IT
    return return_value

#STATEMENTS
#returns None kapag normal, "GTFO" kapag nag-break, ["FOUND YR", value] kapag nag-return

#I HAS <var> ITZ <val>
def declaration(node):
    var_name = node[1]

    if findVar(var_name) != -1:
        error("redeclared variable " + var_name)

    value = None #NOOB default

    #optional ITZ, evaluate if meron
    if node[2] is not None:
        value = evalExpression(node[2])

    storeVal(var_name, value)

def assignment(node):
    var_name = node[1]

    #check if var is declared
    if findVar(var_name) == -1:
        error("undeclared variable " + var_name)

    value = evalExpression(node[2])
    storeVal(var_name, value)

# var IS NOW A type, change type mostly typecasting ulit
def recast(node):
    var_name = node[1]
    var_index = findVar(var_name)

    if var_index == -1:
        error("undeclared variable " + var_name)

    new_type = node[2]
    result = typecast(symbol_table[var_index][1], new_type, True)
    storeVal(var_name, result)

def visible(node):
    output = ""

    for expression in node[1]:
        value = evalExpression(expression)
        #implicit typecast sa YARN
        text = typecast(value, "YARN")
        output = output + text

    if node[2] == True: #automatically adds newline (unless may ! sa dulo) THIS ONES BUNOS TO BE CHECKED ALSo
        output = output + "\n"

    console_output.append(output)
    if output_function is not None: #para lumabas agad sa GUI console
        output_function(output)

#GIMMEH var
def gimmeh(node):
    #find if existing yung hinihingi
    var_name = node[1]
    if findVar(var_name) == -1:
        error("undeclared variable " + var_name)

    storeVal(var_name, input_function(var_name)) #the input value is always a YARN

#lagay result sa IT
def exprStatement(node):
    value = evalExpression(node[1])
    storeVal("IT", value)

def statement(node):
    kind = node[0]

    if kind == "DECLARE":
        declaration(node)
    elif kind == "VISIBLE":
        visible(node)
    elif kind == "GIMMEH":
        gimmeh(node)
    elif kind == "ASSIGN":
        assignment(node)
    elif kind == "RECAST":
        recast(node)
    elif kind == "EXPRESSION":
        exprStatement(node)
    elif kind == "IF":
        return conditional(node)
    elif kind == "SWITCH":
        return switch(node)
    elif kind == "LOOP":
        return loop(node)
    elif kind == "GTFO":
        return "GTFO"
    elif kind == "FOUND YR":
        value = evalExpression(node[1])
        return ["FOUND YR", value]

    return None

#execute statements one by one, titigil kapag may GTFO or FOUND YR
def exec_cond_block(block):
    for node in block:
        result = statement(node)
        if result is not None:
            return result #ipasa pataas yung GTFO / FOUND YR
    return None

#note: YA RLY if, MEBBE else if, NO WAI else
def conditional(node):
    if_block = node[1]
    mebbe_list = node[2]
    else_block = node[3]

    it_value = getVal("IT")

    #if IT can be cast to WIN, the if-clause executes
    if typecast(it_value, "TROOF") == True:
        return exec_cond_block(if_block)

    #for bonus! to be double checked pa (MEBBE/else-if)
    for mebbe in mebbe_list:
        value = evalExpression(mebbe[0])
        storeVal("IT", value) #MEBBE expression result goes to IT din
        if typecast(value, "TROOF") == True:
            return exec_cond_block(mebbe[1])

    #otherwise, the else-clause executes
    if else_block is not None:
        return exec_cond_block(else_block)
    else:
        return None

#check kung equal si IT at yung OMG case, no typecasting pero 1 and 1.0 should be equal
def isCaseMatch(it_value, case_value):
    it_type = getDataType(it_value)
    case_type = getDataType(case_value)

    if (it_type == "NUMBR" or it_type == "NUMBAR") and (case_type == "NUMBR" or case_type == "NUMBAR"):
        return it_value == case_value
    elif it_type != case_type: #iba yung type, hindi match
        return False
    else:
        return it_value == case_value

#WTF? compares IT to each OMG case
def switch(node):
    cases = node[1]
    default_block = node[2]
    it_value = getVal("IT")

    #hanapin yung unang case na equal kay IT
    matched = -1
    for k in range(len(cases)):
        case_value = evalExpression(cases[k][0])
        if isCaseMatch(it_value, case_value) == True:
            matched = k
            break

    #execute from the matched case until GTFO or OIC (fall through sa mga susunod na case)
    blocks = []
    if matched != -1:
        for k in range(matched, len(cases)):
            blocks.append(cases[k][1])
    if default_block is not None: #default case (or fall through papunta sa default)
        blocks.append(default_block)

    for block in blocks:
        result = exec_cond_block(block)
        if result == "GTFO": #GTFO = break, labas na sa switch
            return None
        elif result is not None: #FOUND YR, ipasa pataas sa function
            return result
    return None

def loop(node):
    operation = node[2]
    var_name = node[3]
    condition_type = node[4]
    condition = node[5]
    loop_block = node[6]

    if findVar(var_name) == -1: #the variable should be an existing variable
        error("undeclared loop variable " + var_name)

    while True:
        #TIL: repeat while FAIL, WILE: repeat while WIN
        if condition_type is not None:
            value = typecast(evalExpression(condition), "TROOF")
            if condition_type == "TIL" and value == True:
                break
            if condition_type == "WILE" and value == False:
                break

        result = exec_cond_block(loop_block)
        if result == "GTFO": #GTFO = break
            break
        elif result is not None: #FOUND YR sa loob ng loop, ipasa pataas sa function
            return result

        #UPPIN = +1, NERFIN = -1 (same rules as SUM OF / DIFF OF, kaya kailangan castable sa number)
        current_value = getVal(var_name)
        if operation == "UPPIN":
            storeVal(var_name, evalArithmetic("SUM OF", current_value, 1))
        else:
            storeVal(var_name, evalArithmetic("DIFF OF", current_value, 1))

    return None

#value as text for the symbol table in the GUI
def displayValue(value):
    data_type = getDataType(value)
    if data_type == "NOOB":
        return "NOOB"
    elif data_type == "TROOF" or data_type == "NUMBAR":
        return typecast(value, "YARN")
    else:
        return str(value)

# returns [success, error message]
# tree is the syntax tree galing sa syntax_analyzer.parseProgram()
def runProgram(tree):
    global symbol_table, console_output, functions
    # reset table
    #it's default is always none and noob
    symbol_table = [["IT", None, "NOOB"]]
    console_output = []
    functions = tree["functions"]

    try:
        #wazzup block
        exec_cond_block(tree["declarations"])
        #main program
        exec_cond_block(tree["body"])
    except LOLSemanticError as e:
        return False, str(e)

    return True, ""
