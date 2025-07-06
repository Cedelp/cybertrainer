# docs_viewer.py

import tkinter as tk

class DocsViewerFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=parent.cget("bg"))
        label = tk.Label(self, text="Documentación del Programa", font=("Arial", 18), bg=self.cget("bg"))
        label.pack(pady=20)
