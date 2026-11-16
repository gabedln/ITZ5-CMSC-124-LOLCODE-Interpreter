# LOLCODE Interpreter

<div align="center" style="margin-top: 25px; margin-bottom: 25px">
<img src="lolcode-icon.png" alt="LOLCODE LOGO" width="300">
</div>

---

## Project Overview

This project implements An interpreter for **LOLCODE** built in Python for **CMSC 124**. It analyzes, validates, and executes `.lol` source programs through modular lexical, syntactic, and semantic phases.

### Core Architecture

- **Lexical Analyzer:** Strips comments (`BTW`, `OBTW...TLDR`) and tokenizes raw source code into a structured Lexeme Table using pattern matching.

- **Syntax Analyzer:** Enforces grammar rules (`HAI...KTHXBYE`, `WAZZUP...BUHBYE`, prefix operations with `AN`), validates control structures, and compiles tokens into an executable Syntax/Instruction Table.

- **Semantic Analyzer:** Manages the runtime Symbol Table, handles dynamic typing and LOLCODE typecasting, tracks the implicit `IT` accumulator, and executes instructions sequentially.

- **User Interface:** Frontend Tkinter dashboard featuring a source editor, interactive Lexeme and Symbol table inspectors, and an execution output console.

---

## Getting Started

### Prerequisites

- **Python 3.8 or higher**
- **Tkinter** (standard GUI package bundled with most Python installations on Windows and macOS)

> **Note for Linux users:** If Tkinter is not bundled with your Python environment, install it via:
> ```bash
> sudo apt-get update && sudo apt-get install python3-tk
> ```

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mddeleon7/ITZ5-CMSC-124-LOLCODE-Interpreter.git
   cd ITZ5-CMSC-124-LOLCODE-Interpreter
   ```

2. **Verify Python installation:**
   ```bash
   python3 --version
   ```

*(All required packages such as `re`, `decimal`, and `tkinter` use Python standard libraries, so no external `pip` dependencies are needed).*

### Running the Project

- **Launch the GUI Application:**
  ```bash
  python3 main.py
  ```
---

## Contributors & Team Members

**CMSC 124 — Section ST2L, Group ITZ5**  
*Design and Implementation of Programming Languages*  
Institute of Computer Science, University of the Philippines Los Baños

- Montas, Natasha Lois Salcedo
- De Leon, Mari Gabriel Dalma
- Ellao, Franz Jeremy Gonzales
- Alde, Mark Kennard Cruz
