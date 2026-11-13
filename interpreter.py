# Runs a LOLCODE program from its parse tree. Starter file: the TODO parts are not written yet.
# main.py calls run(tree, symbol_table, output, ask)
#   output(text, newline=True) prints in the Console, ask() waits for what the user types (GIMMEH)
# evaluate() from expressions.py gives the value of an expression.
# For a mistake while running, raise RunError(line, 'message')

import threading
from expressions import evaluate, to_troof, to_yarn, cast, same_value, node_line, RunError, RunStopped

# main.py sets this when the user presses Stop
stop_event = threading.Event()

table = None
output = None
ask = None
functions = {}  # function name -> its <func_def> node


# runs the whole program
def run(tree, symbol_table, output_function, ask_function):
    global table, output, ask
    table, output, ask = symbol_table, output_function, ask_function
    functions.clear()
    # TODO: save the functions, run the variable declarations, then run the statements
    pass


# runs every statement in a <statement_list>
def run_statements(statement_list):
    # TODO
    pass


# runs one statement: VISIBLE, GIMMEH, R, IS NOW A, a lone expression, GTFO, FOUND YR
def run_statement(statement):
    # TODO
    pass


# O RLY? ... OIC
def run_if(if_block):
    # TODO
    pass


# WTF? ... OIC
def run_switch(switch_block):
    # TODO
    pass


# IM IN YR ... IM OUTTA YR
def run_loop(loop_block):
    # TODO
    pass


# I IZ name ... MKAY (evaluate() calls this for every function call)
def call_function(name, values, line):
    # TODO
    pass