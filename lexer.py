import re

def lexer(source):
    source = clean_code(source)
    print(source)

def clean_code(source):
    # remove comments
    mc_pattern = re.compile(r'^OBTW\s[\s\S]*?\sTLDR(?:\r?\n|$)', re.MULTILINE)
    sc_pattern = re.compile(r'BTW [^\n]*(?:\r?\n|$)')

    source = sc_pattern.sub('\n', source)
    source = mc_pattern.sub('', source)

    # remove multiple newline
    source = re.sub('\n+', '\n', source).strip()

    return source

with open("sample.lol", "r") as file:
    code = file.read()

lexer(code)