"""Recursive-descent syntax parser for the LOLCODE project.

The parser uses a token list and a shared cursor. Each parse_* function
handles one part of the grammar and returns a simple tuple-based parse tree.
"""

from lexer import lexer, LexError


class ParseError(Exception):
    pass


tokens = []
current = 0
symbols = None  # the SymbolTable from symbol_table.py (optional)

NAME_TYPES = (
    "Variable Identifier", "Function Identifier",
    "Loop Identifier", "Identifier"
)

ARITHMETIC = (
    "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF",
    "MOD OF", "BIGGR OF", "SMALLR OF"
)
BOOLEAN = ("BOTH OF", "EITHER OF", "WON OF")
COMPARISON = ("BOTH SAEM", "DIFFRINT")
LIST_OPERATIONS = ("SMOOSH", "ALL OF", "ANY OF")


def current_token():
    """Get the token currently being checked."""
    if current < len(tokens):
        return tokens[current]

    if tokens:
        return ("", "End of File", tokens[-1][2])

    return ("", "End of File", 1)


def next_token():
    """Consume the current token and move forward."""
    global current

    token = current_token()
    if token[1] != "End of File":
        current += 1
    return token


def is_token(*words, kinds=(), offset=0):
    """Check a token without consuming it."""
    token_index = current + offset
    if token_index >= len(tokens):
        return "End of File" in kinds

    lexeme, token_type, line = tokens[token_index]
    if lexeme in words and token_type != "YARN Literal":
        return True
    return token_type in kinds


def found_token():
    lexeme, token_type, line = current_token()

    if token_type == "Line Break":
        return "the end of the line"
    if token_type == "End of File":
        return "the end of the file"
    return "'" + lexeme + "'"


def syntax_error(message, token=None):
    if token is None:
        token = current_token()
    raise ParseError("Line " + str(token[2]) + ": " + message)


def expect(*words):
    if not is_token(*words):
        expected = " or ".join("'" + word + "'" for word in words)
        syntax_error("expected " + expected + " but found " + found_token())
    return next_token()


def read_name(description, token_type=None):
    allowed = NAME_TYPES if token_type is None else (token_type,)

    if not is_token(kinds=allowed):
        syntax_error("expected " + description + " but found " + found_token())

    return next_token()[0]


def skip_line_breaks():
    while is_token(kinds=("Line Break",)):
        next_token()


def end_line():
    if is_token(kinds=("End of File",)):
        return

    if not is_token(kinds=("Line Break",)):
        syntax_error("expected the end of the line but found " + found_token())

    skip_line_breaks()


def parse_program():
    line = current_token()[2]
    functions = []
    declarations = []

    skip_line_breaks()

    # Function definitions can be placed before HAI.
    while is_token("HOW IZ I"):
        functions.append(parse_function())
        skip_line_breaks()

    expect("HAI")
    if is_token(kinds=("NUMBAR Literal",)):
        next_token()
    end_line()

    # Variable declarations belong in the WAZZUP section.
    if is_token("WAZZUP"):
        next_token()
        end_line()

        while is_token("I HAS A"):
            declaration_line = next_token()[2]
            variable = read_name("a variable name")
            value = None

            if is_token("ITZ"):
                next_token()
                value = parse_expression(top_level=True)

            declarations.append(("declare", declaration_line, variable, value))

            # Record the variable. A literal gives it a first value, anything else stays NOOB.
            if symbols is not None:
                first_value = None
                if value is not None and value[0] == "literal":
                    first_value = value[3]
                symbols.declare(variable, first_value)

            end_line()

        expect("BUHBYE")
        end_line()

    statements = parse_block("KTHXBYE")
    expect("KTHXBYE")
    end_line()

    # Function definitions can also follow KTHXBYE.
    skip_line_breaks()
    while is_token("HOW IZ I"):
        functions.append(parse_function())
        skip_line_breaks()

    if not is_token(kinds=("End of File",)):
        syntax_error("unexpected " + found_token() + " after KTHXBYE")

    return ("program", line, functions, declarations, statements)


