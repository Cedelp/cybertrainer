"""
Módulo de la vista del Dashboard.

Este archivo define el frame `DashboardFrame`, que actúa como la pantalla
de bienvenida o la página de inicio de la aplicación. Actualmente, muestra
un mensaje simple.
"""

import tkinter as tk
from tkinter import ttk

class DashboardViewFrame(tk.Frame):
    """
    Frame que actúa como la pantalla de bienvenida de la aplicación.
    Presenta una introducción visualmente atractiva a las capacidades
    y objetivos de CyberTrainer.
    """
    def __init__(self, parent, controller=None):
        """
        Inicializa el frame del Dashboard.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg="#e8f4f8")  # Un fondo claro y limpio

        # --- Contenedor principal para centrar el contenido ---
        main_frame = tk.Frame(self, bg=self.cget("bg"))
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # --- Encabezado ---
        tk.Label(main_frame, text="Bienvenido a CyberTrainer", font=("Arial", 28, "bold"), bg=self.cget("bg"), fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(
            main_frame,
            text="Su plataforma de entrenamiento para fortalecer la ciberseguridad de su PYME.",
            font=("Arial", 14), bg=self.cget("bg"), fg="#34495e"
        ).pack(pady=(0, 30))

        # --- Frame para las tarjetas de información ---
        cards_frame = tk.Frame(main_frame, bg=self.cget("bg"))
        cards_frame.pack(fill="x", expand=True, pady=10)
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)

        # --- Tarjeta 1: Capacidades ---
        self._crear_card(
            parent=cards_frame, row=0, column=0,
            titulo="¿Qué puede hacer?",
            items=[
                "📡 Capturar y analizar tráfico de red en vivo.",
                "💣 Simular ataques comunes (SYN Scan, UDP Flood...).",
                "📘 Aprender a identificar patrones sospechosos.",
                "💾 Exportar capturas para análisis externo (Wireshark)."
            ]
        )

        # --- Tarjeta 2: Objetivo del Programa ---
        self._crear_card(
            parent=cards_frame, row=0, column=1,
            titulo="Objetivo del Programa",
            items=[
                "✅ Reducir el tiempo de detección de incidentes.",
                "✅ Capacitar al personal en conceptos prácticos.",
                "✅ Fomentar una cultura de seguridad proactiva.",
                "✅ Ser una herramienta de autoestudio accesible."
            ]
        )

        # --- Botón de llamada a la acción ---
        if controller:
            btn_ir_monitor = tk.Button(
                main_frame,
                text="🚀 Empezar a Monitorear",
                font=("Arial", 14, "bold"),
                bg="#2980b9",  # Color activo de la app
                fg="white",
                relief="ridge",
                bd=1,
                padx=15,
                pady=8,
                cursor="hand2",
                command=lambda: controller.mostrar_frame("Monitor")
            )
            btn_ir_monitor.pack(pady=40)

    def _crear_card(self, parent, row, column, titulo, items, columnspan=1):
        """Crea una tarjeta de información con un estilo consistente."""
        card_frame = tk.Frame(parent, bg="#ffffff", relief="raised", bd=1)
        card_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=15, pady=15)
        card_frame.rowconfigure(2, weight=1) # Permite que el contenido se expanda

        # Título de la tarjeta
        tk.Label(card_frame, text=titulo, font=("Arial", 16, "bold"), bg=card_frame.cget("bg"), fg="#2c3e50").pack(pady=(15, 10))

        # Separador
        ttk.Separator(card_frame, orient="horizontal").pack(fill="x", padx=20, pady=(0, 10))

        # Contenido (lista de items)
        items_frame = tk.Frame(card_frame, bg=card_frame.cget("bg"))
        items_frame.pack(pady=10, padx=25, fill="both", expand=True)
        for item in items:
            tk.Label(items_frame, text=item, font=("Arial", 11), justify="left", anchor="w", wraplength=350, bg=card_frame.cget("bg"), fg="#34495e").pack(pady=4, fill="x")
