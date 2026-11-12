import asyncio
import contextlib
import io

from nicegui import ui
from lexer import lexer, LexError
from parser import parse, ParseError, print_tree
from symbol_table import SymbolTable

lexemes = []
symbol_table = SymbolTable()
state = {'running': False}   # stops a second click from starting a run while one is still going

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


# writes one line in the Console. 'ok' makes it green, 'error' makes it red
CONSOLE_COLORS = {'info': 'text-slate-600', 'ok': 'text-green-700', 'error': 'text-red-600'}


def console_log(text, kind='info'):
    console_output.push(text, classes=CONSOLE_COLORS[kind])


# Turn the parse tree into the text shown in the Parse Tree tab
def tree_to_text(tree):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):  # print_tree prints, so capture it
        print_tree(tree)
    return buffer.getvalue()


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
    except Exception as err:
        parse_tree_output.set_text(f'Unexpected error: {err}')
        console_log(f'Unexpected error: {err}', 'error')
        ui.notify(f'Unexpected error: {err}', type='negative')
    finally:
        # 5. Symbol Table tab (always refreshed, even after an error)
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
                            # the messages go here, newest at the bottom
                            console_output = ui.log().classes('w-full h-full p-2').style(MONO_STYLE)
                            console_output.push('Press the play button to run the code.', classes=CONSOLE_COLORS['info'])

                        # Parse Tree Panel
                        with ui.tab_panel('Parse Tree').classes('p-0 w-full h-full'):
                            with ui.column().classes('w-full h-full overflow-auto p-2 bg-slate-50'):
                                # a plain label with a monospace font keeps the tree exactly as printed
                                parse_tree_output = ui.label('').style(MONO_STYLE)

ui.run()