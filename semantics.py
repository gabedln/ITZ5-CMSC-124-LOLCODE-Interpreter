# Sources: 
# https://github.com/amtuazon4/PyGUI/blob/main/source%20code/check_semantics.py
# Project Requirement # 3 - Semantics

#SEMANTICS CHECKLIST/THINGS TO CONSIDER

#1. State & Program Structure (p. 2-3)
# a. Variables
# - remember variables current type and value
#   (var -> type, value)
# - variables are dynamically typed
# - NOOB is default datatype
# - check for redeclared/undeclared variables
# - all variables must be inside WAZZUP

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
# - ALL OF and ANY OF can't be nested
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

# 6. Functions (p. 8)


from lexical_analyzer import getLexemes
import re # import regex
from decimal import Decimal, ROUND_DOWN # for exact truncation of NUMBAR -> YARN

# ------------- example code -----------
valid_code = """HAI
WAZZUP
I HAS A x ITZ 10
BUHBYE
VISIBLE x
KTHXBYE"""

# ------------- example code 2 (needs SUM OF, skeleton pa lang) ---------
valid_code2 = """HAI
WAZZUP
I HAS A x ITZ 5
I HAS A y
BUHBYE
y R SUM OF x AN 3
VISIBLE "noot noot" y
KTHXBYE"""
 
# ------------- example code 3 (IT, assignment, IS NOW A) ---------
valid_code3 = """HAI
WAZZUP
I HAS A x ITZ 5
I HAS A y ITZ x
BUHBYE
x R 7
x
VISIBLE IT
y IS NOW A NUMBAR
VISIBLE "x is " x " and y is " y
KTHXBYE"""

symbol_table = [] #[identifier, value, data_type] -> ["a", 10, "NUMBR"]
console_output = [] #para sa console (6) ng GUI

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

# TYPECASTING RULES
# implicit - automatic casting
# explicit - could be done using the MAEK operator or IS NOW A
def typecast(val, new_data_type, explicit=False):
    #NOOBs can be implicitly typecast into TROOF. Implicit typecasting to any other type
    #except TROOF will result in an error. Explicit typecasting of NOOBs is allowed and results to empty/zero values (SPECS)
    data_type = getDataType(val) #get the current data type

    if data_type == new_data_type: #data type is already correct
        return val
    
    if new_data_type == "NOOB": #casting to NOOB is only through MAEK, basically bawal explicit typecasting
        if explicit:
            return None
        print(f"Semantic Error: cannot implicitly typecast {data_type} to NOOB")
        return None
    
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
            print(f"Semantic Error: cannot implicitly typecast NOOB to {new_data_type}")
            return None
        
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
            #val = int(val)
            return int(val)
        #if yarn, convert the value to string of characters
        if new_data_type == "YARN":
            #val = str(val)
            return str(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)) # truncate to 2 decimal places
        #consider troof also, kapag 0 false, other value true
        if new_data_type == "TROOF":
            if val == 0:
                return False
            else:
                return True

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
            if val == 0:
                return False
            else:
                return True

    #YARN TYPECASTING RULES
    if data_type == "YARN":
        if new_data_type == "TROOF":
            #empty string are cast to fail
            if val == "":
                return False
            else: #if not cast to win automatically
                return True

        if new_data_type == "NUMBR" or new_data_type == "NUMBAR":
            for char in val:
                #can be successfully cast if it contains non-numerical, non-hyphen, non-period characs
                if not char.isdigit() and char != "-" and char != ".":
                    print(f"Semantic Error: cannot typecast '{val}' to {new_data_type}")
                    return None

            if not re.match(r'^-?[0-9]+(\.[0-9]+)?$', val):
                print(f"Semantic Error: cannot typecast '{val}' to {new_data_type}")
                return None
            if new_data_type == "NUMBR":
                return int(float(val))
            return float(val)

#EXPRESSIONS
ARITHMETIC = ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]
BOOLEAN = ["BOTH OF", "EITHER OF", "WON OF", "NOT", "ALL OF", "ANY OF"]
COMPARISON = ["BOTH SAEM", "DIFFRINT"]
TYPES = ["NOOB", "TROOF", "NUMBR", "NUMBAR", "YARN"]

#skip mga nasa loob ng string
def isKeyword(token, words):
    return token[1] != "YARN Literal" and token[0] in words

