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
        self._crear_card(scrollable_frame, "1. Introducción a CyberTrainer", [
            "Este manual proporciona una guía detallada para el uso de CyberTrainer, una herramienta educativa diseñada para la capacitación en fundamentos de ciberseguridad de redes. El objetivo principal de la aplicación es ofrecer un entorno interactivo y seguro donde los usuarios puedan aprender a monitorear el tráfico de red, identificar anomalías y reconocer patrones de ataques comunes sin ningún riesgo para sus sistemas reales."
        ])
        self._crear_card(scrollable_frame, "2. El Dashboard (Pantalla de Inicio)", [
            "El Dashboard es la primera pantalla que el usuario ve al iniciar la aplicación. Está diseñado para ser un punto de partida claro y orientado a la acción.",
            "Contiene cuatro tarjetas principales que dirigen a las secciones clave de la aplicación: 'Aprende los Fundamentos' (Capacitación), 'Monitorea tu Red' (Monitor), 'Identifica un Ataque' (Simulador) y 'Consulta el Manual' (esta guía).",
            "En la parte inferior, se encuentra el panel de 'Información del Sistema', que muestra datos en tiempo real como el estado del driver Npcap, la interfaz de red activa y la dirección IP local del usuario. Esta información es útil para confirmar que la aplicación detecta correctamente el entorno de red."
        ])
        self._crear_card(scrollable_frame, "3. Módulo de Capacitación", [
            "Esta sección es el componente teórico de la aplicación. Presenta contenido educativo estructurado en cinco niveles progresivos.",
            "Navegación: El usuario puede navegar entre los niveles utilizando los botones en la parte superior ('Nivel 1', 'Nivel 2', etc.).",
            "Interactividad: Cada nivel concluye con un 'Desafío de Conocimiento', un pequeño quiz para validar la comprensión del tema. Además, el usuario puede presionar el botón 'Marcar como Completado' para llevar un registro visual de su progreso. El botón del nivel correspondiente cambiará para mostrar un ícono de verificación (✅)."
        ])
        self._crear_card(scrollable_frame, "4. Monitor de Red", [
            "El Monitor de Red es una herramienta para la captura y análisis de tráfico en tiempo real. Permite al usuario observar los paquetes que atraviesan una interfaz de red seleccionada.",
            "Flujo de trabajo:",
            "1. Selección de Interfaz: En el panel de controles izquierdo, el usuario debe elegir una interfaz de red del menú desplegable (ej. 'Wi-Fi' o 'Ethernet').",
            "2. Inicio de Captura: Al presionar 'Iniciar Captura', la aplicación comienza a escuchar en la interfaz seleccionada. Los paquetes capturados aparecen en la lista de la derecha.",
            "3. Análisis de Paquetes: La lista superior muestra un resumen de cada paquete (origen, destino, protocolo, etc.). Al hacer clic en una fila, el panel inferior 'Detalles del Paquete' muestra un desglose completo de las capas y campos de dicho paquete.",
            "4. Detención de Captura: El proceso se detiene al presionar 'Detener Captura'.",
            "Funcionalidades Adicionales: El usuario puede exportar la sesión de captura a un archivo .pcap para un análisis posterior en herramientas como Wireshark, o importar un archivo .pcap para analizarlo dentro de CyberTrainer."
        ])
        self._crear_card(scrollable_frame, "5. Simulador de Ataques", [
            "Esta es la sección más interactiva, donde el usuario puede lanzar simulaciones de ataques para aprender a identificarlos en un entorno controlado.",
            "Concepto de Seguridad: Es fundamental entender que las simulaciones son 100% seguras. Los paquetes de ataque se generan y se muestran únicamente dentro de la interfaz de la aplicación; nunca se envían a la red real.",
            "Flujo de trabajo recomendado:",
            "1. Iniciar Captura Real: Para una experiencia de aprendizaje óptima, se recomienda primero iniciar una captura en vivo. Esto permite ver los paquetes de ataque mezclados con el tráfico de red normal.",
            "2. Lanzar un Ataque: En el panel izquierdo, el usuario selecciona y presiona el botón del ataque que desea simular (ej. 'Escaneo SYN').",
            "3. Observar y Analizar: En la lista de paquetes, aparecerán nuevas entradas resaltadas en color rojo. Estos son los paquetes del ataque simulado. La pestaña 'Log de Simulación' en el panel inferior narra el progreso del ataque en tiempo real, explicando cada paso.",
            "4. Detener Procesos: El usuario puede detener la simulación en cualquier momento con el botón 'Detener Ataque' y la captura general con 'Detener Captura Real'."
        ])
        self._crear_card(scrollable_frame, "6. Solución de Problemas Comunes", [
            "Error 'Npcap no encontrado' al iniciar: Este error indica que falta el driver de captura de paquetes. La solución es descargar e instalar Npcap desde su sitio web oficial (nmap.org/npcap). Durante la instalación, es crucial marcar la casilla 'Install Npcap in WinPcap API-compatible Mode'.",
            "No se detectan interfaces de red: Si los menús desplegables de interfaces aparecen vacíos o con un error, generalmente se debe a una instalación incorrecta de Npcap. Se recomienda reinstalarlo, asegurando que la opción de compatibilidad esté activada.",
            "La aplicación se inicia lentamente: Es un comportamiento normal. Al arrancar, CyberTrainer realiza una comprobación del sistema y detecta la configuración de red, lo que puede tomar unos segundos.",
            "La interfaz se vuelve lenta durante la captura: La captura de paquetes en tiempo real consume recursos del sistema. Si la aplicación no responde con fluidez, se recomienda detener la captura mientras no se esté analizando activamente el tráfico."
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