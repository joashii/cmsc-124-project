# Works out the value of an expression from the parse tree.
# Example: the tree of  SUM OF x AN 2  becomes the number 7 when x is 5.

import math
import re
from symbol_table import SymbolTableError

DECIMALS = 2  # how many decimals a NUMBAR shows when it is printed or joined into a string

INT_TEXT = re.compile(r'-?\d+')
FLOAT_TEXT = re.compile(r'-?\d+\.\d+')


# an error that happens while the program is running (not while it is being read)
class RunError(Exception):
    def __init__(self, line, message):
        super().__init__(f'Line {line}: {message}')
        self.line = line
        self.message = message


# raised when the user presses Stop
class RunStopped(Exception):
    pass


# looking inside the parse tree

# a token looks like [kind, (text, line)], a rule looks like [label, [children]]
def is_token(node):
    return isinstance(node[1], tuple)


# the line of the first token inside a node (0 if there is none)
def node_line(node):
    if is_token(node):
        return node[1][1]
    if node[1]:
        return node_line(node[1][0])
    return 0


# <expr_list> is  expr AN expr AN expr ...  Gives back the list of <expr> nodes
def list_items(node):
    items = []
    while node:
        items.append(node[1][0])
        node = node[1][2] if len(node[1]) == 3 else None
    return items


# <call_args> is  YR expr AN YR expr ...  Gives back the list of <expr> nodes
def call_arguments(node):
    items = []
    while node[1]:  # an empty node means there are no more arguments
        for child in node[1]:
            if child[0] == '<expr>':
                items.append(child)
        node = node[1][-1]  # the next <arg_list> is always the last child
    return items


# changing a value into another type

# NOOB, 0, 0.0, "" and FAIL count as FAIL. Everything else is WIN
def to_troof(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value != ''
    return bool(value)


# a number we can do math with. A YARN has to look like a number, like "12" or "3.5"
def to_number(value, line):
    if value is None:
        raise RunError(line, 'cannot use a NOOB (a variable with no value) as a number')
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return value
    if INT_TEXT.fullmatch(value):
        return int(value)
    if FLOAT_TEXT.fullmatch(value):
        return float(value)
    raise RunError(line, f'cannot turn "{value}" into a number')


# the text of a value, the way VISIBLE and SMOOSH show it
def to_yarn(value, line):
    if value is None:
        raise RunError(line, 'cannot use a NOOB (a variable with no value) as text')
    if isinstance(value, bool):
        return 'WIN' if value else 'FAIL'
    if isinstance(value, float):
        # cut the decimals off (not rounded). Going through text keeps 1.15 from becoming 1.14
        whole, dot, decimals = f'{value:.10f}'.partition('.')
        text = whole + '.' + decimals[:DECIMALS]
        return text.lstrip('-') if float(text) == 0 else text
    return str(value)


# MAEK and IS NOW A: change a value to another type on purpose
def cast(value, type_word, line):
    if type_word == 'NUMBR':
        return int(0 if value is None else to_number(value, line))  # a NUMBAR is cut, not rounded
    if type_word == 'NUMBAR':
        return float(0 if value is None else to_number(value, line))
    if type_word == 'YARN':
        return '' if value is None else to_yarn(value, line)
    if type_word == 'TROOF':
        return to_troof(value)
    if type_word == 'NOOB':
        return None
    raise RunError(line, f'{type_word} is not supported')


# BOTH SAEM: same type and same value. 1 and 1.0 count as the same, "1" and 1 do not, and WIN is not 1
def same_value(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return isinstance(a, str) and isinstance(b, str) and a == b
    return a == b


# the math

def do_math(op, a, b, line):
    if op == 'SUM OF':
        return a + b
    if op == 'DIFF OF':
        return a - b
    if op == 'PRODUKT OF':
        return a * b
    if op == 'BIGGR OF':
        return max(a, b)
    if op == 'SMALLR OF':
        return min(a, b)

    # QUOSHUNT OF and MOD OF
    if b == 0:
        raise RunError(line, 'cannot divide by zero')
    if isinstance(a, float) or isinstance(b, float):
        return a / b if op == 'QUOSHUNT OF' else math.fmod(a, b)
    quotient = abs(a) // abs(b)  # whole numbers: cut toward zero, like -7 / 2 = -3
    if (a < 0) != (b < 0):
        quotient = -quotient
    return quotient if op == 'QUOSHUNT OF' else a - b * quotient


# the main function

# call_function(name, values, line) runs a LOLCODE function and gives back its value.
# interpreter.py provides it. Without it, a function call is an error.
def evaluate(node, table, call_function=None):
    label, data = node

    # <top_expr> and <expr> only hold one child, so look inside
    if label in ('<top_expr>', '<expr>'):
        return evaluate(data[0], table, call_function)

    # a single token can only be a variable here
    if is_token(node):
        name, line = data
        try:
            return table.get(name)
        except SymbolTableError:
            raise RunError(line, f'variable {name} is not declared')

    if label == '<literal>':
        kind, (text, line) = data[0]
        if kind == 'NUMBR Literal':
            return int(text)
        if kind == 'NUMBAR Literal':
            return float(text)
        if kind == 'TROOF Literal':
            return text == 'WIN'
        return data[1][1][0]  # a string comes as  "  text  "

    if label == '<arithmetic_expr>':  # [operator, expr, AN, expr]
        op, line = data[0][1]
        a = to_number(evaluate(data[1], table, call_function), line)
        b = to_number(evaluate(data[3], table, call_function), line)
        result = do_math(op, a, b, line)
        if isinstance(a, float) or isinstance(b, float):
            result = float(result)  # one NUMBAR makes the answer a NUMBAR
        return result

    if label == '<boolean_expr>':  # NOT expr   or   [operator, expr, AN, expr]
        op, line = data[0][1]
        a = to_troof(evaluate(data[1], table, call_function))
        if op == 'NOT':
            return not a
        b = to_troof(evaluate(data[3], table, call_function))
        if op == 'BOTH OF':
            return a and b
        if op == 'EITHER OF':
            return a or b
        return a != b  # WON OF

    if label == '<comparison_expr>':  # [operator, expr, AN, expr]
        op, line = data[0][1]
        same = same_value(evaluate(data[1], table, call_function), evaluate(data[3], table, call_function))
        return same if op == 'BOTH SAEM' else not same

    if label == '<concat_expr>':  # [SMOOSH, expr_list]
        line = node_line(node)
        text = ''
        for item in list_items(data[1]):
            text += to_yarn(evaluate(item, table, call_function), line)
        return text

    if label in ('<all_expr>', '<any_expr>'):  # [ALL OF or ANY OF, expr_list, MKAY]
        wanted = label == '<any_expr>'  # ANY OF is done as soon as one is WIN, ALL OF as soon as one is FAIL
        for item in list_items(data[1]):
            if to_troof(evaluate(item, table, call_function)) == wanted:
                return wanted
        return not wanted

    if label == '<cast_expr>':  # [MAEK, expr, A, type]  or  [MAEK, expr, type]
        line = node_line(node)
        return cast(evaluate(data[1], table, call_function), data[-1][1][0], line)

    if label == '<func_call>':  # [I IZ, name, call_args, MKAY]
        name, line = data[1][1]
        if call_function is None:
            raise RunError(line, 'functions cannot be called here')
        values = [evaluate(arg, table, call_function) for arg in call_arguments(data[2])]
        return call_function(name, values, line)

    raise RunError(node_line(node), f'cannot work out {label}')
