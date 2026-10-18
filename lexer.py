import re

TOKEN_PATTERN = [
    # literals
    ('YARN Literal', r'^"[^"\n\a]*"'),
    ('NUMBAR Literal', r'^-?[0-9]+\.[0-9]+'),
    ('NUMBR Literal', r'^-?[0-9]+'),
    ('TROOF Literal', r'^(?:WIN|FAIL)\b'),
    ('TYPE Literal', r'^(?:NUMBR|NUMBAR|YARN|TROOF|BUKKIT|NOOB)\b'),

    # comments
    ('Single Comment', r'^BTW\b[^\n]*(?:\r?\n|$)'),
    ('Multi Comment', r'^OBTW\s[\s\S]*?\sTLDR(?:\r?\n|$)'),

    # keywords
    ('HAI', r'^HAI\b'),
    ('KTHXBYE', r'^KTHXBYE\b'),
    ('WAZZUP', r'^WAZZUP\b'),
    ('BUHBYE', r'^BUHBYE\b'),
    ('I HAS A', r'^I HAS A\b'),
    ('ITZ', r'^ITZ\b'),
    ('R', r'^R\b'),
    ('SUM OF', r'^SUM OF\b'),
    ('DIFF OF', r'^DIFF OF\b'),
    ('PRODUKT OF', r'^PRODUKT OF\b'),
    ('QUOSHUNT OF', r'^QUOSHUNT OF\b'),
    ('MOD OF', r'^MOD OF\b'),
    ('BIGGR OF', r'^BIGGR OF\b'),
    ('SMALLR OF', r'^SMALLR OF\b'),
    ('BOTH OF', r'^BOTH OF\b'),
    ('EITHER OF', r'^EITHER OF\b'),
    ('WON OF', r'^WON OF\b'),
    ('NOT', r'^NOT\b'),
    ('ANY OF', r'^ANY OF\b'),
    ('ALL OF', r'^ALL OF\b'),
    ('BOTH SAEM', r'^BOTH SAEM\b'),
    ('DIFFRINT', r'^DIFFRINT\b'),
    ('SMOOSH', r'^SMOOSH\b'),
    ('MAEK', r'^MAEK\b'),
    ('A', r'^A\b'),
    ('IS NOW A', r'^IS NOW A\b'),
    ('VISIBLE', r'^VISIBLE\b'),
    ('GIMMEH', r'^GIMMEH\b'),
    ('O RLY?', r'^O RLY\?'),
    ('YA RLY', r'^YA RLY\b'),
    ('MEBBE', r'^MEBBE\b'),
    ('NO WAI', r'^NO WAI\b'),
    ('OIC', r'^OIC\b'),
    ('WTF?', r'^WTF\?'),
    ('OMG', r'^OMG\b'),
    ('OMGWTF', r'^OMGWTF\b'),
    ('IM IN YR', r'^IM IN YR\b'),
    ('UPPIN', r'^UPPIN\b'),
    ('NERFIN', r'^NERFIN\b'),
    ('YR', r'^YR\b'),
    ('TIL', r'^TIL\b'),
    ('WILE', r'^WILE\b'),
    ('IM OUTTA YR', r'^IM OUTTA YR\b'),
    ('HOW IZ I', r'^HOW IZ I\b'),
    ('IF U SAY SO', r'^IF U SAY SO\b'),
    ('GTFO', r'^GTFO\b'),
    ('FOUND YR', r'^FOUND YR\b'),
    ('I IZ', r'^I IZ\b'),
    ('MKAY', r'^MKAY\b'),
    ('AN', r'^AN\b'),
    ('PLUS' , r'^\+'),
    ('BANG', r'^!'),

    # identifiers
    ('IDENTIFIER', r'^[A-Za-z][A-Za-z0-9_]*'),
]

def lexer(source):
    lexemes = [] # to store the tokens
    remaining = source # loop through the source code string

    while remaining:
        remaining = remaining.lstrip(' \t\r\n,') # remove leading whitespace and line delimiter

        for token, pattern in TOKEN_PATTERN: # iterate through token_pattern
            match = re.match(pattern, remaining)

            if match:
                remaining = remaining[match.end():] # remove the matched substring
                if token == "Single Comment" or token == "Multi Comment": break # disregard comments

                token_lex = match.group() # lexeme = matched string
                token_type = token # corresponding type

                lexemes.append((token_lex, token_type)) # append the lexeme
                break

    return lexemes

with open("sample.lol", "r") as file:
    code = file.read()

lexemes = lexer(code)

for token_lex, token_type in lexemes:
    print(f"{token_lex:50}\t{token_type:<10}")
