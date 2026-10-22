from nicegui import ui

def handle_upload(e):
    # Check the file extension (optional, but good practice)
    if not (e.name.endswith('.txt') or e.name.endswith('.lol')):
        ui.notify('Please select a .txt or .lol file', type='warning')
        return

    # Read the bytes, decode to UTF-8 string
    file_content = e.content.read().decode('utf-8')

    # Update the CodeMirror editor
    editor.value = file_content
    ui.notify(f'Loaded: {e.name}', type='positive')

uploader = ui.upload(auto_upload=True, on_upload=handle_upload).classes('hidden')

with ui.header().classes('items-center justify-center'):
    ui.label('LOLCode Interpreter').classes('text-xl font-bold')

# Added overflow-hidden here to prevent overall page scrolling
with ui.column().classes('w-full h-screen p-4 gap-4 overflow-hidden'):
    # --- ROW 1: Three Columns ---
    with ui.row().classes('w-full gap-4 flex-nowrap h-64'):
        # Column 1
        with ui.column().classes('w-1/3 border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Code Editor').classes('font-bold')

                # Trigger the file picker
                ui.button(icon='folder_open', on_click=lambda: uploader.run_method('pickFiles')) \
                    .props('flat round color=white size=sm')

            with ui.row().classes('w-full flex-grow overflow-hidden'):
                # The editor is defined at the top now, we just place it here
                editor = ui.codemirror('HAI 1.2\nVISIBLE "Hello"\nKTHXBYE', language='Text')

        # Column 2: Changed to w-1/3
        with ui.column().classes('w-1/3 border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Lexemes').classes('font-bold')
                ui.icon('code')
            with ui.column().classes('w-full flex-grow overflow-y-auto p-2'):
                ui.label('Lexeme list goes here...')

        # Column 3: Changed to w-1/3
        with ui.column().classes('w-1/3 border-2 border-slate-300 h-full rounded bg-gray-50 overflow-hidden'):
            with ui.row().classes('w-full bg-slate-800 text-white p-2 items-center justify-between rounded-t'):
                ui.label('Tokens').classes('font-bold')
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