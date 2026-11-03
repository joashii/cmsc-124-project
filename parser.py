import sys
from lexer import lexer, LexError

# Error raised when the code does not follow the grammar.
class ParseError(Exception):
    pass

tokens, pos, furthest, expected = [], 0, 0, set()

# A variable name. "Identifier" is a name the lexer never saw declared: the parser still
# accepts it (checking that a variable was declared is left to the semantic analyzer).
VARIABLE = ("Variable Identifier", "Identifier")

# main parser function

# check the lexemes against the grammar; returns the parse tree or raises ParseError.
# If a symbol table is given, the variables declared in WAZZUP ... BUHBYE are put in it.
def parse(lexemes, symbol_table=None):
    global tokens, pos, furthest, expected
    last_line = lexemes[-1][2] if lexemes else 1
    tokens = [t for idx, t in enumerate(lexemes) if idx > 0 or t[1] != "Line Break"]
    tokens.append(("EOF", "EOF", last_line))
    pos, furthest, expected = 0, 0, set()
    if symbol_table is not None:
        symbol_table.clear()

    try:
        tree = program()
    except RecursionError:
        raise ParseError("the program is nested too deeply to be checked")

    if tree and tokens[pos][1] == "EOF":
        if symbol_table is not None:
            fill_symbol_table(tree, symbol_table)
        return tree

    # the program was read up to KTHXBYE but something else follows it
    if tree and furthest <= pos:
        raise ParseError(f"Line {tokens[pos][2]}: unexpected {describe_found(tokens[pos])} after KTHXBYE")

    raise ParseError(build_error())

# print resulting tree

def print_tree(node, prefix="", last=True):
    label, data = node
    branch = "└── " if last else "├── "
    if isinstance(data, tuple):
        print(f"{prefix}{branch}{label}: {data[0]!r} (line {data[1]})")
        return
    print(f"{prefix}{branch}{label}" if prefix else label)
    child_prefix = (prefix + ("    " if last else "│   ")) if prefix else " "
    for i, child in enumerate(data):
        print_tree(child, child_prefix, i == len(data) - 1)

# error messages

# tokens that can start something, used to keep "expected ..." short
EXPR_START = {"Variable Identifier", "Identifier", "NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "String Delimiter",
              "Arithmetic Operation", "Comparison Operation", "BOTH OF", "EITHER OF", "WON OF", "NOT", "MAEK", "I IZ"}
