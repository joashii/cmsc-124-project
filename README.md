# LOLCODE Interpreter

This project is a simple LOLCODE lexer, parser, and interpreter built with Python and NiceGUI.

## Files
- **main.py:** The entry point of the application. It builds the NiceGUI interface, handles file uploads, and manages the overall execution flow. It runs the lexer and parser, displays the live lexeme and symbol tables, and executes the program in a background thread so the GUI remains responsive during loops or GIMMEH input.
- **lexer.py:** The lexical analyzer. It reads the raw LOLCode source string and tokenizes it into a stream of meaningful lexemes. It handles all LOLCode keywords, literals, comments, string escapes, and classifies identifiers (variables, functions, loops).
- **parser.py:** The syntax analyzer (recursive descent parser). It consumes the tokenized lexemes and verifies that they follow the correct LOLCode grammar. If successful, it builds and returns a parse tree. It also populates the global variables in the SymbolTable based on the WAZZUP block.
- **symbol_table.py:** The data structure that stores variables and their current values. It uses a stack to handle different scopes during function calls. It also acts as a bridge to the GUI, providing the on_change hook so the front-end knows exactly when a variable's value or type updates.
- **interpreter.py**
- **expressions.py**

## Requirements
- Python 3
- NiceGUI

## How to Run
1. Open the directory in terminal.
2. Run python3 main.py.
3. Input LOLCODE file or write directly in code editor.
4. Click run to start.
5. View the console for output.