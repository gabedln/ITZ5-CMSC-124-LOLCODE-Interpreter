# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 1 - Lexemes 

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

import re  # import regex

# ------------- example code -----------
code = """HAI
    I HAS A var ITZ 5 BTW this is a comment
    OBTW
    this should not be
    seen
    amen?
    TLDR
    VISIBLE var
    KTHXBYE"""

# ------------- example code 2 ---------
code2 = """BTW this is a comment too
    HAI BTW this is a comment
    I HAS A var ITZ 12
    VISIBLE "noot noot" var
    OBTW
    in line comment
    TLDR
    KTHXBYE"""

# ------------- example code 3 (with comments) ---------
code3 = """HAI
    BTW this is a comment
    I HAS A x ITZ 10
    OBTW
    this whole block is a comment
    TLDR
    VISIBLE x
    KTHXBYE"""

# ------------- example code 4 (with WAZZUP block and more keywords) ---------
code4 = """HAI
    WAZZUP
        I HAS A a ITZ 0
        I HAS A b
    BUHBYE
    b R SUM OF a AN 5
    VISIBLE b
    KTHXBYE"""

# ------------------------------------------------------------------------------------------------------------
# FUNCTION FOR DEALING WITH COMMENTS:
# comments are not considered statements and must be ignored; we will STRIP COMMENTS AWAY before passing to getLexemes() function
def stripComments(code):
    clean_lines = [] # init empty list for clean lines
    obtw_tldr = False # flag tracker for obtw_tldr (comment block)

    code_lines = code.split("\n") # split the code into lines
    for line in code_lines:
        stripped_line = line.strip() # strip the line to remove leading/trailing whitespace

        if stripped_line == "OBTW": # if OBTW start, we set the flag to True and continue 
            obtw_tldr = True
            continue
        elif stripped_line == "TLDR": # if TLDR, we end the flag and continue
            obtw_tldr = False
            continue
        elif obtw_tldr: # while obtw_tldr == TRUE, we just continue
            continue # wala tayong pake sa lines of code kapag naka enclose sa OBTW and TLDR

        match = re.search(r'BTW', stripped_line)

        if match: # if may nahanap tayong BTW sa line, we will only pass the part before it to the clean_lines list
            stripped_line = stripped_line[:match.start()].strip() # remove comment part

        if stripped_line: # if the stripped line is not empty, we add it to the clean_lines list
            clean_lines.append(stripped_line) # add the cleaned line to the list

    if obtw_tldr == True: # kapag TRUE parin siya even after, ibig sabihin hindi na close so syntax error
        print("Syntax Error: Unclosed comment block (OBTW without TLDR)")
        return None

    return "\n".join(clean_lines) # join the cleaned lines back into a single string
# ------------------------------------------------------------------------------------------------------------