TOP_EXPR_START = EXPR_START | {"SMOOSH", "ALL OF", "ANY OF"}
STATEMENT_START = {"VISIBLE", "GIMMEH", "GTFO", "FOUND YR", "O RLY?", "WTF?", "IM IN YR"}
LITERAL_START = {"NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "String Delimiter"}

# how a token kind is written in an error message (keywords are just written in quotes)
NICE_NAMES = {
    "Line Break": "the end of the line",
    "Variable Identifier": "a variable name",
    "Identifier": "a variable name",
    "Function Identifier": "a function name",
    "Loop Identifier": "a loop name",
    "TYPE Literal": "a type (NUMBR, NUMBAR, YARN, TROOF)",
    "YARN Literal": "the text of a string",
    "Loop Operation": "'UPPIN' or 'NERFIN'",
    "Loop Condition": "'TIL' or 'WILE'",
    "Arithmetic Operation": "an arithmetic operation",
    "Comparison Operation": "a comparison operation",
    "NUMBR Literal": "a number",
    "NUMBAR Literal": "a number",
    "TROOF Literal": "WIN or FAIL",
    "String Delimiter": "a string",
}

# "a, b or c"
def join_words(texts):
    if len(texts) <= 1:
        return "".join(texts)
    return ", ".join(texts[:-1]) + " or " + texts[-1]

# the token that was found, as written in an error message
def describe_found(token):
    lex, kind, line = token
    if kind == "Line Break":
        return "the end of the line"
    if kind == "EOF":
        return "the end of the file"
    if kind == "String Delimiter":
        return "a string"
    return "'" + lex + "'"

# the tokens that were expected, as written in an error message
def describe_expected(names):
    names = set(names)
    texts = []

    # if every token that can start a statement (or a value) is allowed, say it in a few words
    if STATEMENT_START <= names:
        names -= STATEMENT_START | TOP_EXPR_START
        texts.append("a statement")
    elif TOP_EXPR_START <= names:
        names -= TOP_EXPR_START
        texts.append("a value or an operation")
    elif EXPR_START <= names:
        names -= EXPR_START
        texts.append("a value or an operation")
    elif LITERAL_START <= names:
        names -= LITERAL_START
        texts.append("a number, string or WIN/FAIL")

    for name in sorted(names):
        text = NICE_NAMES.get(name, "'" + name + "'")
        if text not in texts:
            texts.append(text)

    if "the end of the line" in texts:  # keep it last
        texts.remove("the end of the line")
        texts.append("the end of the line")
    return join_words(texts)

# at the end of the file: the closing keyword of the innermost block that was never closed
def missing_closer():
    openers = {"HAI": "KTHXBYE", "WAZZUP": "BUHBYE", "HOW IZ I": "IF U SAY SO",
               "IM IN YR": "IM OUTTA YR", "O RLY?": "OIC", "WTF?": "OIC"}
    open_blocks = []
    for lex, kind, line in tokens:
        if kind == "YARN Literal":
            continue
        if lex in openers:
            open_blocks.append(openers[lex])
        elif lex in openers.values() and open_blocks and open_blocks[-1] == lex:
            open_blocks.pop()
    return open_blocks[-1] if open_blocks else None

# the message for a program that does not match the grammar (uses the furthest token that failed)
def build_error():
    lex, kind, line = tokens[furthest]
    first_in_line = furthest > 0 and tokens[furthest - 1][1] == "Line Break"

    # mistakes that have their own message
    if kind == "Variable Declaration" and first_in_line and "I HAS A" not in expected:
        return f"Line {line}: variables must be declared inside WAZZUP ... BUHBYE, before the statements"
    if lex == "HOW IZ I" and first_in_line and "HOW IZ I" not in expected:
        return f"Line {line}: functions must be defined before HAI or after KTHXBYE"
    if lex in ("SMOOSH", "ALL OF", "ANY OF") and "ALL OF" not in expected:
        return f"Line {line}: {lex} cannot be used inside another expression"
    if kind == "EOF" and ("Line Break" in expected or "KTHXBYE" in expected):
        closer = missing_closer()
        if closer:
            return f"Line {line}: expected '{closer}' but reached the end of the file"

    return f"Line {line}: expected {describe_expected(expected)} but found {describe_found(tokens[furthest])}"

# symbol table

# put the variables of the WAZZUP block in the symbol table (done after the tree is complete)
def fill_symbol_table(node, table):
    label, data = node
    if label in ("<program>", "<body>", "<var_dec_block>", "<var_dec_list>"):
        for child in data:
            fill_symbol_table(child, table)
    elif label == "<var_dec>":
        name = data[1][1][0]  # I HAS A <name> [ITZ <value>]
        table.declare(name, literal_value(data[3]) if len(data) == 4 else None)

# the Python value of a <top_expr> that is only a literal; None for anything else
# (a variable or an operation has no value until the program runs)
def literal_value(node):
    for label in ("<top_expr>", "<expr>"):
        if node[0] != label or len(node[1]) != 1:
            return None
        node = node[1][0]
    if node[0] != "<literal>":
        return None

    kind, lex = node[1][0][0], node[1][0][1][0]
    if kind == "NUMBR Literal": return int(lex)
    if kind == "NUMBAR Literal": return float(lex)
    if kind == "TROOF Literal": return lex == "WIN"
    return node[1][1][1][0]  # a string: " text "

# helper functions

def match(step):
    global pos, furthest, expected

    if callable(step): return step() # if callable/grammar rule sequence function (ex. var_dec_block, etc...), call (recursion)
    names = step if isinstance(step, tuple) else (step,) # normalize to tuple

    lex, kind, line = tokens[pos] # take current token
    # the text inside a string never counts as a keyword
    if kind in names or (lex in names and kind != "YARN Literal"): # if match
        pos += 1
        return [kind, (lex, line)] # return terminal node

    # basic grammar error handling
    if pos > furthest: furthest, expected = pos, set()
    if pos == furthest: expected.update(names)
    return None

def seq(label, *steps):
    global pos

    start = pos # current position for backtracking
    children = [] # list of child nodes

    # try to match each step in the sequence
    for step in steps:
        child = match(step)

        # if matching fails, backtrack by reverting to last position
        if child is None:
            pos = start
            return None
        # else add child to children
        children.append(child)

    return [label, children] # return nonterminal node

# match the steps again and again (as many times as possible) into one flat node
# (a loop instead of recursion, so a long program does not run out of Python's recursion limit)
def repeat(label, *steps):
    children = []
    while True:
        start = pos
        item = seq(label, *steps)
        if item is None or pos == start: break
        children += item[1]
    return [label, children]

# grammar rule functions 

# program structure

def program():
    head = ("<program>", outer, "HAI", version, linebreak, body, "KTHXBYE")
    return seq(*head, linebreak, outer) or seq(*head)

def version():
    return seq("<version>", ("NUMBR Literal", "NUMBAR Literal")) or seq("<version>")

def outer():
    children = []
    while True:
        item = func_def() or line_end()
        if item is None: break
        children.append(item)
    return ["<outer>", children]

def body():
    return seq("<body>", var_dec_block, statement_list)

def statement_list():
    return repeat("<statement_list>", statement, linebreak)

# line break

def linebreak():
    node = repeat("<linebreak>", line_end)
    return node if node[1] else None

def line_end():
    return seq("<line_end>", "Line Break")

# variable declaration block

def var_dec_block():
    return seq("<var_dec_block>", "WAZZUP", linebreak, var_dec_list, "BUHBYE", linebreak) or seq("<var_dec_block>")

def var_dec_list():
    return repeat("<var_dec_list>", var_dec, linebreak)

def var_dec():
    return seq("<var_dec>", "I HAS A", "Variable Identifier", "ITZ", top_expr) or seq("<var_dec>", "I HAS A", "Variable Identifier")

# statements

def statement():
    return (seq("<statement>", output) or seq("<statement>", input_) or seq("<statement>", assignment) or seq("<statement>", typecast)
        or seq("<statement>", if_block) or seq("<statement>", switch_block) or seq("<statement>", loop_block)
        or seq("<statement>", break_) or seq("<statement>", return_) or seq("<statement>", top_expr)
    )

def output():
    return seq("<output>", "VISIBLE", top_expr, output_list, output_end)

def output_list():
    return seq("<output_list>", "+", top_expr, output_list) or seq("<output_list>")

def output_end():
    return seq("<output_end>", "!") or seq("<output_end>")

def input_():
    return seq("<input>", "GIMMEH", VARIABLE)

def assignment():
    return seq("<assignment>", VARIABLE, "R", top_expr)

def typecast():
    return seq("<typecast>", VARIABLE, "IS NOW A", "TYPE Literal")

def break_():
    return seq("<break>", "GTFO")

def return_():
    return seq("<return>", "FOUND YR", top_expr)

# if statement block

def if_block():
    return seq("<if_block>", "O RLY?", linebreak, "YA RLY", linebreak, statement_list, elif_block, else_block, "OIC")

def elif_block():
    return seq("<elif_block>", "MEBBE", top_expr, linebreak, statement_list, elif_block) or seq("<elif_block>")

def else_block():
    return seq("<else_block>", "NO WAI", linebreak, statement_list) or seq("<else_block>")

# switch statement block

def switch_block():
    return seq("<switch_block>", "WTF?", linebreak, case_list, default_block, "OIC")

def case_list():
    node = repeat("<case_list>", case_item)
    return node if node[1] else None

def case_item():
    return seq("<case_item>", "OMG", literal, linebreak, statement_list)

def default_block():
    return seq("<default_block>", "OMGWTF", linebreak, statement_list) or seq("<default_block>")

# loop statement block

def loop_block():
    global pos
    start = pos
    node = seq("<loop_block>", "IM IN YR", "Loop Identifier", loop_upd, linebreak, statement_list, "IM OUTTA YR")
    if node is None:
        return None

    # the loop must be closed with the same name it was opened with
    opened = node[1][1][1][0]
    closing = match(("Loop Identifier", "Variable Identifier", "Identifier"))
    if closing is None:
        pos = start
        return None
    if closing[1][0] != opened:
        raise ParseError(f"Line {closing[1][1]}: loop '{opened}' is closed with a different name '{closing[1][0]}'")

    node[1].append(closing)
    return node

def loop_upd():
    return seq("<loop_upd>", "Loop Operation", "YR", VARIABLE, loop_cond) or seq("<loop_upd>")

def loop_cond():
    return seq("<loop_cond>", "Loop Condition", top_expr) or seq("<loop_cond>")

# functions

def func_def():
    return seq("<func_def>", "HOW IZ I", "Function Identifier", func_params, linebreak, statement_list, "IF U SAY SO", linebreak)

def func_params():
    return seq("<func_params>", "YR", "Variable Identifier", param_list) or seq("<func_params>")

def param_list():
    return seq("<param_list>", "AN", "YR", "Variable Identifier", param_list) or seq("<param_list>")

def func_call():
    return seq("<func_call>", "I IZ", "Function Identifier", call_args, "MKAY")

def call_args():
    return seq("<call_args>", "YR", expr, arg_list) or seq("<call_args>")

def arg_list():
    return seq("<arg_list>", "AN", "YR", expr, arg_list) or seq("<arg_list>")

# operations

def top_expr():
    return seq("<top_expr>", expr) or seq("<top_expr>", concat_expr) or seq("<top_expr>", all_expr) or seq("<top_expr>", any_expr)

def expr():
    return (seq("<expr>", VARIABLE) or seq("<expr>", literal) or seq("<expr>", arithmetic_expr) or seq("<expr>", boolean_expr) 
            or seq("<expr>", comparison_expr) or seq("<expr>", cast_expr) or seq("<expr>", func_call))

def literal():
    return seq("<literal>", ("NUMBR Literal", "NUMBAR Literal", "TROOF Literal")) or seq("<literal>", "String Delimiter", "YARN Literal", "String Delimiter")

def arithmetic_expr():
    return seq("<arithmetic_expr>", "Arithmetic Operation", expr, "AN", expr)

def boolean_expr():
    return seq("<boolean_expr>", "NOT", expr) or seq("<boolean_expr>", ("BOTH OF", "EITHER OF", "WON OF"), expr, "AN", expr)

def comparison_expr():
    return seq("<comparison_expr>", "Comparison Operation", expr, "AN", expr)

def concat_expr():
    return seq("<concat_expr>", "SMOOSH", expr_list)

def cast_expr():
    return seq("<cast_expr>", "MAEK", expr, "A", "TYPE Literal") or seq("<cast_expr>", "MAEK", expr, "TYPE Literal")

def all_expr():
    return seq("<all_expr>", "ALL OF", expr_list, "MKAY")

def any_expr():
    return seq("<any_expr>", "ANY OF", expr_list, "MKAY")

def expr_list():
    return seq("<expr_list>", expr, "AN", expr_list) or seq("<expr_list>", expr)

if __name__ == "__main__":
    from symbol_table import SymbolTable

    file_name = sys.argv[1] if len(sys.argv) > 1 else "sample.lol"

    # Handle errors when opening or reading the input file.
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: file '{file_name}' was not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: permission denied when reading '{file_name}'.", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: file '{file_name}' is not a valid UTF-8 text file.", file=sys.stderr)
        sys.exit(1)
    except OSError as error:
        print(f"Error reading '{file_name}': {error}", file=sys.stderr)
        sys.exit(1)

        # Handle errors when creating the output file.
    try:
        sys.stdout = open("output.txt", "w", encoding="utf-8")
    except OSError as error:
        print(f"Error creating output.txt: {error}", file=sys.stderr)
        sys.exit(1)

    try:
        lexemes = []
        for _ in lexer(code, lexemes): pass
        table = SymbolTable()
        tree = parse(lexemes, table)
        print_tree(tree)

        print("\nSymbol table:")
        for row in table.get_all_variables_for_gui():
            print("  " + row["identifier"].ljust(10) + row["type"].ljust(8) + row["value"])
    except (LexError, ParseError) as error:
        print(f"{type(error).__name__}: {error}")