#check if start ng expression or value
def isValue(token):
    return token[1] in ["NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "Variable Identifier", 
                        "String Delimiter"] or isKeyword(token, ARITHMETIC + BOOLEAN + COMPARISON + ["SMOOSH", "MAEK"])

#converts a lexer token
def getLiteralValue(token):
    if token[1] == "TROOF Literal":
        if token[0] == "WIN":
            return True
        else:
            return False
    if token[1] == "NUMBR Literal":
        return int(token[0])  #here
    if token[1] == "NUMBAR Literal":
        return float(token[0])
    return token[0] # YARN Literal  

#check if token is a literal
def isLiteral(token):
    return token[1] in ["NUMBR Literal", 
                        "NUMBAR Literal", 
                        "TROOF Literal"]

def evalArithmetic(operator, op1, op2):
    op1_type = getDataType(op1)
    op2_type = getDataType(op2)

    if op1_type not in ["NUMBR", "NUMBAR"]:
        op1 = typecast(op1, "NUMBAR")

    if op2_type not in ["NUMBR", "NUMBAR"]:
        op2 = typecast(op2, "NUMBAR")

    if op1 is None or op2 is None:
        return None

    if operator == "SUM OF":
        return op1 + op2
    elif operator == "DIFF OF":
        return op1 - op2
    elif operator == "PRODUKT OF":
        return op1 * op2

    elif operator == "QUOSHUNT OF":
        if op2 == 0:
            print("Semantic Error: division by zero")
            return None
        return op1 / op2

    elif operator == "MOD OF":
        if op2 == 0:
            print("Semantic Error: division by zero")
            return None
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

    #typecase troof into NOT so the op1 gets its bool value and then use pythons 'not' to negate 
    if operator == "NOT":
        op1 = typecast(op1, "TROOF")
        return not op1

def evalComparison(operator, op1, op2):
    # - BOTH SAEM, DIFFRINT
    # - no automatic typecasting, e.g. yarn to numbr/numbar
    # - NUMBR comparison uses integer math
    # - NUMBAR comparison uses floating-point math

    #check if both are numeric
    if (getDataType(op1) == "NUMBR" or getDataType(op1) == "NUMBAR") and (getDataType(op2) == "NUMBR" or getDataType(op2) == "NUMBAR"):
        pass
    elif getDataType(op1) != getDataType(op2): # no automatic typecasting
        print("Semantic Error: no automatic typecasting for " + getDataType(op1) + " '" + str(op1) + "' and " + getDataType(op2) + " '" + str(op2) + "'")
        return None
    
    if operator == "BOTH SAEM":
        return op1 == op2
    elif operator == "DIFFRINT":
        return op1 != op2

#since buong program nasa tokens, need hanapin yung end for eval expression
def findExpressionEnd(tokens, i):
    needed_op = 1 #start with 1 
    lists = [] #added for all of and any of
    j = i

    #keep going while we still need operands (or an ALL OF / ANY OF is still waiting for its MKAY)
    while j < len(tokens) and (needed_op > 0 or len(lists) > 0):
        token = tokens[j]

        #string is 3 tokens " text " and counts as one val
        if token[1] == "String Delimiter":
            if j + 2 < len(tokens) and tokens[j + 1][1] == "YARN Literal" and tokens[j + 2][1] == "String Delimiter":
                needed_op -= 1
                j += 3
                continue
            break

        # pag binary operator, kailangan niya ng 2 operands
        elif isKeyword(token, ARITHMETIC + COMPARISON + ["BOTH OF", "EITHER OF", "WON OF"]):
            needed_op += 1
        # pag literal or variable, may nakuha na so -1
        elif isLiteral(token) or token[1] == "Variable Identifier":
            needed_op -= 1

        #1 operand for not, keep current count
        elif isKeyword(token, ["NOT"]):
            pass

        #take operands until mkay
        elif isKeyword(token, ["ALL OF", "ANY OF"]):
            lists.append(needed_op - 1)
            needed_op = 1

        elif token[0] == "AN":
            if len(lists) > 0 and needed_op == 0:
                needed_op = 1

        elif token[0] == "MKAY" and len(lists) > 0:
            if needed_op != 0:
                break
            needed_op = lists.pop()

        else:
            break

        j += 1

    #if wala nang needed operand, kumpleto na expression
    if needed_op == 0 and len(lists) == 0:
        return j

    print("Semantic Error: invalid expression")
    return i

