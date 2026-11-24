# Sources:
# https://docs.python.org/3/library/tkinter.html
# https://docs.python.org/3/library/tkinter.ttk.html
# https://docs.python.org/3/library/dialog.html
# https://github.com/amtuazon4/PyGUI/blob/main/source%20code/main.py
# Project Requirement # 4 - User Interface
#
# GUI Parts (based sa project specs):
# 1) File Explorer
# 2) Text Editor   
# 3) List of Tokens
# 4) Symbol Table    
# 5) Execute Button                    
# 6) Console

import lexical_analyzer
import semantics
from lexical_analyzer import getLexemes
from semantics import runProgram
from syntax_analyzer import parseProgram

# ====================================================================================================================================
# FUNCTION FOR INTERPRETING LOLCODE:                                                                                                 |
# runs all three phases in order: 1) lexical analysis, 2) syntax analysis, 3) semantic analysis                                      |
# returns [tokens, symbol_table, output, error_message]                                                                              |
# ====================================================================================================================================

def interpret(code):
    # 1) lexical analysis: turn raw text into [lexeme, classification] rows
    tokens = getLexemes(code) # extracts lexemes and classification from source code
    if tokens is None: # if None meaning there's lexical error, returns empty tokens, empty symbol table, empty output, and the lexical error message
        return [], [], "", "Lexical Error: " + lexical_analyzer.lexical_error

    # 2) syntax analysis: check grammar and build the syntax tree
    tree, message = parseProgram(tokens) # parse the tokens, builds syntax tree, and returns the tree and any syntax error message
    if tree is None: 
        return tokens, [], "", "Syntax Error: " + message

    # 3) semantic analysis: execute the syntax tree and collect output/variables
    try: # catch RecursionError in case the program has infinite recursion (e.g., recursive function calls without a base case)
        success, message = runProgram(tree)
    except RecursionError:
        output = "".join(semantics.console_output)
        return tokens, semantics.symbol_table, output, "Semantic Error: maximum recursion depth exceeded"

    output = "".join(semantics.console_output)
    if not success:
        return tokens, semantics.symbol_table, output, "Semantic Error: " + message
    # intrepret[0] - tokens for lexeme table, interpret[1] - symbol table, interpret[2] - output for console, interpret[3] - error message
    return tokens, semantics.symbol_table, output, ""

# ====================================================================================================================================
# HELPER FUNCTION FOR UPDATING LINE NUMBERS (VS CODE STYLE):                                                                         |
# counts how many lines are inside the text editor and updates the line-number gutter on the left                                    |
# ====================================================================================================================================

def updateLineNumbers(editor, line_numbers): # has two parameters, text editor and line number gutter (vertical strip along the left edge of the editing area)
    total_lines = int(editor.index("end-1c").split(".")[0]) # get the total number of lines in the editor
    numbers_text = ""
    for num in range(1, total_lines + 1):
        numbers_text = numbers_text + str(num) + "\n"

    line_numbers.config(state="normal") # temporarily unlock gutter so we can edit it
    line_numbers.delete("1.0", "end") # clear old line numbers
    line_numbers.insert("1.0", numbers_text.rstrip("\n")) # insert updated line numbers (1, 2, 3, ...)
    line_numbers.config(state="disabled") # lock gutter again so user cannot type in it
    line_numbers.yview_moveto(editor.yview()[0]) # keep scroll position aligned with editor

# ====================================================================================================================================
# HELPER FUNCTION FOR POPULATING LEXEMES AND SYMBOL TABLE:                                                                           |
# clears previous rows and inserts the latest tokens and symbol table entries (Identifier & Value) into the GUI tables               |
# ====================================================================================================================================

