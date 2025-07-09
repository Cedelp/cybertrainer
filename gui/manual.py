"""
Módulo de la vista del Manual de Usuario.

Este archivo define el frame `ManualUsuarioViewFrame`, que presenta una guía
detallada sobre cómo utilizar las diferentes funcionalidades de la aplicación
CyberTrainer.
"""

import tkinter as tk
from tkinter import ttk

class ManualUsuarioViewFrame(tk.Frame):
    """
    Frame que contiene la guía de usuario de la aplicación.
    """
    def __init__(self, parent, controller=None):
        """
        Inicializa el frame del Manual de Usuario.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg="#e8f4f8")

        # --- Contenedor principal para centrar el contenido ---
        main_frame = tk.Frame(self, bg=self.cget("bg"))
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # --- Encabezado ---
        tk.Label(main_frame, text="Manual de Usuario", font=("Arial", 28, "bold"), bg=self.cget("bg"), fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(
            main_frame,
            text="Guía completa para utilizar CyberTrainer.",
            font=("Arial", 14), bg=self.cget("bg"), fg="#34495e"
        ).pack(pady=(0, 20))

        # --- Contenedor para el contenido scrollable ---
        canvas_container = tk.Frame(main_frame, bg=self.cget("bg"))
        canvas_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_container, bg=self.cget("bg"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg=self.cget("bg"))

        scroll_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Cuando el canvas cambie de tamaño, forzamos al frame interior a tener el mismo ancho.
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(scroll_window, width=e.width))

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")

        # --- Bindeo de la rueda del ratón ---
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # --- Contenido del Manual ---
        self._crear_card(scrollable_frame, "Introducción", [
            "Bienvenido a CyberTrainer. Esta herramienta está diseñada para ser una plataforma educativa e interactiva, enfocada en capacitar al personal de PYMEs en los fundamentos de la ciberseguridad de redes.",
            "El objetivo principal es proporcionar un entorno seguro y controlado donde puedas aprender a identificar tráfico de red normal, reconocer anomalías y entender cómo se manifiestan algunos de los ataques más comunes, todo sin poner en riesgo tu red real."
        ])
        self._crear_card(scrollable_frame, "Módulo de Capacitación", [
            "Esta sección es tu punto de partida teórico. Aquí encontrarás contenido educativo estructurado en cinco niveles progresivos, desde los conceptos más básicos de redes hasta las buenas prácticas de seguridad.",
            "Navegación: Utiliza los botones en la parte superior ('Nivel 1', 'Nivel 2', etc.) para acceder a cada tema.",
            "Interactividad: Al final de cada nivel, encontrarás un pequeño desafío para poner a prueba tus conocimientos. También puedes marcar un nivel como 'Completado' para llevar un registro visual de tu progreso."
        ])
        self._crear_card(scrollable_frame, "Monitor de Red", [
            "El monitor de red es tu ventana al tráfico que fluye a través de tu dispositivo. Te permite capturar y analizar paquetes en tiempo real.",
            "1. Selecciona una interfaz: En el panel izquierdo, elige la interfaz de red que deseas monitorear (ej. 'Wi-Fi' o 'Ethernet').",
            "2. Inicia la captura: Haz clic en 'Iniciar Captura'. Los paquetes que pasen por esa interfaz comenzarán a aparecer en la lista de la derecha.",
            "3. Analiza los paquetes: La lista superior muestra un resumen de cada paquete. Haz clic en una fila para ver un desglose completo de sus capas y campos en el panel de 'Detalles del Paquete' inferior.",
            "4. Detén la captura: Cuando termines, haz clic en 'Detener Captura'.",
            "Funcionalidades extra: Puedes exportar los paquetes capturados a un archivo .pcap para analizarlos más tarde con herramientas como Wireshark, o importar un archivo .pcap existente."
        ])
        self._crear_card(scrollable_frame, "Simulador de Ataques", [
            "Esta es la sección más interactiva. Aquí puedes lanzar simulaciones de ataques comunes en un entorno completamente seguro para aprender a identificarlos.",
            "Uso recomendado: Para una experiencia más realista, primero inicia una captura en vivo y luego lanza el ataque. Así verás los paquetes maliciosos mezclados con tu tráfico normal.",
            "1. Inicia la captura real: Selecciona una interfaz y haz clic en 'Iniciar Captura Real'.",
            "2. Lanza un ataque: En el panel izquierdo, haz clic en el botón del ataque que deseas simular (ej. 'Escaneo SYN').",
            "3. Observa y analiza: Verás cómo aparecen nuevos paquetes en la lista, resaltados en rojo. Estos son los paquetes del ataque. La pestaña 'Log de Simulación' te narrará el progreso del ataque paso a paso.",
            "4. Detén todo: Puedes detener la simulación con 'Detener Ataque' y la captura general con 'Detener Captura Real'.",
            "Importante: Las simulaciones son 100% seguras. Los paquetes de ataque se generan y se muestran en la interfaz, pero nunca se envían a tu red real."
        ])
        self._crear_card(scrollable_frame, "Solución de Problemas", [
            "Si la aplicación muestra un error de 'Npcap no encontrado' al iniciar: Debes instalar Npcap desde su sitio web oficial (nmap.org/npcap). Durante la instalación, es crucial que marques la casilla 'Install Npcap in WinPcap API-compatible Mode'.",
            "Si no se detectan interfaces de red en los menús desplegables: Esto generalmente se debe a una instalación incorrecta de Npcap o a problemas con los drivers. Intenta reinstalar Npcap asegurándote de marcar la opción de compatibilidad.",
            "La aplicación se inicia lentamente: Es normal que la aplicación tarde unos segundos en arrancar. Durante este tiempo, está detectando la configuración de tu red para funcionar correctamente.",
            "La interfaz se siente lenta durante la captura: La captura de paquetes en tiempo real consume recursos. Si la aplicación no responde fluidamente, prueba deteniendo la captura mientras no estés analizando activamente el tráfico."
        ])

    def _on_mousewheel(self, event):
        """Manejador del evento de la rueda del ratón para hacer scroll en el canvas."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _crear_card(self, parent, titulo, items):
        """Crea una tarjeta de información con un estilo consistente."""
        card_frame = tk.Frame(parent, bg="#ffffff", relief="raised", bd=1)
        card_frame.pack(fill="x", expand=True, padx=15, pady=10)

        tk.Label(card_frame, text=titulo, font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10), padx=25, anchor="w")
        ttk.Separator(card_frame, orient="horizontal").pack(fill="x", padx=25, pady=(0, 10))

        items_frame = tk.Frame(card_frame, bg="white")
        items_frame.pack(pady=10, padx=25, fill="both", expand=True)

        labels_to_wrap = []
        for item in items:
            label = tk.Label(items_frame, text=f"• {item}", font=("Arial", 11), justify="left", anchor="w", bg="white", fg="#34495e", wraplength=1)
            label.pack(pady=4, fill="x")
            label.bind("<MouseWheel>", self._on_mousewheel)
            labels_to_wrap.append(label)

        def update_wraplength(event):
            # El ancho disponible para el texto es el ancho de la tarjeta menos los paddings.
            # Padding de items_frame: 25px a cada lado.
            # Un pequeño margen extra de 10px para seguridad.
            wrap_width = event.width - (25 * 2) - 10
            if wrap_width < 1: # Evitar valores negativos o cero
                wrap_width = 1
            for label in labels_to_wrap:
                label.config(wraplength=wrap_width)

        # Vincular el evento al widget correcto: card_frame, que es el que se expande.
        card_frame.bind("<Configure>", update_wraplength)

        card_frame.bind("<MouseWheel>", self._on_mousewheel)
        items_frame.bind("<MouseWheel>", self._on_mousewheel)