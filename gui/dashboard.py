"""
Módulo de la vista del Dashboard.

Este archivo define el frame `DashboardFrame`, que actúa como la pantalla
de bienvenida o la página de inicio de la aplicación. Actualmente, muestra
un mensaje simple.
"""

import tkinter as tk

class DashboardFrame(tk.Frame):
    """Frame que representa la vista del Dashboard."""
    def __init__(self, parent, controller):
        """
        Inicializa el frame del Dashboard.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg=parent.cget("bg"))
        label = tk.Label(self, text="Bienvenido al Dashboard", font=("Arial", 18), bg=self.cget("bg"))
        label.pack(pady=20)
