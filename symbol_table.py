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


# ------------------------------------------------------------------ value helpers
# (kept at module level so the interpreter can reuse them)

def type_name(value):
    """The LOLCODE type of a Python value. bool is checked before int (True is an int in Python)."""
    if value is None:
        return "NOOB"
    if isinstance(value, bool):
        return "TROOF"
    if isinstance(value, int):
        return "NUMBR"
    if isinstance(value, float):
        return "NUMBAR"
    if isinstance(value, str):
        return "YARN"
    raise SymbolTableError(f"unsupported value {value!r}")


def format_value(value):
    """How a value is shown in the GUI table."""
    if value is None:
        return "NOOB"
    if isinstance(value, bool):
        return "WIN" if value else "FAIL"
    return str(value)


class SymbolTable:
    def __init__(self):
        # a stack of scopes: [0] is the global scope, each function call pushes a new one
        self._scopes = [{"IT": None}]
        # optional hook: called with no arguments after every change, so the GUI can refresh
        # (the project specification allows updating the table every time a value changes)
        self.on_change = None

    # ---------------------------------------------------------------- internals
    @property
    def _current(self):
        return self._scopes[-1]

    def _changed(self):
        if self.on_change:
            self.on_change()

    # ---------------------------------------------------------------- variables
    def declare(self, name, value=None):
        """I HAS A name [ITZ value]. Declaring a name again resets it."""
        self._current[name] = value
        self._changed()

    def assign(self, name, value):
        """name R value. The variable must already be declared."""
        if name not in self._current:
            raise SymbolTableError(f"variable {name} is not declared")
        self._current[name] = value
        self._changed()

    def get(self, name):
        if name not in self._current:
            raise SymbolTableError(f"variable {name} is not declared")
        return self._current[name]

    def exists(self, name):
        return name in self._current

    def type_of(self, name):
        return type_name(self.get(name))

    def names(self):
        return list(self._current)

    # IT is the implicit variable. It always exists and is set by bare expressions.
    def set_it(self, value):
        self._current["IT"] = value
        self._changed()

    def get_it(self):
        return self._current["IT"]

    # ---------------------------------------------------------------- scopes (functions)
    def push_scope(self, variables=None):
        """Start a function call. Functions only see their own variables (plus their own IT)."""
        scope = {"IT": None}
        if variables:
            scope.update(variables)  # the parameters
        self._scopes.append(scope)
        self._changed()

    def pop_scope(self):
        """End a function call."""
        if len(self._scopes) == 1:
            raise SymbolTableError("cannot leave the global scope")
        self._scopes.pop()
        self._changed()

    @property
    def depth(self):
        """0 at the top level, 1 inside a function, 2 inside a function called by a function, ..."""
        return len(self._scopes) - 1

    # ---------------------------------------------------------------- reset
    def clear(self):
        """Forget everything (done at the start of every run)."""
        self._scopes = [{"IT": None}]
        self._changed()

    # ---------------------------------------------------------------- GUI
    def get_all_variables_for_gui(self):
        """Rows for the GUI table (the variables of the scope that is running right now)."""
        return [
            {"identifier": name, "type": type_name(value), "value": format_value(value)}
            for name, value in self._current.items()
        ]

    # ---------------------------------------------------------------- lexer connection
    def load_from_lexemes(self, lexemes):
        """Fill the table from lexer output: every global `I HAS A name` becomes a NOOB variable.

        Works with the full token list or the one from without_line_breaks(). Variables declared
        inside a function (between HOW IZ I and IF U SAY SO) are local, so they are skipped.
        Values stay NOOB until the interpreter assigns them.
        """
        self.clear()
        inside_function = False
        previous = ""
        for lexeme, kind, _line in lexemes:
            if kind == "Function Delimiter":
                inside_function = (lexeme == "HOW IZ I")
            elif previous == "I HAS A" and kind == "Variable Identifier" and not inside_function:
                if lexeme not in self._current:
                    self._current[lexeme] = None
            previous = lexeme if kind != "YARN Literal" else ""
        self._changed()


def from_source(source):
    """Convenience: lex a piece of code and build the symbol table from it."""
    from lexer import lexer  # imported here so symbol_table.py works even without lexer.py

    table = SymbolTable()
    table.load_from_lexemes(lexer(source))
    return table