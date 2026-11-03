import sys
from lexer import lexer, LexError

tokens, pos, furthest, expected = [], 0, 0, set()

# main parser function

def parse(lexemes):
    global tokens, pos, furthest, expected
    last_line = lexemes[-1][2] if lexemes else 1
    tokens = [t for idx, t in enumerate(lexemes) if idx > 0 or t[1] != "Line Break"]
    tokens.append(("EOF", "EOF", last_line))
    pos, furthest, expected = 0, 0, set()

    tree = program()
    if tree and tokens[pos][1] == "EOF":
        return tree

    lex, kind, line = tokens[furthest]
    if kind == "Identifier":
        raise SyntaxError(f"Line {line}: Undeclared identifier '{lex}'")
    raise SyntaxError(f"Line {line}: Unexpected '{lex}' ({kind}); expected {', '.join(sorted(expected))}")

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

# helper functions

def match(step):
    global pos, furthest, expected

    if callable(step): return step() # if callable/grammar rule sequence function (ex. var_dec_block, etc...), call (recursion)
    names = step if isinstance(step, tuple) else (step,) # normalize to tuple

    lex, kind, line = tokens[pos] # take current token
    if lex in names or kind in names: # if match
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

# grammar rule functions 

# program structure

def program():
    head = ("<program>", outer, "HAI", version, linebreak, body, "KTHXBYE")
    return seq(*head, linebreak, outer) or seq(*head)

def version():
    return seq("<version>", ("NUMBR Literal", "NUMBAR Literal")) or seq("<version>")

def outer():
    return seq("<outer>", func_def, outer) or seq("<outer>", line_end, outer) or seq("<outer>")

def body():
    return seq("<body>", var_dec_block, statement_list)

def statement_list():
    return seq("<statement_list>", statement, linebreak, statement_list) or seq("<statement_list>")

# line break

def linebreak():
    return seq("<linebreak>", line_end, linebreak) or seq("<linebreak>", line_end)

def line_end():
    return seq("<line_end>", "Line Break")

# variable declaration block

def var_dec_block():
    return seq("<var_dec_block>", "WAZZUP", linebreak, var_dec_list, "BUHBYE", linebreak) or seq("<var_dec_block>")

def var_dec_list():
    return seq("<var_dec_list>", var_dec, linebreak, var_dec_list) or seq("<var_dec_list>")

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
    return seq("<input>", "GIMMEH", "Variable Identifier")

def assignment():
    return seq("<assignment>", "Variable Identifier", "R", top_expr)

def typecast():
    return seq("<typecast>", "Variable Identifier", "IS NOW A", "TYPE Literal")

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
    return seq("<case_list>", case_item, case_list) or seq("<case_list>", case_item)

def case_item():
    return seq("<case_item>", "OMG", literal, linebreak, statement_list)

def default_block():
    return seq("<default_block>", "OMGWTF", linebreak, statement_list) or seq("<default_block>")

# loop statement block

def loop_block():
    return seq("<loop_block>", "IM IN YR", "Loop Identifier", loop_upd, linebreak, statement_list, "IM OUTTA YR", "Loop Identifier")

def loop_upd():
    return seq("<loop_upd>", "Loop Operation", "YR", "Variable Identifier", loop_cond) or seq("<loop_upd>")

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
    return (seq("<expr>", "Variable Identifier") or seq("<expr>", literal) or seq("<expr>", arithmetic_expr) or seq("<expr>", boolean_expr) 
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
    file_name = sys.argv[1] if len(sys.argv) > 1 else "sample.lol"
    with open(file_name, "r", encoding="utf-8") as file:
        code = file.read()

    sys.stdout = open("output.txt", "w", encoding="utf-8")

    try:
        lexemes = []
        for _ in lexer(code, lexemes): pass
        tree = parse(lexemes)
        print_tree(tree)
    except (LexError, SyntaxError) as error:
        print(f"{type(error).__name__}: {error}")