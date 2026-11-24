"""Symbol table backend for the LOLCODE interpreter.

It stores every variable together with its current value. The TYPE is not stored,
it is worked out from the value, so the two can never disagree:

    int -> NUMBR     float -> NUMBAR     str -> YARN     bool -> TROOF     None -> NOOB

The table is independent of the GUI and of the lexer, so the interpreter, the
semantic analyzer and the GUI can all share it:

    * interpreter  : declare() / assign() / get() / set_it() / push_scope() / pop_scope()
    * GUI          : get_all_variables_for_gui(), plus the on_change hook
    * lexer output : load_from_lexemes() fills the table from the token list, so the
                     table can be shown before (or without) running the program
"""

class SymbolTableError(Exception):
    """Raised when a variable is used before it is declared."""
    pass

# Module-level state
# a stack of scopes: [0] is the global scope, each function call pushes a new one
scopes = [{"IT": None}]
# optional hook: called with no arguments after every change, so the GUI can refresh
# (the project specification allows updating the table every time a value changes)
on_change = None

def notify_change():
    """Calls the optional GUI refresh callback if one is registered."""
    if callable(on_change):
        on_change()

# ------------------------------------------------------------------ value helpers
# (kept at module level so the interpreter can reuse them)

def type_name(value):
    """The LOLCODE type of a Python value. bool is checked before int (True is an int in Python)."""
    if value is None: return "NOOB"
    if isinstance(value, bool): return "TROOF"
    if isinstance(value, int): return "NUMBR"
    if isinstance(value, float): return "NUMBAR"
    if isinstance(value, str): return "YARN"
    raise SymbolTableError(f"unsupported value {value!r}")

def format_value(value):
    """How a value is shown in the GUI table."""
    if value is None: return "NOOB"
    if isinstance(value, bool): return "WIN" if value else "FAIL"
    return str(value)

# ------------------------------------------------------------------ variables
def declare(name, value=None):
    """I HAS A name [ITZ value]. Declaring a name again resets it."""
    scopes[-1][name] = value
    notify_change()

def assign(name, value):
    """name R value. The variable must already be declared."""
    scope = scopes[-1]
    if name not in scope:
        raise SymbolTableError(f"variable {name} is not declared")
    scope[name] = value
    notify_change()

def get(name):
    """Returns the current value of `name`, or raises SymbolTableError if undeclared."""
    scope = scopes[-1]
    if name not in scope:
        raise SymbolTableError(f"variable {name} is not declared")
    return scope[name]

def exists(name): return name in scopes[-1]
def type_of(name): return type_name(get(name))
def names(): return list(scopes[-1])

# IT is the implicit variable. It always exists and is set by bare expressions.
def set_it(value):
    scopes[-1]["IT"] = value
    notify_change()

def get_it(): return scopes[-1]["IT"]

# ------------------------------------------------------------------ scopes (functions)
def push_scope(variables=None):
    """Start a function call. Functions only see their own variables (plus their own IT)."""
    scope = {"IT": None}
    if variables:
        scope.update(variables)  # the parameters
    scopes.append(scope)
    notify_change()

def pop_scope():
    """End a function call."""
    if len(scopes) == 1:
        raise SymbolTableError("cannot leave the global scope")
    scopes.pop()
    notify_change()

def depth():
    """0 at the top level, 1 inside a function, 2 inside a function called by a function, ..."""
    return len(scopes) - 1

# ------------------------------------------------------------------ reset
def clear():
    """Forget everything (done at the start of every run)."""
    global scopes
    scopes = [{"IT": None}]
    notify_change()

# ------------------------------------------------------------------ GUI
def get_all_variables_for_gui():
    """Rows for the GUI table (the variables of the scope that is running right now)."""
    return [
        {"identifier": name, "type": type_name(value), "value": format_value(value)}
        for name, value in scopes[-1].items()
    ]

# ------------------------------------------------------------------ lexer connection
def load_from_lexemes(lexemes):
    """Fill the table from lexer output: every global `I HAS A name` becomes a NOOB variable.

    Works with the full token list or the one from without_line_breaks(). Variables declared
    inside a function (between HOW IZ I and IF U SAY SO) are local, so they are skipped.
    Values stay NOOB until the interpreter assigns them.
    """
    clear()
    inside_function = False
    previous = ""
    for lexeme, kind, _ in lexemes:
        if kind == "Function Delimiter":
            inside_function = (lexeme == "HOW IZ I")
        elif previous == "I HAS A" and kind == "Variable Identifier" and not inside_function:
            if lexeme not in scopes[-1]:
                scopes[-1][lexeme] = None
        previous = lexeme if kind != "YARN Literal" else ""
    notify_change()

def from_source(source):
    """Convenience: lex a piece of code and populate the symbol table from it."""
    from lexer import lexer  # imported here so symbol_table.py works even without lexer.py

    lexemes = []
    for _ in lexer(source, lexemes):
        pass
    load_from_lexemes(lexemes)
    return get_all_variables_for_gui()