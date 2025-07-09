"""
Módulo de la vista de Información Adicional.

Este archivo define el frame `InfoFrame`, destinado a mostrar información
general, créditos, versión del programa, etc. Actualmente, es un
marcador de posición.
"""

import tkinter as tk

class InfoFrame(tk.Frame):
    """Frame que representa la vista de Información Adicional."""
    def __init__(self, parent, controller):
        """
        Inicializa el frame de Información Adicional.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg=parent.cget("bg"))
        label = tk.Label(self, text="Información Adicional", font=("Arial", 18), bg=self.cget("bg"))
        label.pack(pady=20)