def populateTables(token_list, symbol_list, tokens, table):
    token_list.delete(*token_list.get_children())   # clear old tokens
    symbol_list.delete(*symbol_list.get_children()) # clear old symbol table rows

    for row in tokens:
        for lexeme, classification in row:
            token_list.insert("", "end", values=(lexeme, classification))

    for identifier, value, _ in table: # only show Identifier and Value columns
        symbol_list.insert("", "end", values=(identifier, semantics.displayValue(value)))

# ====================================================================================================================================
# FUNCTION FOR LAUNCHING THE TKINTER GUI:                                                                                            |
# creates a fixed-size dark mode desktop window with File Explorer, Code Editor, Lexemes, Symbol Table, Execute Button, and Console  |
# ====================================================================================================================================

def main():
    import tkinter as tk  # import for tkinter
    from tkinter import (  # filedialog is for explorer, simpledialog is for input, ttk is for tables
        filedialog,  # file explorer dialog box for opening files
        simpledialog,  # pop up dialog box for GIMMEH input
        ttk,  # provides modern GUI widgets in tkinter
    )

    # tkinter initialization and window setup
    window = tk.Tk() # init tkinter
    window.title("LOLCODE Interpreter") # title
    window.geometry("1000x620") # fixed window size so it does not take up the entire screen
    window.resizable(False, False) # lock window to the set resolution
    window.configure(bg="#1E1E1E") # dark mode background color (RGB hex #1E1E1E is very dark gray)

    # load lolcode-icon.png as the window icon
    icon_image = tk.PhotoImage(file="lolcode-icon.png")
    window.iconphoto(True, icon_image) # set the window icon to the lolcode-icon.png image
    window.icon_image = icon_image # keep a reference so Python does not clear the image from memory

    # apply Arial font and dark mode colors to Treeview tables
    style = ttk.Style()
    style.theme_use("clam")
    style.configure( # Treeview is a multicolumn table widget 
        "Treeview", # specify the style for the Treeview widget
        font=("Arial", 9),
        rowheight=20,
        background="#252526" ,
        fieldbackground="#252526" ,
        foreground="#E5E7EB" ,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading", # specify the style for the Treeview heading
        font=("Arial", 9, "bold"),
        background="#333337",
        foreground="#E5E7EB" ,
    )
    style.configure(
        "Blue.TButton", # cross-platform blue button style (works on both macOS and Windows with clam theme)
        font=("Arial", 9, "bold"),
        background="#2563EB",
        foreground="#FFFFFF",
        borderwidth=0,
        focusthickness=0,
        focuscolor="#2563EB",
        relief="flat",
    )
    style.map(
        "Blue.TButton",
        background=[("pressed", "#1E40AF"), ("active", "#1D4ED8")],
        foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")],
    )
    style.configure(
        "Red.TButton", # style for the STOP / reset button
        font=("Arial", 9, "bold"),
        background="#DC2626",
        foreground="#FFFFFF",
        borderwidth=0,
        focusthickness=0,
        focuscolor="#DC2626",
        relief="flat",
    )
    style.map(
        "Red.TButton",
        background=[("pressed", "#991B1B"), ("active", "#B91C1C")],
        foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")],
    )

    # ---------------- file explorer bar ----------------
    top_frame = tk.Frame(window, bg="#1E1E1E")
    top_frame.pack(fill="x", padx=12, pady=(10, 4))

    file_label = tk.Label(top_frame, text="No file selected", font=("Arial", 9), bg="#1E1E1E", fg="#9CA3AF" ) # label to show current file path 

    # helper function to open a file dialog and load the selected .lol file into the editor
    def openFile():
        filename = filedialog.askopenfilename(filetypes=[("LOLCODE files", "*.lol")]) # only allows opening .lol files, not other file types
        if filename: # if there is a valid path returned
            try: # opens file 
                with open(filename, "r", encoding="utf-8") as file: 
                    file_content = file.read()
            except OSError as e: # except if there is an error opening the file
                writeConsole("File Error: " + str(e) + "\n", "error") # writes to console about file error
                return # return

            file_label.config(text=filename) # updates label
            editor.delete("1.0", "end") # clears the editor before inserting new content
            editor.insert("1.0", file_content) # inserts the content of the file into the editor
            updateLineNumbers(editor, line_numbers) # refresh line numbers after loading file

    open_btn = ttk.Button( # creates new button for open file
        top_frame,
        text="Open File",
        style="Blue.TButton",
        padding=(12, 4),
        cursor="hand2",
        command=openFile
    )
    open_btn.pack(side="left", padx=(0, 10)) # places the button on the left side of the top frame with some padding to the right
    file_label.pack(side="left") # places the label next to the button on the left side of the top frame

    # ---------------- editor, lexeme table, and symbol table ----------------
    middle_frame = tk.Frame(window, bg="#1E1E1E")
    middle_frame.pack(fill="both", expand=True, padx=12, pady=4)
    middle_frame.columnconfigure(0, weight=5, uniform="panel") # code editor
    middle_frame.columnconfigure(1, weight=4, uniform="panel") # lexemes table
    middle_frame.columnconfigure(2, weight=3, uniform="panel") # symbol table
    middle_frame.rowconfigure(0, weight=1)

    # ---------------- text editor (with line numbers) ----------------
    editor_section = tk.Frame(middle_frame, bg="#1E1E1E") # new frame for the code editor section, with dark mode background color, placed in middle_frame
    editor_section.grid(row=0, column=0, sticky="nsew", padx=(0, 6)) # placed in the first column of middle_frame, with padding to the right
    # nsew means frame will expand in all directions to fill space on grid

    tk.Label(editor_section, text="Code Editor", font=("Arial", 9, "bold"), bg="#1E1E1E", fg="#E5E7EB" ).pack(anchor="w", pady=(0, 4)) # label (similar to above)

    editor_box = tk.Frame(editor_section, bg="#252526" , highlightbackground="#3E3E42" , highlightthickness=1) # adds a border around editor
    editor_box.pack(fill="both", expand=True)

    # line number gutter on the left (disabled text box synced with editor)
    line_numbers = tk.Text(
        editor_box,
        width=4,
        height=1,
        font=("Arial", 9),
        bg="#2D2D30",
        fg="#9CA3AF" ,
        bd=0,
        padx=5,
        pady=6,
        state="disabled",
        takefocus=0,
        wrap="none"
    )
    line_numbers.pack(side="left", fill="y")

    editor_scroll = tk.Scrollbar(editor_box, orient="vertical") # scrollbar for the editor, placed on the right side of the editor_box
    editor_scroll.pack(side="right", fill="y")

    editor = tk.Text( # the main text editor where users can write LOLCODE, placed in the editor_box
        editor_box,
        height=1,
        font=("Arial", 9),
        bg="#252526" ,
        fg="#E5E7EB" ,
        insertbackground="#FFFFFF" , # white typing cursor so it is clearly visible in dark mode
        selectbackground="#264F78" ,
        bd=0,
        padx=8,
        pady=6,
        undo=True,
        wrap="none" # keep wrap off so line numbers always match editor lines 1-to-1
    )
    editor.pack(side="left", fill="both", expand=True)

    # ---------------- UPDATING & SYNCING LINE NUMBERS ON THE UI ----------------
    # whenever the editor scrolls (mouse wheel, arrow keys, or dragging the scrollbar),
    # Tkinter automatically calls onEditorScroll with the top (first) and bottom (last) scroll positions
    def onEditorScroll(first, last):
        editor_scroll.set(first, last)   # update the scrollbar thumb position
        line_numbers.yview_moveto(first) # move the line-number gutter to match the editor

    editor.config(yscrollcommand=onEditorScroll) # connect editor scrolling to onEditorScroll
    editor_scroll.config(command=editor.yview)   # dragging the scrollbar scrolls the editor (which triggers onEditorScroll)

    # Tkinter automatically passes an "event" object (info about the key/mouse action) to bound functions,
    # even though we don't need to use "event" inside refreshLines
    def refreshLines(event):
        window.after_idle(updateLineNumbers, editor, line_numbers)

    # editor.bind() connects user actions inside the editor specifically to update the line numbers on the UI:
    editor.bind("<KeyRelease>", refreshLines)      # update line numbers after typing or pressing Enter/Backspace
    editor.bind("<ButtonRelease-1>", refreshLines) # update line numbers after clicking inside the editor
    editor.bind("<MouseWheel>", refreshLines)      # update line numbers after scrolling with the mouse wheel
    editor.bind("<<Paste>>", refreshLines)         # update line numbers after pasting code
    updateLineNumbers(editor, line_numbers)        # show line "1" immediately at startup

    # helper to lock column widths so user cannot drag column dividers
    def blockColumnResize(event):
        if event.widget.identify_region(event.x, event.y) == "separator":
            return "break"

    # ---------------- lexeme table ----------------
    token_section = tk.Frame(middle_frame, bg="#1E1E1E")
    token_section.grid(row=0, column=1, sticky="nsew", padx=6)

    tk.Label(token_section, text="Lexemes", font=("Arial", 9, "bold"), bg="#1E1E1E", fg="#E5E7EB" ).pack(anchor="w", pady=(0, 4))

    token_box = tk.Frame(token_section, bg="#252526" , highlightbackground="#3E3E42" , highlightthickness=1)
    token_box.pack(fill="both", expand=True)

    token_scroll = tk.Scrollbar(token_box, orient="vertical")
    token_scroll.pack(side="right", fill="y")

    token_list = ttk.Treeview(token_box, columns=("lexeme", "classification"), show="headings", height=1, yscrollcommand=token_scroll.set)
    token_list.heading("lexeme", text="Lexeme")
    token_list.heading("classification", text="Classification")
    token_list.column("lexeme", width=110, stretch=False)
    token_list.column("classification", width=188, stretch=False)
    token_list.bind("<Button-1>", blockColumnResize) # lock column widths
    token_list.pack(side="left", fill="both", expand=True)
    token_scroll.config(command=token_list.yview)

    # ---------------- smybol table ----------------
    symbol_section = tk.Frame(middle_frame, bg="#1E1E1E")
    symbol_section.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

    tk.Label(symbol_section, text="Symbol Table", font=("Arial", 9, "bold"), bg="#1E1E1E", fg="#E5E7EB" ).pack(anchor="w", pady=(0, 4))

    symbol_box = tk.Frame(symbol_section, bg="#252526" , highlightbackground="#3E3E42" , highlightthickness=1)
    symbol_box.pack(fill="both", expand=True)

    symbol_scroll = tk.Scrollbar(symbol_box, orient="vertical")
    symbol_scroll.pack(side="right", fill="y")

    symbol_list = ttk.Treeview(symbol_box, columns=("identifier", "value"), show="headings", height=1, yscrollcommand=symbol_scroll.set)
    symbol_list.heading("identifier", text="Identifier")
    symbol_list.heading("value", text="Value")
    symbol_list.column("identifier", width=109, stretch=False)
    symbol_list.column("value", width=110, stretch=False)
    symbol_list.bind("<Button-1>", blockColumnResize) # lock column widths
    symbol_list.pack(side="left", fill="both", expand=True)
    symbol_scroll.config(command=symbol_list.yview)

    # ---------------- execute button ----------------
    btn_frame = tk.Frame(window, bg="#1E1E1E")
    btn_frame.pack(fill="x", padx=12, pady=(6, 4))

    # ---------------- console ----------------
    # take note that console only displays, cannot type in console.
    console_section = tk.Frame(window, bg="#1E1E1E", height=265)
    console_section.pack_propagate(False) # prevents the console section from shrinking to fit its contents, so it maintains a fixed height of 265 pixels
    console_section.pack(fill="x", padx=12, pady=(2, 12))

    tk.Label(console_section, text="Console Output", font=("Arial", 9, "bold"), bg="#1E1E1E", fg="#E5E7EB" ).pack(anchor="w", pady=(0, 4))

    console_box = tk.Frame(console_section, bg="#252526" , highlightbackground="#3E3E42" , highlightthickness=1)
    console_box.pack(fill="both", expand=True)

    console_scroll = tk.Scrollbar(console_box, orient="vertical")
    console_scroll.pack(side="right", fill="y")

    console = tk.Text( 
        console_box,
        font=("Arial", 9),
        bg="#252526" ,
        fg="#E5E7EB" ,
        bd=0,
        padx=8,
        pady=6,
        state="disabled",
        yscrollcommand=console_scroll.set
    )
    console.pack(side="left", fill="both", expand=True)
    console_scroll.config(command=console.yview)

    # configure red text tag for lexical, syntax, and semantic errors
    console.tag_config("error", foreground="#F87171" , font=("Arial", 9, "bold")) # if tag is error, text will be red and bold

    def writeConsole(text, tag=None): # helper function to write text to the console, with optional tag for styling (e.g., red for errors)
        console.config(state="normal")
        if tag is not None:
            console.insert("end", text, tag)
        else:
            console.insert("end", text)
        console.see("end")
        console.config(state="disabled")
        window.update()

    def printToConsole(text): # tinatawag ng semantics tuwing may VISIBLE
        writeConsole(text)

    def askInput(var_name): # GIMMEH -> popup dialog box
        value = simpledialog.askstring("GIMMEH", "Enter value for " + var_name + ":", parent=window) # when GIMMEH is called, dialog box appears
        if value is None: # if nothing inputted, return empty string
            value = ""
        writeConsole(value + "\n") # show user input in the console
        return value

    def resetProgram(): # stops any running loop and resets tables, console, and runtime state
        semantics.stop_requested = True
        semantics.symbol_table = [["IT", None, "NOOB"]]
        semantics.console_output = []
        if window.winfo_exists(): # only clear widgets if the window has not been closed
            token_list.delete(*token_list.get_children())
            symbol_list.delete(*symbol_list.get_children())
            console.config(state="normal")
            console.delete("1.0", "end")
            console.config(state="disabled")

    def onClose(): # stop any running loop cleanly before closing the window
        semantics.stop_requested = True
        window.destroy()

    def execute():
        # clear previous console output before running
        console.config(state="normal")
        console.delete("1.0", "end")
        console.config(state="disabled")

        semantics.output_function = printToConsole # sets the output function in semantics.py to printToConsole, so that any VISIBLE statements will write to the console
        semantics.input_function = askInput # sets input function to askInput
        semantics.check_events = window.update # keeps GUI responsive during loops so STOP can be clicked

        source_code = editor.get("1.0", "end-1c")
        tokens, table, _, error_message = interpret(source_code)

        if semantics.stop_requested: # if STOP was clicked mid-execution, leave program state reset
            resetProgram()
            return

        populateTables(token_list, symbol_list, tokens, table)

        if error_message:
            # display lexical, syntax, or semantic errors in red
            writeConsole(error_message + "\n", "error")

    # stop running loops cleanly if the user closes the window
    window.protocol("WM_DELETE_WINDOW", onClose)

    # place Execute and Stop buttons on the bottom-left under the Code Editor
    execute_btn = ttk.Button(
        btn_frame,
        text="EXECUTE",
        style="Blue.TButton",
        padding=(20, 5),
        cursor="hand2",
        command=execute
    )
    execute_btn.pack(side="left")

    stop_btn = ttk.Button(
        btn_frame,
        text="STOP",
        style="Red.TButton",
        padding=(20, 5),
        cursor="hand2",
        command=resetProgram
    )
    stop_btn.pack(side="left", padx=(8, 0))
    window.mainloop()
# ------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
