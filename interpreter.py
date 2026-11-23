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

# used to stop a loop or switch
class BreakSignal(Exception):
    pass


# used to return a value from a function
class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


def check_stop():
    if stop_event.is_set():
        raise RunStopped()


# runs the whole program
def run(tree, symbol_table, output_function, ask_function):
    global table, output, ask
    table, output, ask = symbol_table, output_function, ask_function
    functions.clear()

    # save functions defined before HAI
    outer = tree[1][0]

    for item in outer[1]:
        if item[0] == "<func_def>":
            name = item[1][1][1][0]
            functions[name] = item

    # save functions defined after KTHXBYE
    outer_end = tree[1][6]

    if outer_end[1]:
        outer = outer_end[1][1]

        for item in outer[1]:
            if item[0] == "<func_def>":
                name = item[1][1][1][0]
                functions[name] = item

    # run variable initializers
    body = tree[1][4]
    var_dec_block = body[1][0]

    if var_dec_block[1]:
        var_dec_list = var_dec_block[1][2]

        for declaration in var_dec_list[1]:
            if len(declaration[1]) == 4:
                name = declaration[1][1][1][0]
                value = evaluate(declaration[1][3], table, call_function)
                table.assign(name, value)

    # run the main program statements
    try:
        run_statements(body[1][1])
    except BreakSignal:
        raise RunError(node_line(tree), "GTFO used outside a loop or switch")
    except ReturnSignal:
        raise RunError(node_line(tree), "FOUND YR used outside a function")


# runs every statement in a <statement_list>
def run_statements(statement_list):
    for statement in statement_list[1]:
        check_stop()
        run_statement(statement)


# runs one statement: VISIBLE, GIMMEH, R, IS NOW A, a lone expression, GTFO, FOUND YR
def run_statement(statement):
    check_stop()
    
    if statement[0] == "<statement>":
            statement = statement[1][0]
    
    label = statement[0]
    data = statement[1]
    
    if label == "<output>":
        value = evaluate(data[1], table, call_function)
        text = to_yarn(value)
    
        output_list = data[2]
    
        while output_list[1]:
            value = evaluate(output_list[1][1], table, call_function)
            text += to_yarn(value)
            output_list = output_list[1][2]
    
        newline = not bool(data[3][1])
        output(text, newline)
    
    elif label == "<input>":
        name = data[1][1][0]
        value = ask()
        table.assign(name, value)
    
    elif label == "<assignment>":
        name = data[0][1][0]
        value = evaluate(data[2], table, call_function)
        table.assign(name, value)
    
    elif label == "<typecast>":
        name = data[0][1][0]
        type_name = data[2][1][0]
        value = cast(table.get(name), type_name)
        table.assign(name, value)
    
    elif label == "<if_block>":
        run_if(statement)
    
    elif label == "<switch_block>":
        run_switch(statement)
    
    elif label == "<loop_block>":
        run_loop(statement)
    
    elif label == "<break>":
        raise BreakSignal()
    
    elif label == "<return>":
        value = evaluate(data[1], table, call_function)
        raise ReturnSignal(value)
    
    elif label == "<top_expr>":
        value = evaluate(statement, table, call_function)
        table.set_it(value)
    
    else:
        raise RunError(node_line(statement), "Unknown statement")


# O RLY? ... OIC
def run_if(if_block):
    data = if_block[1]

    # run YA RLY when IT is WIN
    if to_troof(table.get_it()):
        run_statements(data[4])
        return

    # check MEBBE conditions
    elif_block = data[5]

    while elif_block[1]:
        elif_data = elif_block[1]
        condition = evaluate(elif_data[1], table, call_function)

        if to_troof(condition):
            run_statements(elif_data[3])
            return

        elif_block = elif_data[4]

    # run NO WAI if no condition matched
    else_block = data[6]

    if else_block[1]:
        run_statements(else_block[1][2])


# WTF? ... OIC
def run_switch(switch_block):
    data = switch_block[1]
    case_list = data[2][1]
    default_block = data[3]

    switch_value = table.get_it()
    matched_index = None

    # find the first case that matches IT
    for index, case in enumerate(case_list):
        case_value = evaluate(case[1][1], table, call_function)

        if same_value(switch_value, case_value):
            matched_index = index
            break

    # run OMGWTF if no case matches
    if matched_index is None:
        if default_block[1]:
            run_statements(default_block[1][2])
        return

    # run the matching case and following cases
    try:
        for case in case_list[matched_index:]:
            run_statements(case[1][3])

    except BreakSignal:
        pass


# IM IN YR ... IM OUTTA YR
def run_loop(loop_block):
    data = loop_block[1]

    loop_update = data[2][1]
    statements = data[4]

    operation = loop_update[0][1][0]
    variable = loop_update[2][1][0]
    condition_block = loop_update[3]

    condition_type = None
    condition = None

    if condition_block[1]:
        condition_type = condition_block[1][0][1][0]
        condition = condition_block[1][1]

    while True:
        check_stop()

        # check TIL or WILE before running statements
        if condition is not None:
            result = evaluate(condition, table, call_function)
            result = to_troof(result)

            if condition_type == "TIL" and result:
                break

            if condition_type == "WILE" and not result:
                break

        try:
            run_statements(statements)
        except BreakSignal:
            break

        # update the loop variable
        value = table.get(variable)

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise RunError(node_line(loop_block), "Loop variable must contain a number")

        if operation == "UPPIN":
            table.assign(variable, value + 1)
        else:
            table.assign(variable, value - 1)

def get_parameters(params_node):
    names = []

    if not params_node[1]:
        return names

    data = params_node[1]
    names.append(data[1][1][0])

    param_list = data[2]

    while param_list[1]:
        data = param_list[1]
        names.append(data[2][1][0])
        param_list = data[3]

    return names


# I IZ name ... MKAY (evaluate() calls this for every function call)
def call_function(name, values, line):
    if name not in functions:
        raise RunError(line, "Function '" + name + "' was not found")

    function = functions[name]
    data = function[1]

    parameters = get_parameters(data[2])

    if len(parameters) != len(values):
        raise RunError(line, "Incorrect number of arguments for function '" + name + "'")

    # create a new scope for the function
    table.push_scope()

    try:
        for index, parameter in enumerate(parameters):
            table.declare(parameter, values[index])

        try:
            run_statements(data[4])

        except ReturnSignal as result:
            return result.value

        except BreakSignal:
            return None

        return None

    finally:
        table.pop_scope()