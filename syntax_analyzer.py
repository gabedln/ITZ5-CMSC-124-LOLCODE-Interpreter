# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 2 - Syntax Analyzer

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

# ------------------------ code for checking syntax ---------------------------------------------------------------------------------
def checkSyntax(code): # function that returns True if syntax is valid; else returns False
    lexical_table = getLexemes(code) # we use lexical analysis from previous milestone (use getLexemes function)
    if lexical_table==None: # lexical analyzer will return None if it doesn't start with HAI and end in KTHXBYE
        return False # returns false

    tokens = lexical_table[1:-1] # the tokens in between HAI and KTHXBYE
    i = 0 # iteration

    while i < len(tokens): # while we haven't reached the end of all our tokens;
        if tokens[i][1] == "Variable Declaration": # if the identified token is a Variable Declaration, then it is I HAS A
            i = parseDeclaration(tokens, i) # we parse the values (we pass i, and we pass the total tokens), then we update i

        elif tokens[i][1] == "Output Keyword": # if we identified it as Output Keyword, then we pass it to parseOutput
            i = parseOutput(tokens, i)

        else: # anything else can't start a statement
            return False

        if i == -1: # the statement was not valid
            return False

    return True
# -------------------------------------------------------------------------------------------------------------------------------------

def main(): # run examples
    print("valid_code  :", checkSyntax(valid_code))
    print("valid_code2 :", checkSyntax(valid_code2))

main()