import asyncio
from nicegui import ui
from lexer import lexer, LexError

lexemes = []


# Load uploaded file into the code editor
async def handle_upload(e):
    name = e.file.name
    if not name.endswith(('.txt', '.lol')):
        ui.notify('Please select a .txt or .lol file', type='warning')
        return
    try:
        file_content = await e.file.text()
        editor.set_value(file_content)
        ui.notify(f'Loaded: {name}', type='positive')
    except Exception as ex:
        ui.notify(f'Error reading file: {ex}', type='negative')


# Run lexer and populate lexeme table one row at a time
async def run_lexer():
    lexemes.clear()
    lexeme_table.rows.clear()
    lexeme_table.update()

    try:
        for row_id, (lex, kind, line) in enumerate(lexer(editor.value, lexemes)):
            lexeme_table.add_row({'id': row_id, 'line': line, 'lexeme': lex, 'classification': kind})
            await asyncio.sleep(0.1)

        ui.notify(f'{len(lexeme_table.rows)} lexemes found', type='positive')
    except LexError as err:
        ui.notify(f'Lexical error: {err}', type='negative')


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
                                        ui.button(icon='play_arrow', on_click=run_lexer).props(
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

                                    with ui.tab_panel('Symbols').classes('p-0 w-full h-full'):
                                        with ui.column().classes('w-full h-full overflow-y-auto p-2'):
                                            ui.label("Milestone 2").classes('text-black')

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

                    # Tab content
                    with ui.tab_panels(output_tabs, value='Console').classes(
                            'w-full flex-grow overflow-hidden bg-white min-h-0'):
                        with ui.tab_panel('Console').classes('p-0 w-full h-full'):
                            with ui.column().classes('w-full h-full overflow-y-auto p-2'):
                                ui.label('Output will appear here...')

                        with ui.tab_panel('Parse Tree').classes('p-0 w-full h-full'):
                            with ui.column().classes('w-full h-full overflow-y-auto p-2'):
                                ui.label('Parse tree will appear here...')

ui.run()