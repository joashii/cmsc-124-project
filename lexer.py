import re


# Error raised when the code has something the lexer does not understand.
class LexError(Exception):
    pass


# Each entry is (classification, regex). The first pattern that matches wins,
# so the ORDER matters (literals first, identifiers last).
# \b means "end of word", so WINNER is an identifier and not the keyword WIN.
TOKEN_PATTERN = [
    # literals
    # a string is matched whole here and split into 3 tokens later in lexer()
    ('YARN Literal', r'^"[^"\n\a]*"'),
    # numbers must not be followed by a letter or digit (12abc is an error)
    ('NUMBAR Literal', r'^-?[0-9]+\.[0-9]+(?![A-Za-z0-9_])'),
    ('NUMBR Literal', r'^-?[0-9]+(?![A-Za-z0-9_])'),
    ('TROOF Literal', r'^(?:WIN|FAIL)\b'),
    ('TYPE Literal', r'^(?:NUMBR|NUMBAR|YARN|TROOF|BUKKIT|NOOB)\b'),

    # comments (the newline after a comment is NOT part of it, it becomes a Line Break)
    ('Single Comment', r'^BTW\b[^\n]*'),
    # OBTW ... TLDR, where TLDR must be alone on its own line
    ('Multi Comment', r'^OBTW\b[\s\S]*?\n[ \t]*TLDR[ \t]*(?=\r?\n|$)'),

    # keywords
    ('Code Delimiter', r'^HAI\b'),
    ('Code Delimiter', r'^KTHXBYE\b'),
    ('Variable Declaration Delimiter', r'^WAZZUP\b'),
    ('Variable Declaration Delimiter', r'^BUHBYE\b'),
    ('Variable Declaration', r'^I HAS A\b'),
    ('Variable Initialization', r'^ITZ\b'),
    ('Assignment Operator', r'^R\b'),
    ('Arithmetic Operation', r'^SUM OF\b'),
    ('Arithmetic Operation', r'^DIFF OF\b'),
    ('Arithmetic Operation', r'^PRODUKT OF\b'),
    ('Arithmetic Operation', r'^QUOSHUNT OF\b'),
    ('Arithmetic Operation', r'^MOD OF\b'),
    ('Arithmetic Operation', r'^BIGGR OF\b'),
    ('Arithmetic Operation', r'^SMALLR OF\b'),
    ('Boolean Operation', r'^BOTH OF\b'),
    ('Boolean Operation', r'^EITHER OF\b'),
    ('Boolean Operation', r'^WON OF\b'),
    ('Boolean Operation', r'^NOT\b'),
    ('Boolean Operation', r'^ANY OF\b'),
    ('Boolean Operation', r'^ALL OF\b'),
    ('Comparison Operation', r'^BOTH SAEM\b'),
    ('Comparison Operation', r'^DIFFRINT\b'),
    ('Concatenation Operation', r'^SMOOSH\b'),
    ('Typecast Operation', r'^MAEK\b'),
    ('Typecast Keyword', r'^A\b'),
    ('Typecast Operation', r'^IS NOW A\b'),
    ('Output Keyword', r'^VISIBLE\b'),
    ('Input Keyword', r'^GIMMEH\b'),
    ('If-Else Keyword', r'^O RLY\?'),
    ('If-Else Keyword', r'^YA RLY\b'),
    ('If-Else Keyword', r'^MEBBE\b'),
    ('If-Else Keyword', r'^NO WAI\b'),
    ('Conditional Delimiter', r'^OIC\b'),
    ('Switch-Case Keyword', r'^WTF\?'),
    ('Switch-Case Keyword', r'^OMG\b'),
    ('Switch-Case Keyword', r'^OMGWTF\b'),
    ('Loop Delimiter', r'^IM IN YR\b'),
    ('Loop Operation', r'^UPPIN\b'),
    ('Loop Operation', r'^NERFIN\b'),
    ('Parameter Keyword', r'^YR\b'),
    ('Loop Condition', r'^TIL\b'),
    ('Loop Condition', r'^WILE\b'),
    ('Loop Delimiter', r'^IM OUTTA YR\b'),
    ('Function Delimiter', r'^HOW IZ I\b'),
    ('Function Delimiter', r'^IF U SAY SO\b'),
    ('Break Keyword', r'^GTFO\b'),
    ('Return Keyword', r'^FOUND YR\b'),
    ('Function Call Keyword', r'^I IZ\b'),
    ('Argument List Terminator', r'^MKAY\b'),
    ('Operand Separator', r'^AN\b'),
    ('Output Separator', r'^\+'),
    ('Newline Suppressor', r'^!'),

    # line breaks (the parser needs them to know where a statement ends)
    ('Line Break', r'^\n'),
    ('Soft Line Break', r'^,'),

    # identifiers
    # TODO: decide if it is a variable, function or loop identifier
    ('Identifier', r'^[A-Za-z][A-Za-z0-9_]*'),
]