MKAY_FOUND = object() #need to mark mkay to know where any of, all of stops

def evalExpression(tokens, i):
    #temporary storage of values, e.g. SUM OF 1 AN 2, store niya 1, 2 tapos later ay yung result
    values = [] 

    end = findExpressionEnd(tokens, i)
    if end == i:
        return None, i
    
    j = end - 1 #last index ng token list, right to left babasahin since prefix

    #read all tokens that are part of the expression
    while j >= i:
        token = tokens[j]
        token_value = token[0]
        token_type = token[1]
 
        #find the delimiter first, push the text and skip 3 tokens since 1 val lang sha 
        if token_type == "String Delimiter":
            values.append(tokens[j - 1][0])
            j -= 3
            continue

        #if literal, kunin yung value and i-append sa stack
        if isLiteral(token):
            values.append(getLiteralValue(token))

        #if var, find its value in the symbol table
        elif token_type == "Variable Identifier":
            var_index = findVar(token_value)

            #if not found then undeclared var siya
            if var_index == -1:
                print("Semantic Error: undeclared variable", token_value)
                values.append(None)
            #append the found value
            else:
                values.append(symbol_table[var_index][1])

        #if arithmetic operator, get 2 operands from stack
        elif isKeyword(token, ARITHMETIC):
            op1 = values.pop()
            op2 = values.pop()
            #append the result to stack (for nested expressions)
            values.append(evalArithmetic(token[0], op1, op2))

        elif isKeyword(token, COMPARISON):
            op1 = values.pop()
            op2 = values.pop()
            #evaluate comparison
            values.append(evalComparison(token_value, op1, op2))

        #these need 2 operands from stack
        elif isKeyword(token, ["BOTH OF", "EITHER OF", "WON OF"]):
            op1 = values.pop()
            op2 = values.pop()
            values.append(evalBoolean(token_value, op1, op2))

        #if not, get 1 operand from stack
        elif isKeyword(token, ["NOT"]):
            op1 = values.pop()
            values.append(evalBoolean("NOT", op1, None))

        elif token_value == "AN":
            pass

        #put a marker on the stack for all of and any of
        elif token_value == "MKAY":
            values.append(MKAY_FOUND)

        #take all operands until mkay is not yet found
        elif isKeyword(token, ["ALL OF", "ANY OF"]):
            operands = []
            while values[-1] is not MKAY_FOUND:
                operands.append(values.pop())
            values.pop() #remove the marker
            values.append(evalBoolean(token[0], operands, None))

        j -= 1     

        #final result lang dapat matira sa stack
        if j == len(tokens) - 1:
            print("Semantic Error: invalid expression")
            return None, i

    #result and index of the next token
    return values[0], end

#maek expression a type, maek expression type
def evalMaek(tokens, i):
    #evaluate the expression after "Maek"
    #j yung index kung when nagend expression
    value, j = evalExpression(tokens, i + 1)
    if j == i + 1: #walang expression after maek
        return None, i

    # since a is optional.. pag may a move to the next token
    if j < len(tokens) and isKeyword(tokens[j], ["A"]):
        j += 1

    #check if token is a valid data type 
    if j >= len(tokens) or tokens[j][0] not in TYPES:
        print("Semantic Error: MAEK doesn't have a type")
        return None, i

    #typecast to needed type tokens[j][0]
    return typecast(value, tokens[j][0], True), j + 1

#value of expression, return tayo ng val and next index
def evalValue(tokens, i):
    if i < len(tokens) and isKeyword(tokens[i], ["MAEK"]):
        #if token is MAEK, evalMaek
        return evalMaek(tokens, i)
    #if not proceed agad sa evalExpr
    return evalExpression(tokens, i)

# TEST FOR EVAL ARITHMETIC
test_tokens = [
    ["VISIBLE", "Output Keyword"],
    ["SUM OF", "Addition Operation"],
    ["5", "NUMBR Literal"],
    ["AN", "Delimiter"],
    ["PRODUKT OF", "Multiplication Operation"],
    ["2", "NUMBR Literal"],
    ["AN", "Delimiter"],
    ["3", "NUMBR Literal"],
    ["VISIBLE", "Output Keyword"],
    ["10", "NUMBR Literal"]
]

result, next_index = evalExpression(test_tokens, 1)

print(result)
print(next_index)
print(test_tokens[next_index])
