import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

CREATE_NO_WINDOW = 0x08000000

root = tk.Tk()
root.title("Dynamic PowerShell Script Runner")

entries = {}
params = []
ps1_path = ""

def parse_params(path):
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
        return []

    match = re.search(r'param\s*\((.*?)\)', text, re.DOTALL)
    if not match:
        return []

    param_block = match.group(1)
    result = []
    for line in param_block.splitlines():
        line = line.strip().rstrip(',')
        if not line:
            continue
        m = re.match(r'(?:\[[^\]]+\])?\s*\$(\w+)(?:\s*=\s*"(.*)")?', line)
        if m:
            name = m.group(1)
            default = m.group(2) if m.group(2) is not None else ""
            result.append((name, default))
    return result

def load_script():
    global ps1_path, params
    path = filedialog.askopenfilename(
        title="Выберите PowerShell скрипт",
        filetypes=[("PowerShell scripts", "*.ps1"), ("Все файлы", "*.*")]
    )
    if not path:
        return

    ps1_path = path
    params = parse_params(ps1_path)

    for widget in frame_params.winfo_children():
        widget.destroy()
    entries.clear()

    for name, default in params:
        tk.Label(frame_params, text=f"{name} (default: {default})").pack(anchor='w', padx=10)
        ent = tk.Entry(frame_params, width=50)
        ent.insert(0, default)
        ent.pack(padx=10, pady=2)
        entries[name] = ent

    lbl_script.config(text=f"Текущий скрипт: {ps1_path}")

def run_powershell_script():
    if not ps1_path:
        messagebox.showwarning("Внимание", "Сначала выберите PowerShell скрипт")
        return

    def task():
        btn_run.config(text="Запуск...", state='disabled')
        try:
            # Формируем команду PowerShell с установкой UTF-8
            command = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '{ps1_path}'"
            for name, _ in params:
                val = entries[name].get().strip()
                if val != "":
                    command += f" -{name} '{val}'"

            args = [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                command
            ]

            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=CREATE_NO_WINDOW
            )
            out, err = process.communicate()

            output_text.config(state='normal')
            output_text.insert(tk.END, "\n" + "="*60 + "\n")  # разделитель между запусками
            if out:
                output_text.insert(tk.END, out)
            if err:
                output_text.insert(tk.END, "\nОшибка:\n" + err)
            output_text.insert(tk.END, "\n")
            output_text.see(tk.END)
            output_text.config(state='disabled')
        finally:
            btn_run.config(text="Запустить скрипт", state='normal')

    threading.Thread(target=task, daemon=True).start()

btn_load = tk.Button(root, text="Выбрать PowerShell скрипт", command=load_script)
btn_load.pack(pady=10)

lbl_script = tk.Label(root, text="Скрипт не выбран")
lbl_script.pack()

frame_params = tk.Frame(root)
frame_params.pack()

btn_run = tk.Button(root, text="Запустить скрипт", command=run_powershell_script)
btn_run.pack(pady=10)

output_text = ScrolledText(root, width=80, height=20, state='disabled')
output_text.pack(padx=10, pady=10)

root.mainloop()
