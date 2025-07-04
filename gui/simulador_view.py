# simulador_view.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from core.simulador import simular_ataque

class SimuladorViewFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Simulador de Ataques", font=("Arial", 18))
        label.pack(pady=10)

        options_frame = tk.Frame(self)
        options_frame.pack(pady=5)

        tk.Label(options_frame, text="Tipo de ataque:").pack(side="left", padx=5)

        self.ataques_disponibles = ["Escaneo SYN", "Flood UDP", "Spoofing ARP"]
        self.ataque_var = tk.StringVar()
        self.ataque_combo = ttk.Combobox(options_frame, textvariable=self.ataque_var, values=self.ataques_disponibles, state="readonly")
        self.ataque_combo.current(0)
        self.ataque_combo.pack(side="left", padx=5)

        self.boton_simular = tk.Button(self, text="Ejecutar ataque", command=self.ejecutar_ataque)
        self.boton_simular.pack(pady=10)

        self.status = tk.Label(self, text="", fg="green")
        self.status.pack()

    def ejecutar_ataque(self):
        tipo = self.ataque_var.get()
        self.status.config(text="Ejecutando ataque...", fg="blue")
        self.boton_simular.config(state="disabled")

        def lanzar():
            try:
                simular_ataque(tipo)
                self.status.config(text=f"Ataque '{tipo}' ejecutado correctamente.", fg="green")
            except Exception as e:
                self.status.config(text=f"Error: {e}", fg="red")
            finally:
                self.boton_simular.config(state="normal")

        threading.Thread(target=lanzar, daemon=True).start()