# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 1 - Lexemes 

import re # import regex

# ------------- example code -----------
code = """HAI
I HAS A var ITZ 5
VISIBLE var
KTHXBYE"""

# ------------- example code 2 ---------
code2 = """HAI
I HAS A var ITZ 12
VISIBLE "noot noot" var
KTHXBYE"""

def getLexemes(code): # functions for getting lexemes
    lexical_table = [] # blank lexical table
    symbol_table = [] # blank symbol table (future implementation)

    pl_element = [ # some PL elements (only for base testing, most of these are the basics)
        ['HAI', r'^HAI$', "Code Delimiter"], # format is [TABLENAME, REGEX, CLASSIFICATION]
        ['KTHXBYE', r'^KTHXBYE$', "Code Delimiter"],
        ['I HAS A', r'^I HAS A$', "Variable Declaration"],
        ['ITZ', r'^ITZ$', "Variable Assignment"],
        ['VISIBLE', r'^VISIBLE$', "Output Keyword"]
    ]

    lines = code.split("\n") # we split the line into an array ; delimeter is new line

    if "HAI" == lines[0] and "KTHXBYE" == lines[-1]: # if HAI is in beginning and KTHXBYE at the end, that's when we do the rest
        lexical_table.append([pl_element[0][0], pl_element[0][2]]) # appends HAI

        for i in lines[1:-1]: # since we checked the start and the end already, we will iterate through first and last lines
            whole_string = i.strip() # strip the string to remove new line

            while whole_string != "": # while the string is not empty
                matched = False # initial bool; match false

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
                            lexical_table.append([j[0], j[2]]) # appends 
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
                        lexical_table.append([token, "NUMBR Literal"])
                    elif re.match(r'^(WIN|FAIL)$', token):
                        lexical_table.append([token, "TROOF Literal"])
                    elif re.match(r'^-?[0-9]+\.[0-9]+$', token):
                        lexical_table.append([token, "NUMBAR Literal"])
                    # (YARN strings are handled before this block — no branch needed here)
                    elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', token):  # varident
                        lexical_table.append([token, "Variable Identifier"])
                    elif re.match(r'^(TROOF|NOOB|NUMBR|NUMBAR|YARN)$', token):
                        lexical_table.append([token, "TYPE"])            
                    else:
                        print(f"Warning: unrecognized token '{token}'")

                    whole_string = remaining

        lexical_table.append([pl_element[1][0], pl_element[1][2]]) # appends KTHXBYE

    else: # else for initial if ; no HAI or no KTHXBYE (not at beginning or end) results in an error
        return None

    # ----- printing the lexical table --------------
    print("\n-----------Lexical Table----------")
    for line in lexical_table:
        print(f"{line[0]:<10} | {line[1]}")
    print("----------------------------------")
    print(lexical_table)
    return lexical_table