def parse_block(*stop_words):
    statements = []

    while not is_token(*stop_words):
        if is_token(kinds=("End of File",)):
            expected = " or ".join("'" + word + "'" for word in stop_words)
            syntax_error("expected " + expected + " but reached the end of the file")

        statements.append(parse_statement())
        end_line()

    return statements


def parse_statement():
    lexeme, token_type, line = current_token()

    if is_token("VISIBLE"):
        next_token()
        values = [parse_expression(top_level=True)]

        while is_token(kinds=("Output Separator",)):
            next_token()
            values.append(parse_expression(top_level=True))

        suppress_newline = is_token(kinds=("Newline Suppressor",))
        if suppress_newline:
            next_token()

        return ("visible", line, values, suppress_newline)

    if is_token("GIMMEH"):
        next_token()
        return ("gimmeh", line, read_name("a variable name"))

    if is_token("GTFO"):
        next_token()
        return ("break", line)

    if is_token("FOUND YR"):
        next_token()
        return ("return", line, parse_expression(top_level=True))

    if is_token("O RLY?"):
        return parse_if()

    if is_token("WTF?"):
        return parse_switch()

    if is_token("IM IN YR"):
        return parse_loop()

    if is_token("I HAS A"):
        syntax_error(
            "variables must be declared inside WAZZUP ... BUHBYE, before the statements"
        )

    if is_token("HOW IZ I"):
        syntax_error("functions must be defined before HAI or after KTHXBYE")

    if is_token(kinds=NAME_TYPES):
        if is_token("R", offset=1):
            variable = next_token()[0]
            next_token()
            return ("assign", line, variable, parse_expression(top_level=True))

        if is_token("IS NOW A", offset=1):
            variable = next_token()[0]
            next_token()
            value_type = read_name(
                "a type (NUMBR, NUMBAR, YARN, TROOF)", "TYPE Literal"
            )
            return ("recast", line, variable, value_type)

    return ("expr", line, parse_expression(top_level=True))


def parse_if():
    line = next_token()[2]
    end_line()
    expect("YA RLY")
    end_line()

    yes_block = parse_block("MEBBE", "NO WAI", "OIC")
    else_if_blocks = []

    while is_token("MEBBE"):
        next_token()
        condition = parse_expression(top_level=True)
        end_line()
        body = parse_block("MEBBE", "NO WAI", "OIC")
        else_if_blocks.append(("mebbe", condition, body))

    no_block = None
    if is_token("NO WAI"):
        next_token()
        end_line()
        no_block = parse_block("OIC")

    expect("OIC")
    return ("if", line, yes_block, else_if_blocks, no_block)


def parse_switch():
    line = next_token()[2]
    end_line()
    expect("OMG")
    cases = []

    while True:
        case_value = parse_literal()
        end_line()
        case_body = parse_block("OMG", "OMGWTF", "OIC")
        cases.append(("case", case_value, case_body))

        if not is_token("OMG"):
            break
        next_token()

    default_block = None
    if is_token("OMGWTF"):
        next_token()
        end_line()
        default_block = parse_block("OIC")

    expect("OIC")
    return ("switch", line, cases, default_block)


def parse_loop():
    line = next_token()[2]
    loop_name = read_name("a loop name")

    operation = None
    variable = None
    condition_kind = None
    condition = None

    if is_token("UPPIN", "NERFIN"):
        operation = next_token()[0]
        expect("YR")
        variable = read_name("a variable name")

        if is_token("TIL", "WILE"):
            condition_kind = next_token()[0]
            condition = parse_expression(top_level=True)

    end_line()
    body = parse_block("IM OUTTA YR")
    expect("IM OUTTA YR")

    closing_token = current_token()
    closing_name = read_name("the loop name")
    if closing_name != loop_name:
        syntax_error(
            "loop '" + loop_name + "' is closed with a different name '" +
            closing_name + "'",
            closing_token
        )

    return (
        "loop", line, loop_name, operation, variable,
        condition_kind, condition, body
    )


