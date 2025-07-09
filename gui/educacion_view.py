"""
Módulo de la vista Educativa.

Este archivo define el frame `EducacionViewFrame`, que presenta los
conceptos fundamentales de ciberseguridad y redes de una manera
estructurada y visualmente atractiva, utilizando un sistema de tarjetas
similar al del dashboard.
"""

import tkinter as tk
from tkinter import ttk

class EducacionViewFrame(tk.Frame):
    """
    Frame que contiene el material educativo sobre fundamentos de ciberseguridad.
    """
    def __init__(self, parent, controller=None):
        """
        Inicializa el frame de la Sección Educativa.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg="#e8f4f8")

        # --- Contenedor principal para centrar el contenido ---
        main_frame = tk.Frame(self, bg=self.cget("bg"))
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # --- Encabezado ---
        tk.Label(main_frame, text="Sección Educativa", font=("Arial", 28, "bold"), bg=self.cget("bg"), fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(
            main_frame,
            text="Fundamentos de Ciberseguridad para PYMEs.",
            font=("Arial", 14), bg=self.cget("bg"), fg="#34495e"
        ).pack(pady=(0, 20))

        # --- Contenedor para el contenido scrollable ---
        canvas_container = tk.Frame(main_frame, bg=self.cget("bg"))
        canvas_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_container, bg=self.cget("bg"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg=self.cget("bg"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")

        # --- Bindeo de la rueda del ratón para que funcione en el área general ---
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # --- Contenido Educativo Estructurado ---
        content_data = {
            "Conceptos Básicos de Red": [
                "🌐 Red: Un conjunto de dispositivos (ordenadores, servidores, etc.) conectados para compartir recursos y datos.",
                "📦 Paquete: Una pequeña unidad de datos que viaja a través de una red. Como una carta con remitente, destinatario y contenido.",
                "📜 Protocolo: Un conjunto de reglas que define cómo se comunican los dispositivos (ej: TCP, UDP, IP, ARP)."
            ],
            "¿Qué es una Anomalía de Red?": [
                "Una anomalía es cualquier patrón de tráfico que se desvía de lo normal o esperado.",
                "Puede ser un indicador de un problema de configuración, un fallo de hardware o, más comúnmente, un ciberataque.",
                "Ejemplo: Un número anormalmente alto de paquetes SYN desde una misma fuente puede indicar un escaneo de puertos."
            ],
            "Tipos de Ataques (Simulados en esta App)": [
                "🔎 Escaneo SYN: Intenta descubrir puertos abiertos enviando solicitudes de conexión (SYN) sin completarlas.",
                "💧 Flood UDP: Satura la red con una gran cantidad de paquetes UDP, forzando al objetivo a gastar recursos.",
                "🎭 ARP Spoofing: Falsifica la identidad de un dispositivo en la red local para interceptar o redirigir el tráfico."
            ],
            "Pistas para Interpretar el Tráfico": [
                "🚩 Un paquete TCP con la bandera 'S' (SYN) es un intento de iniciar una conexión.",
                "🌪️ Múltiples paquetes al mismo puerto desde varias fuentes pueden ser un ataque DDoS.",
                "❓ Respuestas ARP ('is-at') que no fueron precedidas por una solicitud ('who-has') son altamente sospechosas de spoofing."
            ],
            "Buenas Prácticas de Seguridad en Redes": [
                "🧱 Utilizar firewalls correctamente configurados para filtrar tráfico no deseado.",
                "🔑 Cambiar contraseñas por defecto en todos los dispositivos de red (routers, switches).",
                "🔄 Mantener el software y firmware de los dispositivos siempre actualizados.",
                "📊 Monitorear el tráfico de red regularmente para establecer una línea base de lo que es 'normal'."
            ],
            "Rol de esta Herramienta": [
                "CyberTrainer es una herramienta de entrenamiento. No reemplaza soluciones de seguridad profesionales como firewalls de próxima generación (NGFW) o sistemas de detección de intrusiones (IDS/IPS).",
                "Su objetivo es capacitarte para entender las alertas que esas herramientas generan y para reconocer patrones clave en una captura de paquetes real, mejorando tu tiempo de respuesta."
            ]
        }

        for titulo, items in content_data.items():
            self._crear_card(scrollable_frame, titulo, items)

    def _on_mousewheel(self, event):
        """Permite el desplazamiento con la rueda del ratón en el canvas."""
        # La división por 120 es estándar para normalizar el delta del ratón en Windows.
        # El signo negativo invierte la dirección para que sea natural.
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _crear_card(self, parent, titulo, items):
        """Crea una tarjeta de información con un estilo consistente."""
        card_frame = tk.Frame(parent, bg="#ffffff", relief="raised", bd=1)
        card_frame.pack(fill="x", expand=True, padx=15, pady=10)

        # Título de la tarjeta
        title_label = tk.Label(card_frame, text=titulo, font=("Arial", 16, "bold"), bg=card_frame.cget("bg"), fg="#2c3e50")
        title_label.pack(pady=(15, 10), padx=25, anchor="w")

        # Separador
        separator = ttk.Separator(card_frame, orient="horizontal")
        separator.pack(fill="x", padx=25, pady=(0, 10))

        # Contenido (lista de items)
        items_frame = tk.Frame(card_frame, bg=card_frame.cget("bg"))
        items_frame.pack(pady=10, padx=25, fill="both", expand=True)

        item_labels = []
        for item in items:
            label = tk.Label(
                items_frame, text=item, font=("Arial", 11),
                justify="left", anchor="w", wraplength=700,  # Ajusta wraplength según el ancho esperado
                bg=card_frame.cget("bg"), fg="#34495e"
            )
            label.pack(pady=5, fill="x")
            item_labels.append(label)

        # Bindeo de la rueda del ratón a todos los elementos para asegurar el scroll en cualquier parte.
        all_widgets = [card_frame, title_label, separator, items_frame] + item_labels
        for widget in all_widgets:
            widget.bind("<MouseWheel>", self._on_mousewheel)
