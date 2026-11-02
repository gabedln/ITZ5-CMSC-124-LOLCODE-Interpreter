# Sources:
# https://github.com/christianrfg/lexical-analyzer/blob/master/LexicalAnalyzer.py
# https://github.com/amtuazon4/PyGUI
# https://regex101.com/
# Project Requirement # 1 - Lexemes


## ASSUMPTIONS AND FORMATTING!!!! (wag nyo delete to pls)
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



import re # import regex

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
code2 = """HAI
    I HAS A var ITZ 12
    VISIBLE "noot noot" var
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

# -------- FUNCTION FOR DEALING WITH COMMENTS -------------------------------
# nakalagay sa docs na COMMENT ARE NOT CONSIDERED STATEMENTS, and must be ignored... so we will strip comments away
def stripComments(source):
    clean_lines = [] # init empty list
    obtw_tldr = False # track if we are in a comment block (OBTW...TLDR) 

    code_lines = source.split("\n") # split source into lines 
    for line in code_lines: # for each line 
        stripped_line = line.strip() # strip whitespace 

        if stripped_line == "OBTW": 
            obtw_tldr = True
            continue

        if stripped_line == "TLDR":
            obtw_tldr = False
            continue

        if obtw_tldr:
            continue
        match = re.search(r'BTW', line)
        if match:
            line = line[:match.start()]
        clean_lines.append(line.strip())
    
    if obtw_tldr == True:
        return "Syntax error: Unclosed comment block"
    return "\n".join(clean_lines)

def getLexemes(code): # function for getting lexemes
    lexical_table = [] # init for lexical table (blank)
    symbol_table = [] # for symbol table (future implementation)

    pl_element = [ # PL elements, regex, and classification
            #  ---------------- code delimiters ------------------------------
            ['HAI', r'^HAI$', "Code Delimiter"], # format is [TABLENAME, REGEX, CLASSIFICATION]
            ['KTHXBYE', r'^KTHXBYE$', "Code Delimiter"],

            #------------------- variable declarations -----------------------
            ['WAZZUP', r'^WAZZUP$', "Variable Declaration Delimeter"],
            ['BUHBYE', r'^BUHBYE$', "Variable Declaration Delimeter"],
            ['BTW', r'^BTW$', "Comment Delimiter"],
            ['OBTW', r'^OBTW$', "Comment Delimiter"],
            ['TLDR', r'^TLDR$', "Comment Delimiter"],
            ['I HAS A', r'^I HAS A$', "Variable Declaration"],
            ['ITZ', r'^ITZ$', "Variable Assignment"],
            ['R', r'^R$', "Variable Assignment"],

            # ---------- arithmetic operations -----------------------------
            ['SUM OF', r'^SUM OF$', "Addition Operation"],
            ['DIFF OF', r'^DIFF OF$', "Subtraction Operation"],
            ['PRODUKT OF', r'^PRODUKT OF$', "Multiplication Operation"],
            ['QUOSHUNT OF', r'^QUOSHUNT OF$', "Division Operation"],
            ['MOD OF', r'^MOD OF$', "Modulo Operation"],

            # ------------- boolean operations --------------------
            ['BOTH OF', r'^BOTH OF$', "AND Operation"],
            ['EITHER OF', r'^EITHER OF$', "OR Operation"],
            ['WON OF', r'^WON OF$', 'XOR Operation'],
            ['NOT', r'^NOT$', "NOT Operation"],
            ['ANY OF', r'^ANY OF$', 'Infinite OR Operation'],
            ['ALL OF', r'^ALL OF$', 'Infinite AND Operation'],

            # --------------- comparison operations -----------------
            ['BOTH SAEM', r'^BOTH SAEM$', 'Equality Operation'],
            ['DIFFRINT', r'^DIFFRINT$', 'Inequality Operation'],
            ['BIGGR OF', r'^BIGGR OF$', "Max Operation"],
            ['SMALLR OF', r'^SMALLR OF$', "Min Operation"],

            # ---------------- string concatenation ------------------
            ['SMOOSH', r'^SMOOSH$','String Concatenation'],

            # ----------------- type casting ------------------------
            ['MAEK', r'^MAEK$','Type Casting'],
            ['A', r'^A$','Type Casting Qualifier'],
            ['IS NOW A', r'^IS NOW A$','Type Casting Operation'],

            # ------------------ input and output (print() and input()) ----------
            ['VISIBLE',r'^VISIBLE$', 'Output Keyword'],
            ['GIMMEH', r'^GIMMEH$', 'Input Keyword'],

            # ------------------ flow-control statements -----------------
            ['O RLY?', r'^O RLY$','Conditional Statement Delimiter'],
            ['YA RLY', r'^YA RLY$', 'If'],
            ['MEBBE', r'^MEBBE$', 'Else If'],
            ['OIC', r'^OIC$', 'End of If-Else Block'],
            ['NO WAI', r'^NO WAI$','Else'],

            # ------------------ loop statements -----------------
            ['IM IN YR', r'^IM IN YR$', 'Loop Keyword'], 
            ['IM OUTTA YR', r'^IM OUTTA YR$', 'End of Loop Block']

            # ----------------- mamaya na muna to iimplement, unahin muna hanggang loop
            # ['UPPIN', r'^UPPIN$','Increment'],
            # ['NERFIN', r'^NERFIN$','Decrement'],
            # ['YR', r'^YR$','Loop Identifier'],
            # ['TIL', r'^TIL$','Until Loop'],
            # ['WILE', r'^WILE$','While Loop'],
            # ['HOW IZ I', r'^HOW IZ I$', 'Function Definition'],
            # ['IF U SAY SO', r'^IF U SAY SO$', 'Function Delimiter'],
            # ['GTFO', r'^GTFO$', 'Function Return'],
            # ['FOUND YR', r'^FOUND YR$', 'Function Return Value'],
            # ['I IZ', r'^I IZ$', 'Function Return Value'],
            # ['MKAY', r'^MKAY$', 'End of Code Delimiter']
    ]


print(stripComments(code))
