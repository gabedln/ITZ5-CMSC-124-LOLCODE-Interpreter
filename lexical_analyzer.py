import re  # import regex

# ------------- example code -----------
code = """
HAI
  WAZZUP
    I HAS A x ITZ 1
  BUHBYE
  VISIBLE x
  I HAS A y ITZ 2
  VISIBLE y
KTHXBYE
"""

# ------------------------------------------------------------------------------------------------------------
# FUNCTION FOR DEALING WITH COMMENTS:
# comments are not considered statements and must be ignored; we will STRIP COMMENTS AWAY before passing to getLexemes() function
def stripComments(code):
    clean_lines = [] # init empty list for clean lines
    obtw_tldr = False # flag tracker for obtw_tldr (comment block)

    code_lines = code.split("\n") # split the code into lines
    for line in code_lines:
        stripped_line = line.strip() # strip the line to remove leading/trailing whitespace

        if re.match(r'^OBTW(?:\s|$)', stripped_line): # if OBTW, we set the flag to TRUE and continue
            if re.search(r'\bTLDR\b', stripped_line): # if TLDR and OBTW in same line, return None (error)
                return None
            obtw_tldr = True
            continue
        elif re.match(r'^TLDR(?:\s|$)', stripped_line): # if TLDR, we end the flag and continue
            if obtw_tldr == False: # if obtw_tldr is false when we encounter TLDR, it means there is no OBTW before TLDR
                return None
            after_tldr = stripped_line[4:].strip() # check if there is anything after TLDR
            if after_tldr and not re.match(r'^BTW(?:\s|$)', after_tldr): # if there is something after TLDR and it's not a BTW comment, return None (error)
                return None
            obtw_tldr = False
            continue

        elif obtw_tldr: # while obtw_tldr == TRUE, we just continue
            continue # wala tayong pake sa lines of code kapag naka enclose sa OBTW and TLDR
        
        # we use match iter because we find all instances of BTW
        for match in re.finditer(r'\bBTW\b', stripped_line): 
            before = stripped_line[:match.start()] # find everything before btw
            # e.g. I HAS A VAR ITZ 5BTW this is a comment
            # before = I HAS A VAR ITZ 5 (we remove btw and the rest)
            # if there are even numbers of quotes before (meaning closed quotes), then everything after BTW is a comment
            # if there are odd numbers of quotes before (only 1 quotation) there are two instances:
                # a) BTW is part of a string
                # b) Closed string (which would produce an error that we have catched)
            if before.count('"') % 2 == 0:
                stripped_line = before.strip()
                break

        if stripped_line: # if the stripped line is not empty, we add it to the clean_lines list
            clean_lines.append(stripped_line) # add the cleaned line to the list

    if obtw_tldr == True: # kapag TRUE parin siya even after, ibig sabihin hindi na close so syntax error
        print("Syntax Error: Unclosed comment block (OBTW without TLDR)")
        return None

    return "\n".join(clean_lines) # join the cleaned lines back into a single string
# ------------------------------------------------------------------------------------------------------------

