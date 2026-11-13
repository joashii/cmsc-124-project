import asyncio
import contextlib
import io
import queue
import threading

from nicegui import ui
from lexer import lexer, LexError
from parser import parse, ParseError, print_tree
from symbol_table import SymbolTable
import interpreter
from expressions import RunError, RunStopped

lexemes = []
symbol_table = SymbolTable()
state = {'running': False,   # stops a second click from starting a run while one is still going
         'answer': None,     # waits for what the user types when the program uses GIMMEH
         'symbols_changed': False}  # the program changed a variable, the Symbols tab needs a refresh

LEX_BATCH = 25     # tokens added to the Lexemes table at a time
LEX_DELAY = 0.01   # pause between batches (the visual effect), was 0.05 PER TOKEN

# the Parse Tree needs a monospace font or the branch lines (|-- and +--) do not line up
MONO_STYLE = ('white-space: pre; font-size: 0.8rem; line-height: 1.35; '
              'font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "DejaVu Sans Mono", "Courier New", monospace;')


# Load uploaded file into the code editor
async def handle_upload(e):
    name = e.file.name
    if not name.endswith(('.txt', '.lol')):
        ui.notify('Please select a .txt or .lol file', type='warning')
        return
    try:
        file_content = (await e.file.text()).replace('\r\n', '\n')  # .lol files from Windows use CRLF
        editor.set_value(file_content)
        ui.notify(f'Loaded: {name}', type='positive')
    except Exception as ex:
        ui.notify(f'Error reading file: {ex}', type='negative')


# Update the Symbol Table UI
def update_symbol_table_ui():
    symbol_table_ui.rows = symbol_table.get_all_variables_for_gui()
    symbol_table_ui.update()


# Add rows to the Lexemes table
def add_lexeme_rows(rows):
    lexeme_table.rows.extend(rows)
    lexeme_table.update()


# writes one line in the Console. 'ok' makes it green, 'error' red, 'out' is what the program prints
CONSOLE_COLORS = {'info': 'text-slate-600', 'ok': 'text-green-700', 'error': 'text-red-600', 'out': 'text-slate-900'}


def console_log(text, kind='info'):
    console_output.push(text, classes=CONSOLE_COLORS[kind])


# Turn the parse tree into the text shown in the Parse Tree tab
def tree_to_text(tree):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):  # print_tree prints, so capture it
        print_tree(tree)
    return buffer.getvalue()


# GIMMEH: show the input box, wait until the user presses Enter, give back what they typed
async def read_line():
    output_tabs.set_value('Console')  # the box lives in the Console tab, so make sure it is showing
    state['answer'] = asyncio.get_running_loop().create_future()
    input_box.value = ''
    input_row.set_visibility(True)
    input_box.run_method('focus')
    typed = await state['answer']
    input_row.set_visibility(False)
    return typed  # None if the user pressed Stop instead


def submit_line():
    if state['answer'] and not state['answer'].done():
        state['answer'].set_result(input_box.value)


def stop_program():
    interpreter.stop_event.set()
    if state['answer'] and not state['answer'].done():  # let go of a GIMMEH that is waiting
        state['answer'].set_result(None)


# Runs the program in its own thread, so a GIMMEH can wait for the user without freezing the page.
# The thread and the page talk through two queues: `shown` (what to print) and `typed` (the answers)
async def run_program(tree):
    shown, typed = queue.Queue(), queue.Queue()
    line = ''  # text printed with ! waits here until the line is finished
    stop_ticks = 0

    def output(text, newline=True):  # the interpreter calls this to print
        if interpreter.stop_event.is_set():
            raise RunStopped()
        shown.put((text, newline))

    def ask():  # ...and this one for GIMMEH
        shown.put(None)  # None means "ask the user"
        answer = typed.get()  # waits here until the user types something
        if answer is None:
            raise RunStopped()
        return answer

    loop = asyncio.get_running_loop()
    finished = loop.create_future()  # done when the program's thread ends (or has an error)
    finished.add_done_callback(lambda f: f.cancelled() or f.exception())  # no warning if we gave up on it

    def work():  # this is the thread
        try:
            interpreter.run(tree, symbol_table, output, ask)
            loop.call_soon_threadsafe(finished.set_result, None)
        except Exception as err:  # RunError, RunStopped...: pass it to the page
            loop.call_soon_threadsafe(finished.set_exception, err)

    interpreter.stop_event.clear()
    symbol_table.on_change = lambda: state.update(symbols_changed=True)  # runs in the thread, so only a flag
    threading.Thread(target=work, daemon=True).start()  # daemon: it cannot keep the app from closing
    try:
        while not (finished.done() and shown.empty()):
            while not shown.empty():
                item = shown.get()
                if item is None:  # GIMMEH
                    answer = await read_line()
                    if answer is not None:
                        console_log(line + answer, 'out')  # what they typed goes after the text before it
                        line = ''
                    typed.put(answer)
                else:
                    line += item[0]
                    if item[1]:  # the line is finished
                        console_log(line or ' ', 'out')
                        line = ''

            if state['symbols_changed']:
                state['symbols_changed'] = False
                try:
                    update_symbol_table_ui()
                except RuntimeError:  # the thread changed the table at that exact moment, try next time
                    state['symbols_changed'] = True

            if interpreter.stop_event.is_set():
                stop_ticks += 1
                if stop_ticks > 40:  # about 2 seconds: the program is not listening to Stop, give up on it
                    raise RunStopped()
            await asyncio.sleep(0.05)
        await finished  # if the program ended with an error, it is raised here
    finally:
        symbol_table.on_change = None
        if line:
            console_log(line, 'out')
        input_row.set_visibility(False)
        update_symbol_table_ui()


