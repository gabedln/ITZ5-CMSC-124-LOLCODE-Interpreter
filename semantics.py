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
    return token[1] in ["NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "Variable Identifier", "String Delimiter"] or isKeyword(token, ARITHMETIC + BOOLEAN + COMPARISON + ["SMOOSH", "MAEK"])

#converts a lexer token into a python value
def getLiteralValue(token):
    if token[1] == "TROOF Literal":
        return token[0] == "WIN"
    if token[1] == "NUMBR Literal":
        return int(token[0])  #here
    if token[1] == "NUMBAR Literal":
        return float(token[0])
    return token[0] # YARN Literal  
#SKELETON PA LANG

#evaluates an expr
def evalExpr(tokens, i):
    # prefix, binary, AN is required between the operands
    # operands can be nested expressions
    # both NUMBR result is NUMBR, at least one NUMBAR result is NUMBAR
    #type cast those not NUMBR/NUMBAR, if cannot ay error
    pass

def evalArithmetic(tokens,i):
    pass

def evalBoolean(tokens, i):
    pass

def evalComparison(tokens, i):
    pass
 
 
def evalMaek(tokens, i):
    pass






