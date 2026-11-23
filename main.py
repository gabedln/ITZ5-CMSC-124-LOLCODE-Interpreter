# Project Requirement # 4 - User Interface (temporary :) feel free to input yours)
# GUI parts (based sa project specs): 1) File Explorer  2) Text Editor  3) List of Tokens  4) Symbol Table  5) Execute button  6) Console
# How to run:
# python main.py
# python main.py file.lol

# references: 
# https://docs.python.org/3/library/tkinter.html
# https://docs.python.org/3/library/tkinter.ttk.html
# https://docs.python.org/3/library/dialog.html
# https://github.com/amtuazon4/PyGUI/blob/main/source%20code/main.py

import sys

import lexical_analyzer
import syntax_analyzer
import semantics
from lexical_analyzer import getLexemes
from syntax_analyzer import parseProgram
from semantics import runProgram


#returns [tokens, symbol table, output, error message]
def interpret(code):
    #lexical analysis
    tokens = getLexemes(code)
    if tokens is None:
        return [], [], "", "Lexical Error: " + lexical_analyzer.lexical_error

    #syntax analysis
    tree, message = parseProgram(tokens)
    if tree is None:
        return tokens, [], "", "Syntax Error: " + message

    #semantic analysis
    success, message = runProgram(tree)
    output = "".join(semantics.console_output)
    if not success:
        return tokens, semantics.symbol_table, output, "Semantic Error: " + message
    return tokens, semantics.symbol_table, output, ""

#terminal
def runInTerminal(filename):
    try:
        code = open(filename, encoding="utf-8").read()
    except OSError as e:
        print("Error reading file:", e)
        return

    semantics.output_function = None
    semantics.input_function = input
    tokens, table, output, error_message = interpret(code)

    print("LEXEMES")
    for row in tokens:
        for lexeme, classification in row:
            print(f"{lexeme:<25} {classification}")

    print("\nSYMBOL TABLE")
    for identifier, value, data_type in table:
        print(f"{identifier:<20} {semantics.displayValue(value):<20} {data_type}")

    print("\nOUTPUT")
    print(output, end="")
    if error_message:
        print(error_message)


#GUI tktinker
def runGUI():
    import tkinter as tk
    from tkinter import ttk, filedialog, simpledialog

    window = tk.Tk()
    window.title("ITZ5 LOLCODE Interpreter")
    window.geometry("1100x700")

    #File Explorer
    top = tk.Frame(window)
    top.pack(fill="x")
    file_label = tk.Label(top, text="(None)")

    def openFile():
        filename = filedialog.askopenfilename(filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")])
        if filename:
            file_label.config(text=filename)
            editor.delete("1.0", "end")
            editor.insert("1.0", open(filename, encoding="utf-8").read())

    tk.Button(top, text="Open File", command=openFile).pack(side="left")
    file_label.pack(side="left")

    middle = tk.Frame(window)
    middle.pack(fill="both", expand=True)

    #Text Editor
    editor = tk.Text(middle, width=50, undo=True)
    editor.pack(side="left", fill="both", expand=True)

    #List of Tokens
    token_list = ttk.Treeview(middle, columns=("lexeme", "classification"), show="headings")
    token_list.heading("lexeme", text="Lexeme")
    token_list.heading("classification", text="Classification")
    token_list.pack(side="left", fill="both", expand=True)

    #Symbol Table
    symbol_list = ttk.Treeview(middle, columns=("identifier", "value", "type"), show="headings")
    symbol_list.heading("identifier", text="Identifier")
    symbol_list.heading("value", text="Value")
    symbol_list.heading("type", text="Type")
    symbol_list.pack(side="left", fill="both", expand=True)

    #Console
    console = tk.Text(window, height=12)

    def printToConsole(text):  # tinatawag ng semantics tuwing may VISIBLE
        console.insert("end", text)
        console.see("end")
        window.update()

    def askInput(var_name):  # GIMMEH -> dialog box
        value = simpledialog.askstring("GIMMEH", f"Enter value for {var_name}:", parent=window)
        if value is None:
            value = ""
        console.insert("end", value + "\n")  #show yung input sa console
        return value

    #Execute button
    def execute():
        console.delete("1.0", "end")
        token_list.delete(*token_list.get_children())
        symbol_list.delete(*symbol_list.get_children())

        semantics.output_function = printToConsole
        semantics.input_function = askInput
        tokens, table, output, error_message = interpret(editor.get("1.0", "end"))

        for row in tokens:
            for lexeme, classification in row:
                token_list.insert("", "end", values=(lexeme, classification))
        for identifier, value, data_type in table:
            symbol_list.insert("", "end", values=(identifier, semantics.displayValue(value), data_type))
        if error_message:
            console.insert("end", error_message + "\n")

    tk.Button(window, text="EXECUTE", command=execute).pack(fill="x")
    console.pack(fill="both")

    window.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        runInTerminal(sys.argv[1])
    else:
        runGUI()