# Run lexer, parser, and update all tabs
async def run_interpreter():
    if state['running']:
        ui.notify('Still running, please wait', type='warning')
        return
    state['running'] = True

    # 1. Clear previous state
    lexemes.clear()
    lexeme_table.rows = []
    lexeme_table.update()
    symbol_table.clear()
    update_symbol_table_ui()
    parse_tree_output.set_text('')
    console_output.clear()

    try:
        # 2. Lex the code. The ONLY input is what is in the code editor right now
        #    (a loaded file was copied into the editor by handle_upload, and any edits are included)
        source = editor.value
        console_log('Lexing...')
        batch = []
        try:
            for row_id, (lex, kind, line) in enumerate(lexer(source, lexemes)):
                batch.append({'id': row_id, 'line': line, 'lexeme': lex, 'classification': kind})
                if len(batch) >= LEX_BATCH:
                    add_lexeme_rows(batch)
                    batch = []
                    await asyncio.sleep(LEX_DELAY)  # visual delay
        finally:
            if batch:  # also show the tokens found before a lexical error
                add_lexeme_rows(batch)
        console_log(f'Lexing done: {len(lexeme_table.rows)} lexemes', 'ok')

        # 3. Parse the code. On success the parser fills the symbol table (WAZZUP block variables)
        console_log('Parsing...')
        tree = parse(lexemes, symbol_table)
        variables = [name for name in symbol_table.names() if name != 'IT']  # skip IT, it is always in the table
        console_log('Parsing done: the syntax is correct', 'ok')
        console_log('Variables: ' + (', '.join(variables) if variables else 'none'))

        # 4. Parse Tree tab
        parse_tree_output.set_text(tree_to_text(tree))
        ui.notify('Parsed successfully', type='positive')

        # 5. Run the program. What it prints shows up in the Console tab
        console_log('Running...')
        await run_program(tree)
        console_log('Program finished', 'ok')

    except LexError as err:
        parse_tree_output.set_text(f'Lexical error: {err}')
        console_log(f'Lexical error: {err}', 'error')
        ui.notify(f'Lexical error: {err}', type='negative')
    except ParseError as err:
        # the parser only fills the symbol table when the WHOLE program parses, so on a syntax error
        # fall back to the declarations found in the tokens (values stay NOOB until the code is fixed)
        symbol_table.load_from_lexemes(lexemes)
        parse_tree_output.set_text(f'Parse error: {err}')
        console_log(f'Parse error: {err}', 'error')
        ui.notify(f'Parse error: {err}', type='negative')
    except RunError as err:
        console_log(f'Run error: {err}', 'error')
        ui.notify(f'Run error: {err}', type='negative')
    except RunStopped:
        console_log('Program stopped', 'info')
    except Exception as err:
        parse_tree_output.set_text(f'Unexpected error: {err}')
        console_log(f'Unexpected error: {err}', 'error')
        ui.notify(f'Unexpected error: {err}', type='negative')
    finally:
        # 6. Symbol Table tab (always refreshed, even after an error)
        update_symbol_table_ui()
        state['running'] = False


uploader = ui.upload(auto_upload=True, on_upload=handle_upload).classes('hidden')
uploader.ignores_events_when_hidden = False

with ui.header().classes('items-center justify-center'):
    ui.label('LOLCode Interpreter').classes('text-xl font-bold')

