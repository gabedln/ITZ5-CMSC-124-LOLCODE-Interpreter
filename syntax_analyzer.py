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

import re # import regex
from lexical_analyzer import getLexemes # we reuse the lexical analyzer

# ------------- example code -----------
valid_code = """HAI
I HAS A var ITZ 5
VISIBLE var
KTHXBYE"""

# ------------- example code 2 ---------
valid_code2 = """HAI
I HAS A var ITZ 12
I HAS A other
VISIBLE "noot noot" var 3.14 WIN other
KTHXBYE"""

# -------- separate natin ung mga operations na may two arity and infinite arity --------
# ang logic dito is: kailangang mag match para alam kung ilang parameters ittake
two_arity = ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF",
"BOTH OF", "EITHER OF", "WON OF", "BOTH SAEM", "DIFFRINT", "BIGGR OF", "SMALLR OF"]
infinite_arity = ["ANY OF", "ALL OF"]
# ------------------------------------------------------------------------------------------

# ------------------------ parsing for ITZ (declaration of variables) ---------------------------------------------------------------------------------
def parseValue(tokens, i): # returns the index of the next token (-1 if failed)
    if i >= len(tokens): # if we go past and there is no value, then we just return -1
        return -1

    if tokens[i][1] in ["NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "Variable Identifier"]: # NUMBR, NUMBAR, TROOF or variable
        return i + 1 # return i + 1

    if tokens[i][1] == "String Delimiter": # in our lexical table, YARN (string)  is made up of three parts (quotation, string literal, and quotation)
        if i + 2 < len(tokens) and tokens[i + 1][1] == "YARN Literal" and tokens[i + 2][1] == "String Delimiter":
            return i + 3

    return -1 # anything else is not a value
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for I HAS A (declaration of variables) ---------------------------------------------------------------------------------
def parseDeclaration(tokens, i): # parse for I HAS A
    i += 1 # since we pass i (index of I HAS A), we move past that
    if i >= len(tokens) or tokens[i][1] != "Identifier": # if i > tokens (meaning there isn't a parameter) or if i isn't an identifier
        return -1 # immediately returns -1 (which returns false)
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', tokens[i][0]):
        # Variable names must start with a letter, followed by any combination of letters, numbers, and underscores. No spaces, dashes, or other special symbols are allowed to be part of the variable name.
        # if the variable name does not match this regex, then invalid identifier and return -1
        return -1
    
    if tokens[i][0] in ["HAI", "KTHXBYE", "ITZ", "VISIBLE"]: # keywords can't be variable names
        return -1 
    
    i += 1 # we check if there is ITZ

    if i < len(tokens) and tokens[i][1] == "Variable Assignment": # ITZ is optional, but if there is an ITZ we need to check if there is a coresponding value
        return parseValue(tokens, i + 1) # we pass the i+1 and tokens to parseValue
    return i # else if there is no ITZ, we just return i
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------ parsing for VISIBLE (printing output) ---------------------------------------------------------------------------------
def parseOutput(tokens, i): # VISIBLE has infiinte arity, meaning it can take n number of inputs
    i = parseValue(tokens, i + 1) # we  check if the value to the next of VISIBLE is a valid value, then update i 

    if i == -1: # if i == -1, meaning invalid, then we return -1
        return -1

    while True: # infinite arity ; keep taking values until there are no more
        j = parseValue(tokens, i) # we continously call parseValue and check if it is valid
        if j == -1: # once parseValue returns invalid, we break out of the while true loop and return i 
            break
        i = j # else, we update i to the value of j

    return i
# --------------------------------------------------------------------------------------------------------------------------------------------------

def parseExpression(tokens, i):
    return

def parseDeclaration(tokens, i):
    return

def parseAssignment(tokens, i):
    return

def parseCasting(tokens, i):
    return

def parseOutput(tokens, i):
    return

def parseInput(tokens, i):
    return

def parseConditional(tokens, i):
    return

def parseSwitch(tokens, i):
    return

def parseLoop(tokens, i):
    return

def parseFunction(tokens, i):
    return


def parseStatement(tokens, i):
    return

# ------------------------ code for checking syntax ---------------------------------------------------------------------------------
def checkSyntax(code): # function that returns True if syntax is valid; else returns False
    lexical_table = getLexemes(code) # we use lexical analysis from previous milestone (use getLexemes function)
    if lexical_table==None: # lexical analyzer will return None if it doesn't start with HAI and end in KTHXBYE
        return False # returns false

    tokens = lexical_table[1:-1] # the tokens in between HAI and KTHXBYE
    i = 0 # iteration

    # since kailangan ng WAZZUP at BUHBYE for variable declaration; titignan if meron (if wala, okay lang, pero bawal na mag declare ng variables)
    if i < len(tokens) and tokens[i][0] == "WAZZUP" and tokens[i][1] == "Variable Declaration Delimiter":
        i += 1 # move past WAZZUP
        while i < len(tokens) and tokens[i][0] != "BUHBYE" and tokens[i][1] != "Variable Declaration Delimiter": # while we haven't seen BUHBYE;
            if tokens[i][0] == "I HAS A" and tokens[i][1] == "Variable Declaration":
                i = parseDeclaration(tokens, i) # parse declarations (e.g I HAS A var)
                if i == -1: # if invalid, return false
                    return False
            else: # if no I HAS A, retunr false
                return False
        
        # if we reach the end and we don't see BUHBYE (not matching WAZZUP...BUHBYE) we return FALSE
        if i >= len(tokens) or tokens[i][0] != BUHBYE and tokens[i][1] != "Variable Declaration Delimiter":
            return False
        i += 1 # move past the block
            

    while i < len(tokens): # while we haven't reached the end of all our tokens;
        i = parseStatement(tokens, i) # parse remaining statements
        if i == -1: # the statement was not valid
            return False

    return True
# -------------------------------------------------------------------------------------------------------------------------------------

def main(): # run examples
    print("valid_code  :", checkSyntax(valid_code))
    print("valid_code2 :", checkSyntax(valid_code2))

main()