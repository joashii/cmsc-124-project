import re

# Error raised when the code has something the lexer does not understand.
class LexError(Exception):
    pass

# first pattern matched wins so ORDER matters (literals, keywords, identifiers)
TOKEN_PATTERN = [
    # literals
    ('YARN Literal', r'^"(?:[^"\n\t:]|:[)>O":])*"'),
    ('NUMBAR Literal', r'^-?[0-9]+\.[0-9]+(?![A-Za-z0-9_])'),
    ('NUMBR Literal', r'^-?[0-9]+(?![A-Za-z0-9_])'),
    ('TROOF Literal', r'^(?:WIN|FAIL)\b'),
    ('TYPE Literal', r'^(?:NUMBR|NUMBAR|YARN|TROOF|BUKKIT|NOOB)\b'),

    # comments
    ('Single Comment', r'^BTW\b[^\n]*'),
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

    # line breaks
    ('Line Break', r'^\n'),
    ('Soft Line Break', r'^,'),

    # identifiers
    ('Identifier', r'^[A-Za-z][A-Za-z0-9_]*'),
]

ESCAPE_DICT = {")": "\n", ">": "\t", "O": "\a", '"': '"', ":": ":"}

def lexer(source):
    lexemes = []
    remaining = source
    line = 1
    variables, functions, loops = set(), set(), set()

    while remaining:
        remaining = remaining.lstrip(' \t\r')
        if not remaining: break

        for token, pattern in TOKEN_PATTERN:
            match = re.match(pattern, remaining)
            if match:
                token_lex = match.group()
                remaining = remaining[match.end():]

                # comments
                if token in ("Single Comment", "Multi Comment"):
                    if token == "Multi Comment" and lexemes and lexemes[-1][1] != "Line Break":
                        raise LexError(f"Line {line}: OBTW must be on its own line")
                    line += token_lex.count("\n")
                    break

                # line breaks
                if token == "Line Break":
                    if lexemes and lexemes[-1][1] != "Line Break":
                        lexemes.append(("\\n", token, line))
                    line += 1
                    break

                # yarn literals
                if token == "YARN Literal":
                    text = re.sub(r':([)>O":])', lambda m: ESCAPE_DICT[m.group(1)], token_lex[1:-1])

                    lexemes.append(('"', "String Delimiter", line))
                    lexemes.append((text, token, line))
                    lexemes.append(('"', "String Delimiter", line))
                    break

                # identifiers
                if token == "Identifier":
                    if token_lex in ("OBTW", "TLDR"):
                        raise LexError(f"Line {line}: '{token_lex}' is not part of a complete comment block")

                    prev_token = lexemes[-1][0] if lexemes else ""
                    if prev_token in ("I HAS A", "YR"):
                        variables.add(token_lex)
                    elif prev_token in ("HOW IZ I", "I IZ"):
                        functions.add(token_lex)
                    elif prev_token == "IM IN YR":
                        loops.add(token_lex)

                    if token_lex == "IT" or token_lex in variables:
                        token = "Variable Identifier"
                    elif token_lex in functions:
                        token = "Function Identifier"
                    elif token_lex in loops:
                        token = "Loop Identifier"

                lexemes.append((token_lex, token, line)) # save token
                break
        else:
            # string error
            if remaining[0] == '"':
                current_line = remaining.split('\n', 1)[0]
                err_escape = re.search(r':([^)>O":])', current_line)
                
                if '\t' in current_line:
                    message = "a string cannot contain a raw tab"
                elif err_escape:
                    message = f"invalid escape ':{err_escape.group(1)}'"
                else:
                    message = "string is missing its closing quote"

                raise LexError(f"Line {line}: {message}")

            # identifier formatting error
            bad_format = re.match(r'-?[0-9]+(?:\.[0-9]+)?[A-Za-z0-9_]+', remaining)
            if bad_format:
                raise LexError(f"Line {line}: invalid identifier '{bad_format.group()}'")
            
            # general error
            raise LexError(f"Line {line}: unknown character '{remaining[0]}'")

    return lexemes

def without_line_breaks(lexemes):
    """Tokens for the GUI table. The parser needs the line breaks, people do not."""
    return [t for t in lexemes if t[1] not in ("Line Break", "Soft Line Break")]

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