with ui.column().classes('w-full h-[calc(100vh-60px)] p-4 overflow-hidden'):
    # Split screen into left and right columns
    with ui.splitter(value=50, limits=[30, 70]).classes('w-full h-full') as main_splitter:
        # Left column: Input and Tables
        with main_splitter.before:
            with ui.column().classes('w-full h-full min-w-0 pr-2'):
                # Split left column vertically
                with ui.splitter(horizontal=True, value=60, limits=[20, 80]).classes('w-full h-full') as left_splitter:
                    # Code editor
                    with left_splitter.before:
                        with ui.column().classes('w-full h-full pb-2 min-h-0'):
                            with ui.column().classes(
                                    'w-full h-full border-2 border-slate-300 rounded bg-gray-50 overflow-hidden'):
                                with ui.row().classes(
                                        'w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                                    ui.label('Input').classes('font-bold')
                                    with ui.row().classes('items-center gap-1'):
                                        ui.button(icon='folder_open',
                                                  on_click=lambda: uploader.run_method('pickFiles')).props(
                                            'flat round color=white size=sm')
                                        ui.button(icon='play_arrow', on_click=run_interpreter).props(
                                            'flat round color=white size=sm')
                                        ui.button(icon='stop', on_click=stop_program).props(
                                            'flat round color=white size=sm')
                                with ui.row().classes('w-full flex-grow overflow-hidden min-h-0'):
                                    editor = ui.codemirror('HAI 1.2\nVISIBLE "Hello"\nKTHXBYE',
                                                           language='Text').classes('w-full h-full')

                    # Tabbed Lexemes and Symbols
                    with left_splitter.after:
                        with ui.column().classes('w-full h-full pt-2 min-h-0'):
                            with ui.column().classes(
                                    'w-full h-full border-2 border-slate-300 rounded bg-gray-50 overflow-hidden'):
                                with ui.row().classes(
                                        'w-full bg-slate-800 text-white p-0 items-center justify-between rounded-t'):
                                    with ui.tabs().classes('text-white') as tables_tabs:
                                        ui.tab('Lexemes').classes('text-white')
                                        ui.tab('Symbols').classes('text-white')
                                    ui.icon('dataset').classes('mr-2')

                                with ui.tab_panels(tables_tabs, value='Lexemes').classes(
                                        'w-full flex-grow overflow-hidden bg-white min-h-0'):
                                    # Lexemes Panel
                                    with ui.tab_panel('Lexemes').classes('p-0 w-full h-full'):
                                        with ui.column().classes('w-full h-full overflow-y-auto'):
                                            lexeme_table = ui.table(
                                                columns=[
                                                    {'name': 'line', 'label': 'Line', 'field': 'line', 'align': 'left'},
                                                    {'name': 'lexeme', 'label': 'Lexeme', 'field': 'lexeme',
                                                     'align': 'left'},
                                                    {'name': 'classification', 'label': 'Classification',
                                                     'field': 'classification', 'align': 'left'},
                                                ],
                                                rows=[], row_key='id',
                                            ).props('dense flat').classes('w-full')

                                    # Symbols Panel
                                    with ui.tab_panel('Symbols').classes('p-0 w-full h-full'):
                                        with ui.column().classes('w-full h-full overflow-y-auto p-2'):
                                            symbol_table_ui = ui.table(
                                                columns=[
                                                    {'name': 'identifier', 'label': 'Identifier', 'field': 'identifier',
                                                     'align': 'left'},
                                                    {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                                                    {'name': 'value', 'label': 'Value', 'field': 'value',
                                                     'align': 'left'},
                                                ],
                                                rows=[], row_key='identifier',
                                            ).props('dense flat').classes('w-full')

        # Right column: Output and Tree
        with main_splitter.after:
            with ui.column().classes('w-full h-full min-w-0 pl-2'):
                # Single container for the tabbed output on the right
                with ui.column().classes('w-full h-full border-2 border-slate-300 rounded bg-gray-50 overflow-hidden'):
                    # Tab header
                    with ui.row().classes('w-full bg-slate-800 text-white p-0 items-center justify-between rounded-t'):
                        with ui.tabs().classes('text-white') as output_tabs:
                            ui.tab('Console').classes('text-white')
                            ui.tab('Parse Tree').classes('text-white')
                        ui.icon('output').classes('mr-2')

                    # Tab contents
                    with ui.tab_panels(output_tabs, value='Parse Tree').classes(
                            'w-full flex-grow overflow-hidden bg-white min-h-0'):
                        # Console Panel
                        with ui.tab_panel('Console').classes('p-0 w-full h-full'):
                            with ui.column().classes('w-full h-full no-wrap gap-0'):
                                # the messages go here, newest at the bottom
                                console_output = ui.log().classes('w-full flex-1 min-h-0 p-2').style(MONO_STYLE)
                                console_output.push('Press the play button to run the code.',
                                                    classes=CONSOLE_COLORS['info'])
                                # the box for GIMMEH. It only shows while the program waits for an answer
                                with ui.row().classes('w-full items-center no-wrap p-2') as input_row:
                                    input_box = ui.input(placeholder='Type here and press Enter').props(
                                        'dense outlined').classes('flex-1')
                                    input_box.on('keydown.enter', submit_line)
                                input_row.set_visibility(False)

                        # Parse Tree Panel
                        with ui.tab_panel('Parse Tree').classes('p-0 w-full h-full'):
                            with ui.column().classes('w-full h-full overflow-auto p-2 bg-slate-50'):
                                # a plain label with a monospace font keeps the tree exactly as printed
                                parse_tree_output = ui.label('').style(MONO_STYLE)

ui.run()