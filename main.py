import tkinter as tk
import subprocess

def run_script():
    subprocess.run(["pwsh", "-ExecutionPolicy", "Bypass", "-File", "script.ps1"])

root = tk.Tk()
root.title("Запуск PowerShell")

btn = tk.Button(root, text="Запустить", command=run_script)
btn.pack(padx=100, pady=80)

root.mainloop()
