from lexer import lexer, LexError

class ParseError(Exception):
    pass

tokens = []     # the tokens made by the lexer
current = 0     # the position of the token we are checking now
symbols = None  # the SymbolTable from symbol_table.py

# kinds of token that can be a name ("Identifier" = not declared yet)
NAME_TYPES = ("Variable Identifier", "Function Identifier", "Loop Identifier", "Identifier")
LITERAL_TYPES = ("NUMBR Literal", "NUMBAR Literal", "TROOF Literal", "String Delimiter")
# operators followed by two expressions:  operator expression AN expression
OPERATORS = ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF",
             "BOTH OF", "EITHER OF", "WON OF", "BOTH SAEM", "DIFFRINT")

# tokens and errors
# the token being checked (an 'End of File' token after the last one)
def current_token():
    if current < len(tokens):
        return tokens[current]
    return ("", "End of File", tokens[-1][2] if tokens else 1)

# take the current token and move on
def next_token():
    global current
    token = current_token()
    if token[1] != "End of File":
        current += 1
    return token

# is the current token one of these keywords? (text inside a string never counts)
def is_word(*words):
    lexeme, kind, line = current_token()
    return lexeme in words and kind != "YARN Literal"

# is the current token one of these classifications?
def is_kind(*kinds):
    return current_token()[1] in kinds

# the current token as written in an error message
def found_token():
    lexeme, kind, line = current_token()
    if kind == "Line Break":
        return "the end of the line"
    if kind == "End of File":
        return "the end of the file"
    return "'" + lexeme + "'"

def syntax_error(message, token=None):
    token = token or current_token()
    raise ParseError("Line " + str(token[2]) + ": " + message)

# stop with an error: what we wanted and what we found
def expected(description):
    syntax_error("expected " + description + " but found " + found_token())

# the current token must be one of these keywords
def expect(*words):
    if not is_word(*words):
        expected(" or ".join("'" + word + "'" for word in words))
    return next_token()

# the current token must be a name; returns it
def read_name(description):
    if not is_kind(*NAME_TYPES):
        expected(description)
    return next_token()[0]

# the current token must be a type; returns it
def read_type():
    if not is_kind("TYPE Literal"):
        expected("a type (NUMBR, NUMBAR, YARN, TROOF)")
    return next_token()[0]

def skip_line_breaks():
    while is_kind("Line Break"):
        next_token()

# a statement must end with a line break or the end of the file
def end_line():
    if not is_kind("Line Break", "End of File"):
        expected("the end of the line")
    skip_line_breaks()


# program and statements
# functions, HAI, WAZZUP declarations, statements, KTHXBYE, more functions
def parse_program():
    skip_line_breaks()
    while is_word("HOW IZ I"):  # functions can be written before HAI
        parse_function()
        skip_line_breaks()

    expect("HAI")
    if is_kind("NUMBAR Literal"):
        next_token()  # the version, like 1.2
    end_line()

    # variables are declared between WAZZUP and BUHBYE only
    if is_word("WAZZUP"):
        next_token()
        end_line()

        while is_word("I HAS A"):
            next_token()
            variable = read_name("a variable name")
            first_value = None  # stays NOOB until the interpreter gives it a value

            if is_word("ITZ"):
                next_token()
                if is_kind(*LITERAL_TYPES):
                    first_value = parse_literal()  # ITZ 10, ITZ "hi", ITZ WIN ...
                else:
                    parse_expression(top_level=True)  # a variable or an operation

            if symbols is not None:
                symbols.declare(variable, first_value)
            end_line()

        expect("BUHBYE")
        end_line()

    parse_block("KTHXBYE")
    expect("KTHXBYE")
    end_line()

    while is_word("HOW IZ I"):  # functions can also be written after KTHXBYE
        parse_function()
        skip_line_breaks()
    if not is_kind("End of File"):
        syntax_error("unexpected " + found_token() + " after KTHXBYE")

# HOW IZ I name [YR a AN YR b] ... IF U SAY SO
def parse_function():
    expect("HOW IZ I")
    read_name("a function name")

    if is_word("YR"):  # parameters:  YR a AN YR b AN YR c
        next_token()
        read_name("a parameter name")
        while is_word("AN"):
            next_token()
            expect("YR")
            read_name("a parameter name")

    end_line()
    parse_block("IF U SAY SO")
    expect("IF U SAY SO")
    end_line()

# check statements until one of the stop words comes
def parse_block(*stop_words):
    while not is_word(*stop_words):
        if is_kind("End of File"):
            expected_words = " or ".join("'" + word + "'" for word in stop_words)
            syntax_error("expected " + expected_words + " but reached the end of the file")
        parse_statement()
        end_line()  # every statement sits on its own line

# the first word tells which kind of statement it is
def parse_statement():
    if is_word("VISIBLE"):
        next_token()
        parse_expression(top_level=True)
        while is_kind("Output Separator"):  # the + between the things to print
            next_token()
            parse_expression(top_level=True)
        if is_kind("Newline Suppressor"):  # the ! at the end
            next_token()
    elif is_word("GIMMEH"):
        next_token()
        read_name("a variable name")
    elif is_word("GTFO"):
        next_token()
    elif is_word("FOUND YR"):
        next_token()
        parse_expression(top_level=True)
    elif is_word("O RLY?"):
        parse_if()
    elif is_word("WTF?"):
        parse_switch()
    elif is_word("IM IN YR"):
        parse_loop()
    elif is_word("I HAS A"):
        syntax_error("variables must be declared inside WAZZUP ... BUHBYE, before the statements")
    elif is_word("HOW IZ I"):
        syntax_error("functions must be defined before HAI or after KTHXBYE")
    elif is_kind(*NAME_TYPES):  # assignment, recast, or a lone name
        next_token()  # the name
        if is_word("R"):  # name R expression
            next_token()
            parse_expression(top_level=True)
        elif is_word("IS NOW A"):  # name IS NOW A type
            next_token()
            read_type()
    else:
        parse_expression(top_level=True)  # any other expression sets IT

