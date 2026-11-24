# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 1 - Lexemes

import re  # import regex

# GLOBAL VARIABLES: lexical error and row line numbers
lexical_error = ""  # init for lexical error; string that shows error message
row_line_numbers = []   # added: line number ng bawat row ng lexical table (para sa error messages ng syntax analyzer)

# ====================================================================================================================================
# FUNCTION FOR DEALING WITH COMMENTS:                                                                                                |
# comments are not considered statements and must be ignored; we will STRIP COMMENTS AWAY before passing to getLexemes() function    |
# returns a list of [line number, clean line] or None kapag may error                                                                |
# ====================================================================================================================================

def stripComments(code):
    global lexical_error
    clean_lines = [] # init empty list for clean lines
    obtw_tldr = False # flag tracker for obtw_tldr (comment block)
    line_number = 0 # added: para alam natin kung anong line yung may error

    code_lines = code.split("\n") # split the code into lines
    for line in code_lines:
        line_number = line_number + 1
        stripped_line = line.strip() # strip the line to remove leading/trailing whitespace

        if re.match(r'^OBTW(?:\s|$)', stripped_line): # if OBTW, we set the flag to TRUE and continue
            if obtw_tldr: # nested OBTW inside an already-open OBTW block is not allowed
                lexical_error = "Line " + str(line_number) + ": Nested OBTW is not allowed"
                return None
            if re.search(r'\bTLDR\b', stripped_line): # if TLDR and OBTW in same line, return None (error)
                lexical_error = "Line " + str(line_number) + ": OBTW and TLDR must be on separate lines"
                return None
            obtw_tldr = True
            continue

        elif obtw_tldr: # while inside OBTW ... TLDR comment block
            tldr_match = re.search(r'\bTLDR\b', stripped_line) # allow comment text before TLDR on closing line
            if tldr_match:
                after_tldr = stripped_line[tldr_match.end():].strip() # check if there is anything after TLDR
                if after_tldr and not re.match(r'^BTW(?:\s|$)', after_tldr): # statements after TLDR are not allowed
                    lexical_error = "Line " + str(line_number) + ": TLDR must be on its own line"
                    return None
                obtw_tldr = False
            continue # ignore everything inside OBTW and TLDR

        elif re.match(r'^TLDR(?:\s|$)', stripped_line): # TLDR encountered when obtw_tldr is False
            lexical_error = "Line " + str(line_number) + ": TLDR without a matching OBTW"
            return None

        # we use match iter because we find all instances of BTW
        for match in re.finditer(r'\bBTW\b', stripped_line):
            before = stripped_line[:match.start()] # find everything before btw
            # e.g. I HAS A VAR ITZ 5 BTW this is a comment
            # before = I HAS A VAR ITZ 5 (we remove btw and the rest)
            # if there are even numbers of quotes before (meaning closed quotes), then everything after BTW is a comment
            # if there are odd numbers of quotes before (only 1 quotation) there are two instances:
                # a) BTW is part of a string
                # b) Closed string (which would produce an error that we have catched)
            if before.count('"') % 2 == 0:
                stripped_line = before.strip()
                break

        # added: bawal yung OBTW na kasama ng ibang statement sa isang line
        for match in re.finditer(r'\bOBTW\b', stripped_line):
            before = stripped_line[:match.start()]
            if before.count('"') % 2 == 0: # nasa labas ng string yung OBTW
                lexical_error = "Line " + str(line_number) + ": OBTW must be on its own line"
                return None

        if stripped_line: # if the stripped line is not empty, we add it to the clean_lines list
            clean_lines.append([line_number, stripped_line]) # add the cleaned line to the list (kasama na yung line number)

    if obtw_tldr == True: # kapag TRUE parin siya even after, ibig sabihin hindi na close so error
        lexical_error = "Line " + str(line_number) + ": Unclosed comment block (OBTW without TLDR)"
        return None

    return clean_lines # added: list na yung binabalik para kasama yung line numbers
# ------------------------------------------------------------------------------------------------------------

# ====================================================================================================================================
# HELPER FUNCTION FOR SOFT BREAK COMMANDS:                                                                                           |
# soft break commands are commas (,) that separate statements within the same line                                                   |
# returns a list of [line number, clean line] or None kapag may error                                                                |
# ====================================================================================================================================
# format of clean_lines: [[line_number, clean_line], [line_number, clean_line], ...]

def splitStatements(clean_lines): # input in splitStatements is the output of stripComments() function
    statements = []
    for item in clean_lines:
        line_number = item[0]
        line = item[1]
        in_string = False # flag kung nasa loob tayo ng "..."
        piece = ""
        for char in line:
            if char == '"':
                in_string = not in_string
            if char == ',' and in_string == False: # comma sa labas ng string = bagong statement
                if piece.strip() != "":
                    statements.append([line_number, piece.strip()])
                piece = ""
            else:
                piece = piece + char
        if piece.strip() != "":
            statements.append([line_number, piece.strip()])

    return statements
# ------------------------------------------------------------------------------------------------------------

