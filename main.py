import asyncio
from nicegui import ui
from lexer import lexer, LexError

lexemes = []


# --- Placeholder backend functions ---
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


# Run the lexer on the current editor contents and populate the lexeme table
async def run_lexer():
    # Clear previous data
    lexemes.clear()
    lexeme_table.rows.clear()
    lexeme_table.update()

    try:
        # The teammate's updated lexer() signature appends to the 'lexemes' list
        for row_id, (lex, kind, line) in enumerate(lexer(editor.value, lexemes)):
            lexeme_table.add_row({'id': row_id, 'line': line, 'lexeme': lex, 'classification': kind})
            await asyncio.sleep(0.1)  # for visualization of identifying lexeme one at a time

        ui.notify(f'{len(lexeme_table.rows)} lexemes found', type='positive')
    except LexError as err:
        ui.notify(f'Lexical error: {err}', type='negative')


uploader = ui.upload(auto_upload=True, on_upload=handle_upload).classes('hidden')
uploader.ignores_events_when_hidden = False

# --- UI Setup ---
with ui.header().classes('items-center justify-center'):
    ui.label('LOLCode Interpreter').classes('text-xl font-bold')

# Main container fills the screen
with ui.column().classes('w-full h-[calc(100vh-60px)] p-4 overflow-hidden'):
    # --- MAIN SPLITTER: Left Column vs Right Column ---
    with ui.splitter(value=50, limits=[30, 70]).classes('w-full h-full') as main_splitter:
        # ==========================================
        # LEFT COLUMN
        # ==========================================
        with main_splitter.before:
            with ui.column().classes('w-full h-full min-w-0 pr-2'):
                # --- NESTED SPLITTER (Horizontal): Input vs Tabs ---
                with ui.splitter(horizontal=True, value=60, limits=[20, 80]).classes('w-full h-full') as left_splitter:
                    # 1. Input Tab Section
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

                    # 2. Merged Lexemes & Symbol Table Section
                    with left_splitter.after:
                        with ui.column().classes('w-full h-full pt-2 min-h-0'):
                            with ui.column().classes(
                                    'w-full h-full border-2 border-slate-300 rounded bg-gray-50 overflow-hidden'):
                                # --- TABBED HEADER ---
                                with ui.row().classes(
                                        'w-full bg-slate-800 text-white p-0 items-center justify-between rounded-t'):
                                    with ui.tabs().classes('text-white') as tables_tabs:
                                        ui.tab('Lexemes').classes('text-white')
                                        ui.tab('Symbols').classes('text-white')
                                    ui.icon('dataset').classes('mr-2')

                                # --- TAB PANELS (Content) ---
                                with ui.tab_panels(tables_tabs, value='Lexemes').classes(
                                        'w-full flex-grow overflow-hidden bg-white min-h-0'):
                                    # Panel 1: Lexemes
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

                                    # Panel 2: Symbols
                                    with ui.tab_panel('Symbols').classes('p-0 w-full h-full'):
                                        with ui.column().classes('w-full h-full overflow-y-auto p-2'):
                                            ui.label("Milestone 2").classes('text-black')

        # ==========================================
        # RIGHT COLUMN
        # ==========================================
        with main_splitter.after:
            with ui.column().classes('w-full h-full min-w-0 pl-2'):
                # --- NESTED SPLITTER: Console Output vs Parse Tree ---
                with ui.splitter(horizontal=True, value=50, limits=[20, 80]).classes('w-full h-full') as right_splitter:
                    # Row 1: Console Output
                    with right_splitter.before:
                        with ui.column().classes('w-full h-full pb-2 min-h-0'):
                            with ui.column().classes(
                                    'w-full h-full border-2 border-slate-300 rounded bg-gray-50 overflow-hidden'):
                                with ui.row().classes(
                                        'w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                                    ui.label('Console Output').classes('font-bold')
                                    ui.icon('terminal')
                                with ui.column().classes('w-full flex-grow overflow-y-auto p-2 min-h-0'):
                                    ui.label('Output will appear here...')

                    # Row 2: Parse Tree Output
                    with right_splitter.after:
                        with ui.column().classes('w-full h-full pt-2 min-h-0'):
                            with ui.column().classes(
                                    'w-full h-full border-2 border-slate-300 rounded bg-gray-50 overflow-hidden'):
                                with ui.row().classes(
                                        'w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                                    ui.label('Parse Tree Output').classes('font-bold')
                                    ui.icon('account_tree')
                                with ui.column().classes('w-full flex-grow overflow-y-auto p-2 min-h-0'):
                                    ui.label('Parse tree will appear here...')

ui.run()