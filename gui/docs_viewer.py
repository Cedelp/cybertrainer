"""
Módulo del visor de documentación.

Este archivo define el frame `DocsViewerFrame`, que está destinado a mostrar
la documentación del programa o guías de usuario. Actualmente, es un
marcador de posición.
"""

import tkinter as tk

class DocsViewerFrame(tk.Frame):
    """Frame que representa la vista de Documentación."""
    def __init__(self, parent, controller):
        """
        Inicializa el frame del visor de documentación.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg=parent.cget("bg"))
        label = tk.Label(self, text="Documentación del Programa", font=("Arial", 18), bg=self.cget("bg"))
        label.pack(pady=20)
