# info.py

import tkinter as tk

class InfoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=parent.cget("bg"))
        label = tk.Label(self, text="Información Adicional", font=("Arial", 18), bg=self.cget("bg"))
        label.pack(pady=20)
