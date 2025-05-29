import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

CREATE_NO_WINDOW = 0x08000000  # Windows only; можно удалить на Linux

root = tk.Tk()
root.title("Dynamic Bash Script Runner")

entries = {}
params = []
sh_path = ""

# Пытаемся распарсить строку вида: # PARAMS: name="val" age="val"
def parse_params(path):
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
        return []

    match = re.search(r'#\s*PARAMS:\s*(.*)', text)
    if not match:
        return []

    param_str = match.group(1)
    result = []
    for m in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', param_str):
        name, default = m.group(1), m.group(2)
        result.append((name, default))
    return result

def load_script():
    global sh_path, params
    path = filedialog.askopenfilename(
        title="Выберите Bash скрипт",
        filetypes=[("Shell scripts", "*.sh"), ("Все файлы", "*.*")]
    )
    if not path:
        return

    sh_path = path
    params = parse_params(sh_path)

    for widget in frame_params.winfo_children():
        widget.destroy()
    entries.clear()

    for name, default in params:
        tk.Label(frame_params, text=f"{name} (default: {default})").pack(anchor='w', padx=10)
        ent = tk.Entry(frame_params, width=50)
        ent.insert(0, default)
        ent.pack(padx=10, pady=2)
        entries[name] = ent

    lbl_script.config(text=f"Текущий скрипт: {sh_path}")

def run_bash_script():
    if not sh_path:
        messagebox.showwarning("Внимание", "Сначала выберите .sh скрипт")
        return

    def task():
        btn_run.config(text="Запуск...", state='disabled')
        try:
            args = [sh_path]
            for name, _ in params:
                val = entries[name].get().strip()
                if val != "":
                    args.append(val)
            bash_path = r"C:\Program Files\Git\bin\bash.exe"
            process = subprocess.Popen(
                [bash_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=CREATE_NO_WINDOW
            )
            out, err = process.communicate()

            output_text.config(state='normal')
            output_text.insert(tk.END, "\n" + "="*60 + "\n")
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

btn_load = tk.Button(root, text="Выбрать Bash скрипт", command=load_script)
btn_load.pack(pady=10)

lbl_script = tk.Label(root, text="Скрипт не выбран")
lbl_script.pack()

frame_params = tk.Frame(root)
frame_params.pack()

btn_run = tk.Button(root, text="Запустить скрипт", command=run_bash_script)
btn_run.pack(pady=10)

output_text = ScrolledText(root, width=80, height=20, state='disabled')
output_text.pack(padx=10, pady=10)

root.mainloop()