# ------------- FUNCTION FOR GETTING LEXEMES -----------------------------------------------------------------
def getLexemes(code): # function for getting lexemes
    lexical_table = [] # init for lexical table (blank)

    pl_element = [ # PL elements, regex, and classification
            #  ---------------- code delimiters ------------------------------
            ['HAI', "Code Delimiter"], # format is [TABLENAME, REGEX, CLASSIFICATION]
            ['KTHXBYE', "Code Delimiter"],

            #------------------- variable declarations -----------------------
            ['WAZZUP', "Variable Declaration Delimeter"],
            ['BUHBYE', "Variable Declaration Delimeter"],
            ['BTW', "Comment Delimiter"],
            ['OBTW', "Comment Delimiter"],
            ['TLDR', "Comment Delimiter"],
            ['I HAS A', "Variable Declaration"],
            ['ITZ', "Variable Assignment"],
            ['R', "Variable Assignment"],

            # ---------- arithmetic operations -----------------------------
            ['SUM OF', "Addition Operation"],
            ['DIFF OF', "Subtraction Operation"],
            ['PRODUKT OF', "Multiplication Operation"],
            ['QUOSHUNT OF', "Division Operation"],
            ['MOD OF', "Modulo Operation"],
            ['AN', "Delimiter"],

            # ------------- boolean operations --------------------
            ['BOTH OF', "AND Operation"],
            ['EITHER OF', "OR Operation"],
            ['WON OF', 'XOR Operation'],
            ['NOT', "NOT Operation"],
            ['ANY OF', 'Infinite OR Operation'],
            ['ALL OF', 'Infinite AND Operation'],

            # --------------- comparison operations -----------------
            ['BOTH SAEM', "Equality Operation"],
            ['DIFFRINT', "Inequality Operation"],
            ['BIGGR OF', "Max Operation"],
            ['SMALLR OF', "Min Operation"],

            # ---------------- string concatenation ------------------
            ['SMOOSH', 'String Concatenation'],

            # ----------------- type casting ------------------------
            ['MAEK', 'Type Casting'],
            ['A', 'Type Casting Qualifier'],
            ['IS NOW A', 'Type Casting Operation'],

            # ------------------ input and output (print() and input()) ----------
            ['VISIBLE','Output Keyword'],
            ['GIMMEH', 'Input Keyword'],

            # ------------------ flow-control statements -----------------
            ['O RLY?', 'Conditional Statement Delimiter'],
            ['YA RLY', 'If'],
            ['MEBBE', 'Else If'],
            ['OIC', 'End of If-Else Block'],
            ['NO WAI', 'Else'],

            # ------------------ loop statements -----------------
            ['IM IN YR', 'Loop Keyword'], 
            ['IM OUTTA YR', 'End of Loop Block'],

            # ----------------- increment and decrement statements -----------------
            ['UPPIN', 'Increment'],
            ['NERFIN', 'Decrement'],

            # ----------------- additional loop statements -----------------
            ['YR', 'Loop Identifier'],
            ['TIL', 'Until Loop'],
            ['WILE', 'While Loop'],

            #-------------------------------- function statements -----------------
            ['HOW IZ I', r'^HOW IZ I$', 'Function Definition'],
            ['IF U SAY SO', r'^IF U SAY SO$', 'Function Delimiter'],
            ['GTFO', r'^GTFO$', 'Function Return'],
            ['FOUND YR', r'^FOUND YR$', 'Function Return Value'],
            ['I IZ', r'^I IZ$', 'Function Return Value'],
            ['MKAY', r'^MKAY$', 'End of Code Delimiter']
    ]

    code = stripComments(code) # we will strip comments first before passing to getLexemes() function
    lines = code.split("\n") # we split the line into an array ; delimeter is new line

    if "HAI" == lines[0] and "KTHXBYE" == lines[-1]: # if HAI is in beginning and KTHXBYE at the end, that's when we do the rest
        lexical_table.append([pl_element[0][0], pl_element[0][1]]) # appends HAI

        for i in lines[1:-1]: # since we checked the start and the end already, we will iterate through first and last lines
            whole_string = i.strip() # strip the string to remove new line
            #print(f"Processing line: {whole_string}") # DEBUG: print line being procesed

            while whole_string != "": # while the string is not empty
                matched = False # initial bool; match false
                #print(f"Remaining string to process: {whole_string}") # print the remaining string to process

                if whole_string.startswith('"'): # For YARN literals, if starts with quotation
                    closing = whole_string.find('"', 1) # starting from index 1, we find the partner end quotation
                    if closing != -1: # if we found a closing;
                        yarn = whole_string[1:closing]   # we take the value in between quotations
                        lexical_table.append(['"', "String Delimiter"]) # add the quotation literal to lexical table;
                        lexical_table.append([yarn, "YARN Literal"]) # add the YARN literal to lexical table;
                        lexical_table.append(['"', "String Delimiter"]) # add the closing quotation literal to lexical table;
                        whole_string = whole_string[closing + 1:].strip() # removes
                    else:
                        print("Warning: unterminated string literal")
                        whole_string = ""
                    matched = True

                if not matched: # if after going through yarn literal still not match, we check each item in pl_element
                    for j in pl_element:
                        if whole_string.startswith(j[0]): # we use string comparison not regex
                            lexical_table.append([j[0], j[1]]) # appends 
                            whole_string = whole_string[len(j[0]):].strip()

                            # immediately grab the identifier that follows I HAS A
                            if j[0] == 'I HAS A': # if the PL matched is I HAS A
                                parts = whole_string.split()  # we split the remaining parts (var name can't have space)
                                if parts: # the first is the var name (the one right after I HAS A)
                                    var_name = parts[0]
                                    lexical_table.append([var_name, "Identifier"]) # then we add that to lexical table
                                    whole_string = whole_string[len(var_name):].strip()

                            matched = True # we find match
                            break

                if not matched: # if still not match, we look at initial
                    parts = whole_string.split(None, 1)
                    token = parts[0]
                    remaining  = parts[1].strip() if len(parts) > 1 else ""

                    if re.match(r'^-?[0-9]+$', token):           # number literal
                        lexical_table.append([int(token), "NUMBR Literal"])
                    elif re.match(r'^(WIN|FAIL)$', token):
                        lexical_table.append([token, "TROOF Literal"])
                    elif re.match(r'^-?[0-9]+\.[0-9]+$', token):
                        lexical_table.append([float(token), "NUMBAR Literal"])
                    # (YARN strings are handled before this block — no branch needed here)
                    elif re.match(r'^(TROOF|NOOB|NUMBR|NUMBAR|YARN)$', token): # must be checked before variable identifiers
                        lexical_table.append([token, "TYPE"]) 
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token) and len(lexical_table) > 0 and lexical_table[-1][0] in ('HOW IZ I', 'I IZ'): # function name
                        lexical_table.append([token, "Function Identifier"])
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token) and len(lexical_table) > 0 and lexical_table[-1][0] in ('IM IN YR', 'IM OUTTA YR'): # loop label
                        lexical_table.append([token, "Loop Label"])
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token):  # varident
                        lexical_table.append([token, "Variable Identifier"])
                    # elif re.match(r'^(TROOF|NOOB|NUMBR|NUMBAR|YARN)$', token):
                        # lexical_table.append([token, "TYPE"])
                    else:
                        print(f"Warning: unrecognized token '{token}'")

                    whole_string = remaining

        lexical_table.append([pl_element[1][0], pl_element[1][1]]) # appends KTHXBYE

    else: # else for initial if ; no HAI or no KTHXBYE (not at beginning or end) results in an error
        return None

    # ----- printing the lexical table --------------
    # print("\n-----------Lexical Table----------")
    # for line in lexical_table:
    #     print(f"{line[0]:<10} | {line[1]}")
    # print("----------------------------------")

    return lexical_table

# getLexemes(code)
# getLexemes(code2)
# getLexemes(code3)
# getLexemes(code4)