# O RLY? / YA RLY / MEBBE / NO WAI / OIC
def parse_if():
    next_token()  # O RLY?
    end_line()
    expect("YA RLY")
    end_line()
    parse_block("MEBBE", "NO WAI", "OIC")

    while is_word("MEBBE"):
        next_token()
        parse_expression(top_level=True)
        end_line()
        parse_block("MEBBE", "NO WAI", "OIC")

    if is_word("NO WAI"):
        next_token()
        end_line()
        parse_block("OIC")
    expect("OIC")

# WTF? / OMG literal / OMGWTF / OIC
def parse_switch():
    next_token()  # WTF?
    end_line()
    expect("OMG")

    while True:  # one case at a time
        parse_literal()
        end_line()
        parse_block("OMG", "OMGWTF", "OIC")
        if not is_word("OMG"):
            break
        next_token()

    if is_word("OMGWTF"):
        next_token()
        end_line()
        parse_block("OIC")
    expect("OIC")

# IM IN YR name [UPPIN|NERFIN YR var [TIL|WILE expression]] ... IM OUTTA YR name
def parse_loop():
    next_token()  # IM IN YR
    loop_name = read_name("a loop name")

    if is_word("UPPIN", "NERFIN"):  # this part is optional
        next_token()
        expect("YR")
        read_name("a variable name")
        if is_word("TIL", "WILE"):
            next_token()
            parse_expression(top_level=True)

    end_line()
    parse_block("IM OUTTA YR")
    expect("IM OUTTA YR")

    closing_token = current_token()  # must end with the name it started with
    closing_name = read_name("the loop name")
    if closing_name != loop_name:
        syntax_error("loop '" + loop_name + "' is closed with a different name '" + closing_name + "'",
                     closing_token)


# expressions
# top_level is True for a whole statement or value; SMOOSH, ALL OF, ANY OF only work there
def parse_expression(top_level=False):
    if top_level and is_word("SMOOSH", "ALL OF", "ANY OF"):
        operator = next_token()[0]
        parse_expression()
        while is_word("AN"):
            next_token()
            parse_expression()
        if operator != "SMOOSH":  # only SMOOSH has no MKAY
            expect("MKAY")
    elif is_kind(*NAME_TYPES):
        next_token()
    elif is_kind(*LITERAL_TYPES):
        parse_literal()
    elif is_word(*OPERATORS):  # operator expression AN expression
        next_token()
        parse_expression()
        expect("AN")
        parse_expression()
    elif is_word("NOT"):
        next_token()
        parse_expression()
    elif is_word("MAEK"):  # MAEK expression [A] type
        next_token()
        parse_expression()
        if is_word("A"):
            next_token()
        read_type()
    elif is_word("I IZ"):  # I IZ name [YR expression {AN YR expression}] MKAY
        next_token()
        read_name("a function name")
        if is_word("YR"):
            next_token()
            parse_expression()
            while is_word("AN"):
                next_token()
                expect("YR")
                parse_expression()
        expect("MKAY")
    elif is_word("SMOOSH", "ALL OF", "ANY OF"):
        syntax_error(current_token()[0] + " cannot be used inside another expression")
    else:
        expected("a value or an operation")

# check one literal and return its Python value
def parse_literal():
    lexeme, kind, line = current_token()

    if kind == "String Delimiter":  # a string is three tokens:  "  text  "
        next_token()
        if not is_kind("YARN Literal"):
            syntax_error("expected the text of a string")
        text = next_token()[0]
        if not is_kind("String Delimiter"):
            syntax_error("string is missing its closing quote")
        next_token()
        return text

    if kind == "NUMBR Literal":
        value = int(lexeme)
    elif kind == "NUMBAR Literal":
        value = float(lexeme)
    elif kind == "TROOF Literal":
        value = lexeme == "WIN"
    else:
        expected("a number, string or WIN/FAIL")
    next_token()
    return value


# start here
# run the lexer, then the parser (raises ParseError / LexError); fills the symbol table if given
def parse(source_code, symbol_table=None):
    global tokens, current, symbols
    tokens = []
    current = 0
    symbols = symbol_table
    if symbols is not None:
        symbols.clear()

    list(lexer(source_code, tokens))  # running the lexer fills the `tokens` list
    parse_program()

if __name__ == "__main__":
    import sys
    from symbol_table import SymbolTable

    file_name = sys.argv[1] if len(sys.argv) > 1 else "sample.lol"
    with open(file_name, "r", encoding="utf-8") as source_file:
        source_code = source_file.read()

    try:
        table = SymbolTable()
        parse(source_code, table)
        print("Syntax OK\n\nSymbol table:")
        for row in table.get_all_variables_for_gui():
            print("  " + row["identifier"].ljust(10) + row["type"].ljust(8) + row["value"])
    except (LexError, ParseError) as error:
        print("Error:", error)