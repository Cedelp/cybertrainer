"""
Módulo de la vista del Dashboard.

Este archivo define el frame `DashboardViewFrame`, que actúa como la pantalla
de bienvenida y guía inicial para los nuevos usuarios.
"""

import tkinter as tk
from tkinter import ttk

class DashboardViewFrame(tk.Frame):
    """
    Frame que actúa como la pantalla de bienvenida y guía inicial.
    Presenta un recorrido paso a paso para que los nuevos usuarios
    se familiaricen con las funcionalidades clave de CyberTrainer.
    """
    def __init__(self, parent, controller=None):
        """
        Inicializa el frame del Dashboard.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App, optional): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg="#e8f4f8")  # Un fondo claro y limpio

        # --- Contenedor principal para centrar el contenido ---
        main_frame = tk.Frame(self, bg=self.cget("bg"))
        main_frame.pack(pady=30, padx=40, fill="both", expand=True)

        # --- Encabezado ---
        tk.Label(main_frame, text="Bienvenido a CyberTrainer", font=("Arial", 28, "bold"), bg=self.cget("bg"), fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(
            main_frame,
            text="Tu campo de entrenamiento en ciberseguridad. ¡Empecemos!",
            font=("Arial", 14), bg=self.cget("bg"), fg="#34495e"
        ).pack(pady=(0, 30))

        # --- Texto de Introducción ---
        intro_text = (
            "CyberTrainer es una herramienta educativa diseñada para enseñarte los fundamentos del monitoreo de red "
            "y la detección de anomalías. A través de módulos interactivos, aprenderás a identificar tráfico normal, "
            "reconocer ataques comunes y fortalecer tus habilidades en ciberseguridad, todo en un entorno seguro."
        )
        intro_label = tk.Label(main_frame, text=intro_text, font=("Arial", 12),
                               justify="left", wraplength=1, bg=self.cget("bg"), fg="#34495e")
        intro_label.pack(pady=(0, 15), fill="x")

        def update_intro_wraplength(event):
            """Ajusta el wraplength del texto de introducción al cambiar el tamaño del frame."""
            wrap_width = event.width
            intro_label.config(wraplength=wrap_width if wrap_width > 0 else 1)

        main_frame.bind("<Configure>", update_intro_wraplength)

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 10))

        # --- Frame para los pasos guiados ---
        steps_frame = tk.Frame(main_frame, bg=self.cget("bg"))
        steps_frame.pack(fill="both", expand=True, pady=10)
        # Configurar una grilla de 2x2 para las tarjetas
        steps_frame.rowconfigure(0, weight=1)
        steps_frame.rowconfigure(1, weight=1)
        steps_frame.columnconfigure(0, weight=1)
        steps_frame.columnconfigure(1, weight=1)

        if controller:
            # --- Paso 1: Aprende ---
            self._crear_paso_card(
                parent=steps_frame, row=0, column=0,
                numero_paso="Paso 1",
                titulo="Aprende los Fundamentos",
                descripcion="Comienza con los conceptos básicos de redes y seguridad. Es el punto de partida ideal si eres nuevo en este mundo.",
                texto_boton="Ir a Capacitación",
                comando_boton=lambda: controller.mostrar_frame("Docs")
            )

            # --- Paso 2: Practica ---
            self._crear_paso_card(
                parent=steps_frame, row=0, column=1,
                numero_paso="Paso 2",
                titulo="Monitorea tu Red",
                descripcion="Observa el tráfico de tu red en tiempo real. Aprende a distinguir lo normal de lo sospechoso en un entorno seguro.",
                texto_boton="Ir al Monitor",
                comando_boton=lambda: controller.mostrar_frame("Monitor")
            )

            # --- Paso 3: Identifica ---
            self._crear_paso_card(
                parent=steps_frame, row=1, column=0,
                numero_paso="Paso 3",
                titulo="Identifica un Ataque",
                descripcion="Lanza simulaciones de ataques comunes y aprende a reconocer sus patrones directamente en el monitor de tráfico.",
                texto_boton="Ir al Simulador",
                comando_boton=lambda: controller.mostrar_frame("Simulador")
            )

            # --- Tarjeta del Manual de Usuario ---
            self._crear_paso_card(
                parent=steps_frame, row=1, column=1,
                numero_paso="¿Necesitas Ayuda?",
                titulo="Consulta el Manual",
                descripcion="Encuentra una guía detallada sobre cómo usar cada módulo, solucionar problemas y sacar el máximo provecho de CyberTrainer.",
                texto_boton="Ir al Manual",
                comando_boton=lambda: controller.mostrar_frame("Manual")
            )
        # --- Panel de Información del Sistema ---
        info_panel = tk.Frame(main_frame, bg="#d6eaf8", relief="sunken", bd=1)
        info_panel.pack(side="bottom", fill="x", pady=(20, 0), ipady=5)
        info_panel.columnconfigure(0, weight=1)
        info_panel.columnconfigure(1, weight=1)
        info_panel.columnconfigure(2, weight=1)

        # Npcap Status
        npcap_frame = tk.Frame(info_panel, bg=info_panel.cget("bg"))
        npcap_frame.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(npcap_frame, text="Estado de Npcap:", font=("Arial", 10, "bold"), bg=info_panel.cget("bg"), fg="#2c3e50").pack(side="left", padx=(10, 2))
        # Dado que la app no se inicia sin Npcap, podemos asumir que está instalado.
        tk.Label(npcap_frame, text="✅ Instalado", font=("Arial", 10), bg=info_panel.cget("bg"), fg="#27ae60").pack(side="left")

        # Active Interface
        if_frame = tk.Frame(info_panel, bg=info_panel.cget("bg"))
        if_frame.grid(row=0, column=1, sticky="ew", padx=10)
        tk.Label(if_frame, text="Interfaz Activa:", font=("Arial", 10, "bold"), bg=info_panel.cget("bg"), fg="#2c3e50").pack(side="left", padx=(10, 2))
        self.if_label = tk.Label(if_frame, text="Cargando...", font=("Arial", 10), bg=info_panel.cget("bg"), fg="#34495e")
        self.if_label.pack(side="left")

        # Local IP
        ip_frame = tk.Frame(info_panel, bg=info_panel.cget("bg"))
        ip_frame.grid(row=0, column=2, sticky="ew", padx=10)
        tk.Label(ip_frame, text="IP Local:", font=("Arial", 10, "bold"), bg=info_panel.cget("bg"), fg="#2c3e50").pack(side="left", padx=(10, 2))
        self.ip_label = tk.Label(ip_frame, text="Cargando...", font=("Arial", 10), bg=info_panel.cget("bg"), fg="#34495e")
        self.ip_label.pack(side="left")

    def update_network_info(self, interface, ip):
        """Actualiza las etiquetas de información de red en el dashboard."""
        self.if_label.config(text=interface if interface else "No detectada")
        self.ip_label.config(text=ip if ip else "No detectada")

    def _crear_paso_card(self, parent, row, column, numero_paso, titulo, descripcion, texto_boton, comando_boton):
        """
        Crea una tarjeta interactiva para un paso del recorrido inicial.
        """
        card_frame = tk.Frame(parent, bg="#ffffff", relief="raised", bd=1)
        card_frame.grid(row=row, column=column, sticky="nsew", padx=15, pady=10)

        inner_frame = tk.Frame(card_frame, bg="white", padx=25, pady=25)
        inner_frame.pack(fill="both", expand=True)

        tk.Label(inner_frame, text=numero_paso, font=("Arial", 12, "bold"), bg="white", fg="#2980b9").pack(anchor="w")
        tk.Label(inner_frame, text=titulo, font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=(8, 10))
        
        # Usar un wraplength dinámico para que el texto se ajuste al tamaño de la tarjeta.
        # Se inicializa en 1 y se actualiza con el evento <Configure>.
        description_label = tk.Label(inner_frame, text=descripcion, font=("Arial", 11), justify="left", wraplength=1, bg="white", fg="#34495e")
        description_label.pack(anchor="w", fill="x", pady=(0, 20))

        # Botón de acción
        action_button = tk.Button(
            inner_frame, text=texto_boton, command=comando_boton,
            font=("Arial", 11, "bold"), bg="#2980b9", fg="white",
            relief="ridge", bd=1, padx=12, pady=6, cursor="hand2"
        )
        action_button.pack(anchor="w", pady=(10, 0))

        def update_wraplength(event):
            """Ajusta el wraplength del texto de descripción al cambiar el tamaño de la tarjeta."""
            # El ancho disponible es el ancho de la tarjeta menos los paddings laterales del inner_frame (25px * 2).
            wrap_width = event.width - 50
            description_label.config(wraplength=wrap_width if wrap_width > 0 else 1)

        card_frame.bind("<Configure>", update_wraplength)
