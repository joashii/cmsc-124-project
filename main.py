from nicegui import ui
from lexer import lexer, without_line_breaks, LexError


# 1. Define the upload handler
async def handle_upload(e):
    name = e.file.name
    if not name.endswith(('.txt', '.lol')):
        ui.notify('Please select a .txt or .lol file', type='warning')
        return
    try:
        file_content = await e.file.text()   # decodes as UTF-8 by default
        editor.set_value(file_content)
        ui.notify(f'Loaded: {name}', type='positive')
    except Exception as ex:
        ui.notify(f'Error reading file: {ex}', type='negative')


# Run the lexer on whatever is currently in the editor
def run_lexer():
    try:
        lexemes = without_line_breaks(lexer(editor.value))
    except LexError as err:
        lexeme_table.rows = []
        lexeme_table.update()
        ui.notify(f'Lexical error: {err}', type='negative')
        return

    lexeme_table.rows = [
        {'id': i, 'line': line, 'lexeme': lex, 'classification': kind}
        for i, (lex, kind, line) in enumerate(lexemes)
    ]
    lexeme_table.update()
    ui.notify(f'{len(lexemes)} lexemes found', type='positive')


# 5. Create the hidden uploader
uploader = ui.upload(auto_upload=True, on_upload=handle_upload).classes('hidden')

uploader.ignores_events_when_hidden = False  # Required to trigger pickFiles

with ui.header().classes('items-center justify-center'):
    ui.label('LOLCode Interpreter').classes('text-xl font-bold')

with ui.column().classes('w-full h-screen p-4 gap-4 overflow-hidden'):
    with ui.row().classes('w-full gap-4 flex-nowrap h-64'):
        # Column 1: Code Editor
        with ui.column().classes('w-2/5 border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Code Editor').classes('font-bold')

                with ui.row().classes('items-center gap-1'):
                    # Trigger the file explorer
                    ui.button(icon='folder_open', on_click=lambda: uploader.run_method('pickFiles')) \
                        .props('flat round color=white size=sm')
                    # Run the lexer
                    ui.button(icon='play_arrow', on_click=run_lexer) \
                        .props('flat round color=white size=sm')

            with ui.row().classes('w-full flex-grow overflow-hidden'):
                # The editor is safely initialized here
                editor = ui.codemirror('HAI 1.2\nVISIBLE "Hello"\nKTHXBYE', language='Text').classes('w-full h-full')

        # Column 2: Changed to w-1/3
        with ui.column().classes('w-2/5 border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Lexemes').classes('font-bold')
                ui.icon('code')
            with ui.column().classes('w-full flex-grow overflow-y-auto p-2'):
                lexeme_table = ui.table(
                    columns=[
                        {'name': 'line', 'label': 'Line', 'field': 'line', 'align': 'left'},
                        {'name': 'lexeme', 'label': 'Lexeme', 'field': 'lexeme', 'align': 'left'},
                        {'name': 'classification', 'label': 'Classification', 'field': 'classification', 'align': 'left'},
                    ],
                    rows=[],
                    row_key='id',
                ).props('dense flat').classes('w-full')

        # Column 3: Changed to w-1/3
        with ui.column().classes('w-1/5 border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Symbol Table').classes('font-bold')
                ui.icon('list')

            with ui.column().classes('w-full flex-grow overflow-y-auto p-2'):
                for i in range(50):
                    ui.label(f'Token {i}')

    # --- ROW 2: Console ---
    with ui.row().classes('w-full flex-grow gap-4 flex-nowrap'):
        # I assume you want this to be the console based on your PDF
        with ui.column().classes('w-full border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Console').classes('font-bold')
            with ui.column().classes('w-full flex-grow overflow-y-auto p-2'):
                ui.label('Output will appear here...')

ui.run()