def lexer(source):
    lexemes = []  # to store the tokens: (lexeme, classification, line_number)
    remaining = source  # loop through the source code string
    line = 1  # the line we are currently on

    while remaining:
        remaining = remaining.lstrip(' \t\r')  # remove leading spaces and tabs (NOT newlines or commas)
        if not remaining:
            break  # only whitespace was left

        for token, pattern in TOKEN_PATTERN:  # iterate through token_pattern
            match = re.match(pattern, remaining)

            if match:
                token_lex = match.group()  # lexeme = matched string
                remaining = remaining[match.end():]  # remove the matched substring

                # comments are disregarded, but we still count the lines inside them
                if token == "Single Comment" or token == "Multi Comment":
                    # OBTW must be alone on its line, so nothing may come before it
                    if token == "Multi Comment" and lexemes and lexemes[-1][1] != "Line Break":
                        raise LexError(f"Line {line}: OBTW must be on its own line")
                    line += token_lex.count("\n")
                    break

                # a newline ends the line (but never keep two Line Breaks in a row, or one at the start)
                if token == "Line Break":
                    if lexemes and lexemes[-1][1] != "Line Break":
                        lexemes.append(("\\n", token, line))
                    line += 1
                    break

                # a string becomes 3 tokens: opening quote, the text, closing quote
                if token == "YARN Literal":
                    lexemes.append(('"', "String Delimiter", line))
                    lexemes.append((token_lex[1:-1], token, line))  # the text can be empty
                    lexemes.append(('"', "String Delimiter", line))
                    break

                # an OBTW or TLDR that is not part of a full comment looks like an identifier
                if token == "Identifier" and token_lex in ("OBTW", "TLDR"):
                    raise LexError(f"Line {line}: {token_lex} is not part of a complete OBTW ... TLDR comment")

                lexemes.append((token_lex, token, line))  # append the lexeme
                break
        else:
            # no pattern matched (the old code looped forever here), so report the error
            if remaining[0] == '"':
                raise LexError(f"Line {line}: string is missing its closing quote")
            raise LexError(f"Line {line}: unknown character '{remaining[0]}'")

    return lexemes


def without_line_breaks(lexemes):
    """Tokens for the GUI table. The parser needs the line breaks, people do not."""
    return [t for t in lexemes if t[1] not in ("Line Break", "Soft Line Break")]


# This only runs with "python lexer.py sample.lol", not when another file imports lexer.
if __name__ == "__main__":
    import sys

    file_name = sys.argv[1] if len(sys.argv) > 1 else "sample.lol"
    with open(file_name, "r", encoding="utf-8") as file:
        code = file.read()

    try:
        for token_lex, token_type, line in without_line_breaks(lexer(code)):
            print(f"{line:>4}  {token_lex:50}\t{token_type:<10}")
    except LexError as error:
        print("Lexical error:", error)