def parse_function():
    line = next_token()[2]
    name = read_name("a function name")
    parameters = []

    if is_token("YR"):
        next_token()
        parameters.append(read_name("a parameter name"))

        while is_token("AN"):
            next_token()
            expect("YR")
            parameters.append(read_name("a parameter name"))

    end_line()
    body = parse_block("IF U SAY SO")
    expect("IF U SAY SO")
    end_line()

    return ("function", line, name, parameters, body)


def parse_expression(top_level=False):
    lexeme, token_type, line = current_token()

    if top_level and is_token("SMOOSH"):
        next_token()
        values = [parse_expression()]

        while is_token("AN"):
            next_token()
            values.append(parse_expression())

        return ("nary", line, "SMOOSH", values)

    if top_level and is_token("ALL OF", "ANY OF"):
        next_token()
        values = [parse_expression()]

        while is_token("AN"):
            next_token()
            values.append(parse_expression())

        expect("MKAY")
        return ("nary", line, lexeme, values)

    if is_token(kinds=NAME_TYPES):
        next_token()
        return ("var", line, lexeme)

    if is_token(kinds=(
        "NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "String Delimiter"
    )):
        return parse_literal()

    if is_token(*ARITHMETIC, *BOOLEAN, *COMPARISON):
        next_token()
        left = parse_expression()
        expect("AN")
        right = parse_expression()
        return ("binary", line, lexeme, left, right)

    if is_token("NOT"):
        next_token()
        return ("unary", line, "NOT", parse_expression())

    if is_token("MAEK"):
        next_token()
        value = parse_expression()

        if is_token("A"):
            next_token()

        value_type = read_name(
            "a type (NUMBR, NUMBAR, YARN, TROOF)", "TYPE Literal"
        )
        return ("cast", line, value, value_type)

    if is_token("I IZ"):
        next_token()
        function_name = read_name("a function name")
        arguments = []

        if is_token("YR"):
            next_token()
            arguments.append(parse_expression())

            while is_token("AN"):
                next_token()
                expect("YR")
                arguments.append(parse_expression())

        expect("MKAY")
        return ("call", line, function_name, arguments)

    if is_token(*LIST_OPERATIONS):
        syntax_error(lexeme + " cannot be used inside another expression")

    syntax_error(
        "expected a value or an operation but found " + found_token()
    )


def parse_literal():
    lexeme, token_type, line = current_token()

    if token_type == "NUMBR Literal":
        next_token()
        return ("literal", line, "NUMBR", int(lexeme))

    if token_type == "NUMBAR Literal":
        next_token()
        return ("literal", line, "NUMBAR", float(lexeme))

    if token_type == "TROOF Literal":
        next_token()
        return ("literal", line, "TROOF", lexeme == "WIN")

    if token_type == "String Delimiter":
        next_token()

        if not is_token(kinds=("YARN Literal",)):
            syntax_error("expected the text of a string")

        value = next_token()[0]

        if not is_token(kinds=("String Delimiter",)):
            syntax_error("string is missing its closing quote")

        next_token()
        return ("literal", line, "YARN", value)

    syntax_error(
        "expected a number, string or WIN/FAIL but found " + found_token()
    )


def parse(source_code, symbol_table=None):
    """Run the lexer, then check the resulting tokens against the grammar.

    If a SymbolTable is given, it is filled with the variables from WAZZUP ... BUHBYE.
    """
    global tokens, current, symbols

    tokens = []
    current = 0
    symbols = symbol_table
    if symbols is not None:
        symbols.clear()
    list(lexer(source_code, tokens))
    return parse_program()


if __name__ == "__main__":
    import sys
    from symbol_table import SymbolTable

    file_name = sys.argv[1] if len(sys.argv) > 1 else "sample.lol"

    with open(file_name, "r", encoding="utf-8") as source_file:
        source_code = source_file.read()

    try:
        table = SymbolTable()
        tree = parse(source_code, table)
        print("Syntax OK")

        print("\nSymbol table:")
        for row in table.get_all_variables_for_gui():
            print("  " + row["identifier"].ljust(10) + row["type"].ljust(8) + row["value"])
    except (LexError, ParseError) as error:
        print("Error:", error)