# ====================================================================================================================================
# ACTUAL CODE TO GET LEXEMES:                                                                                                        |
# ====================================================================================================================================
def getLexemes(code): # function for getting lexemes
    global lexical_error, row_line_numbers
    lexical_error = ""
    row_line_numbers = []
    lexical_table = [] # init for lexical table (one token list per source line)
    type_literals = ["WIN", "FAIL", "TROOF", "NOOB", "NUMBR", "NUMBAR", "YARN"] # added: list of type literals
    pl_element = [ # PL elements, regex, and classification
            #  ---------------- code delimiters ------------------------------
            ['HAI', "Code Delimiter"], # format is [TABLENAME, CLASSIFICATION]
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

    clean_lines = stripComments(code) # we will strip comments first before passing to getLexemes() function
    if clean_lines is None: # if there is an error while stripping code, return None
        return None # Return None since there's an error

    lines = splitStatements(clean_lines) # for bonus! line continuation and soft command breaks

    if len(lines) == 0: # walang laman yung program
        lexical_error = "The program is empty"
        return None

    #hindi na natin chinecheck dito kung HAI yung una at KTHXBYE yung huli, kasi allowed ang funcs before hai and kthnx bye
    # kasi pwedeng may functions bago mag HAI at pagkatapos ng KTHXBYE, kaya sa syntax analyzer na yun chinecheck
    for item in lines:
        line_number = item[0]
        line_tokens = []
        whole_string = item[1].strip() # strip the string to remove new line

        while whole_string != "": # while the string is not empty
            matched = False # initial bool; match false

            if whole_string.startswith('"'): # For YARN literals, if starts with quotation
                closing = whole_string.find('"', 1) # starting from index 1, we find the partner end quotation
                if closing != -1: # if we found a closing;
                    yarn = whole_string[1:closing]   # we take the value in between quotations
                    line_tokens.append(['"', "String Delimiter"]) # add the quotation literal to lexical table;
                    line_tokens.append([yarn, "YARN Literal"]) # add the YARN literal to lexical table;
                    line_tokens.append(['"', "String Delimiter"]) # add the closing quotation literal to lexical table;
                    whole_string = whole_string[closing + 1:].strip() # removes
                else:
                    lexical_error = "Line " + str(line_number) + ": unterminated string literal"
                    return None # unterminated string error
                matched = True
            elif whole_string.startswith("+"): # For YARN literals, if starts with + (concatenation)
                line_tokens.append(["+", "Concatenation Operator"]) # add the + operator to lexical table;
                whole_string = whole_string[1:].strip() # removes
                matched = True

            if not matched: # if after going through yarn literal still not match, we check each item in pl_element
                for j in pl_element:
                    if re.match(re.escape(j[0]) + r'(?=\s|\+|$)', whole_string): # regex match; keyword must end with whitespace or end of line
                        if j[0] in ['BTW', 'OBTW', 'TLDR']: # if the PL matched is a comment, we ignore it and continue
                            # at this point comments should have been stripped already, so if we encounter a comment here, it means there is an error in the code
                            lexical_error = "Line " + str(line_number) + ": " + j[0] + " must be on its own line"
                            return None
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
                                            lexical_error = "Line " + str(line_number) + ": keyword " + var_name + " cannot be a variable name"
                                            return None # if it is a keyword, return None (error)
                                    for k in type_literals: # we check if the var_name is not a type literal
                                        if var_name == k:
                                            lexical_error = "Line " + str(line_number) + ": type literal " + var_name + " cannot be a variable name"
                                            return None # if it is a type literal, return None (error)
                                    line_tokens.append([var_name, "Variable Identifier"]) # then we add that to lexical table
                                    whole_string = whole_string[len(var_name):].strip()
                                else:
                                    lexical_error = "Line " + str(line_number) + ": invalid variable name " + var_name
                                    return None

                        matched = True # we find match
                        break

            if not matched: # if still not match, we look at initial
                parts = whole_string.split(None, 1)
                token = parts[0]
                remaining  = parts[1].strip() if len(parts) > 1 else ""

                if "+" in token:
                    plus_pos = token.find("+")
                    remaining = whole_string[plus_pos:].strip()
                    token = token[:plus_pos]

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
                    lexical_error = "Line " + str(line_number) + ": invalid token " + token
                    return None # if no match, return None (error)

                whole_string = remaining

        lexical_table.append(line_tokens)
        row_line_numbers.append(line_number) # added: tandaan yung line number ng row na to
    #printLexicalTable(lexical_table) # helper function to print the lexical table in a readable format
    return lexical_table


def printLexicalTable(lexical_table): # helper function to print the lexical table in a readable format
    # ONLY FOR DBEUGGING IN TERMINAL; NOT USED IN GUI
    if lexical_table is None:
        print("No lexical table to print.")
        return
    print("\n-----------Lexical Table----------")
    for line in lexical_table:
        for token in line:
            print(f"{token[0]:<10} | {token[1]}")
    print("----------------------------------")