# ------------- FUNCTION FOR GETTING LEXEMES -----------------------------------------------------------------
def getLexemes(code): # function for getting lexemes
    lexical_table = [] # init for lexical table (one token list per source line)

    pl_element = [ # PL elements, regex, and classification
            #  ---------------- code delimiters ------------------------------
            ['HAI', "Code Delimiter"], # format is [TABLENAME, REGEX, CLASSIFICATION]
            ['KTHXBYE', "Code Delimiter"],

            #------------------- variable declarations -----------------------
            ['WAZZUP', "Variable Declaration Delimiter"],
            ['BUHBYE', "Variable Declaration Delimiter"],
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
            ['+', 'Concatenation Delimiter'],
            ['GIMMEH', 'Input Keyword'],

            # ------------------ flow-control statements -----------------
            ['O RLY?', 'Conditional Statement Delimiter'],
            ['YA RLY', 'If'],
            ['MEBBE', 'Else If'],
            ['NO WAI', 'Else'],

            # ------------------ loop statements -----------------
            ['IM IN YR', 'Loop Keyword'], 
            ['IM OUTTA YR', 'End of Loop Block'],
            # ----------------- switch case statements ----------------------------
            ['WTF?', 'Switch Case Delimiter'],
            ['OMG', 'Case'],
            ['OMGWTF', 'Default'],
            ['OIC', 'Flow Control Delimiter'],
            # ----------------- increment and decrement statements -----------------
            ['UPPIN', 'Increment'],
            ['NERFIN', 'Decrement'],

            # ----------------- additional loop statements -----------------
            ['YR', 'Loop Identifier'],
            ['TIL', 'Until Loop'],
            ['WILE', 'While Loop'],

            #-------------------------------- function statements -----------------
            ['HOW IZ I', 'Function Definition'],
            ['IF U SAY SO', 'Function Delimiter'],
            ['GTFO', 'Function Return'],
            ['FOUND YR', 'Function Return Value'],
            ['I IZ', 'Function Call'],
            ['MKAY', 'End of Infinite Arity / Function Call']
    ]

    code = stripComments(code) # we will strip comments first before passing to getLexemes() function
    if code is None: # if there is an error while stripping code, return None
        return None # Return None since there's an error
        
    lines = code.split("\n") # we split the line into an array ; delimeter is new line

    if "HAI" == lines[0] and "KTHXBYE" == lines[-1]: # if HAI is in beginning and KTHXBYE at the end, that's when we do the rest
        lexical_table.append([[pl_element[0][0], pl_element[0][1]]]) # appends HAI

        for i in lines[1:-1]: # since we checked the start and the end already, we will iterate through first and last lines
            line_tokens = []
            whole_string = i.strip() # strip the string to remove new line
            #print(f"Processing line: {whole_string}") # DEBUG: print line being procesed

            while whole_string != "": # while the string is not empty
                matched = False # initial bool; match false
                #print(f"Remaining string to process: {whole_string}") # print the remaining string to process

                if whole_string.startswith('"'): # For YARN literals, if starts with quotation
                    closing = whole_string.find('"', 1) # starting from index 1, we find the partner end quotation
                    if closing != -1: # if we found a closing;
                        yarn = whole_string[1:closing]   # we take the value in between quotations
                        line_tokens.append(['"', "String Delimiter"]) # add the quotation literal to lexical table;
                        line_tokens.append([yarn, "YARN Literal"]) # add the YARN literal to lexical table;
                        line_tokens.append(['"', "String Delimiter"]) # add the closing quotation literal to lexical table;
                        whole_string = whole_string[closing + 1:].strip() # removes
                    else:
                        # print("Warning: unterminated string literal")
                        # whole_string = ""
                        return None # unterminated string error
                    matched = True

                if not matched: # if after going through yarn literal still not match, we check each item in pl_element
                    for j in pl_element:
                        #if whole_string.startswith(j[0]): # we use string comparison not regex
                        if re.match(re.escape(j[0]) + r'(?=\s|$)', whole_string): # regex match; keyword must end with whitespace or end of line
                            if j[0] in ['BTW', 'OBTW', 'TLDR']: # if the PL matched is a comment, we ignore it and continue
                                return None # at this point comments should have been stripped already, so if we encounter a comment here, it means there is an error in the code
                            line_tokens.append([j[0], j[1]]) # appends 
                            whole_string = whole_string[len(j[0]):].strip()

                            # immediately grab the identifier that follows I HAS A
                            if j[0] == 'I HAS A': # if the PL matched is I HAS A
                                parts = whole_string.split()  # we split the remaining parts (var name can't have space)
                                if parts: # the first is the var name (the one right after I HAS A)
                                    var_name = parts[0]
                                    if re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', var_name):
                                        for k in pl_element: # we check if the var_name is not a keyword
                                            if var_name == k[0]:
                                                return None # if it is a keyword, return None (error)
                                        line_tokens.append([var_name, "Variable Identifier"]) # then we add that to lexical table
                                        whole_string = whole_string[len(var_name):].strip()
                                    else:
                                        return None

                            matched = True # we find match
                            break

                if not matched: # if still not match, we look at initial
                    parts = whole_string.split(None, 1)
                    token = parts[0]
                    remaining  = parts[1].strip() if len(parts) > 1 else ""

                    if re.match(r'^-?[0-9]+$', token):           # number literal
                        line_tokens.append([token, "NUMBR Literal"])
                    elif re.match(r'^(WIN|FAIL)$', token):
                        line_tokens.append([token, "TROOF Literal"])
                    elif re.match(r'^-?[0-9]+\.[0-9]+$', token):
                        line_tokens.append([token, "NUMBAR Literal"])
                    elif re.match(r'^(TROOF|NOOB|NUMBR|NUMBAR|YARN)$', token): # types
                        line_tokens.append([token, "TYPE Literal"])
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token) and len(line_tokens) > 0 and line_tokens[-1][0] in ('HOW IZ I', 'I IZ'): # function name
                        line_tokens.append([token, "Function Identifier"])
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token) and len(line_tokens) > 0 and line_tokens[-1][0] in ('IM IN YR', 'IM OUTTA YR'): # loop label
                        line_tokens.append([token, "Loop Label"])
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token): # General variable identifier reference
                        line_tokens.append([token, "Variable Identifier"])
                    else:
                        return None # if no match, return None (error)

                    whole_string = remaining

            lexical_table.append(line_tokens)

        lexical_table.append([[pl_element[1][0], pl_element[1][1]]]) # appends KTHXBYE

    else: # else for initial if ; no HAI or no KTHXBYE (not at beginning or end) results in an error
        return None

    # ----- printing the lexical table --------------
    print("\n-----------Lexical Table----------")
    for line in lexical_table:
        for token in line:
            print(f"{token[0]:<10} | {token[1]}")
    print("----------------------------------")

    return lexical_table

getLexemes(code) # call the function to get lexemes for the example code

# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 1 - Lexemes 
