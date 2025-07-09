"""
Módulo principal de la Interfaz Gráfica de Usuario (GUI).

Este archivo define la clase `App`, que hereda de `tk.Tk` y actúa como la
ventana principal de la aplicación. Es responsable de:
- Crear y gestionar el layout principal (panel de navegación y área de contenido).
- Implementar la funcionalidad del menú de navegación lateral colapsable.
- Instanciar y administrar las diferentes vistas (frames) de la aplicación.
- Controlar el cambio entre las distintas vistas.
"""
import threading
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
from gui.dashboard import DashboardViewFrame
from gui.educacion_view import EducacionViewFrame
from gui.monitor_view import MonitorViewFrame
from gui.simulador_view import SimuladorViewFrame
from gui.manual import ManualUsuarioViewFrame
from gui.info import InfoAdicionalViewFrame
from core.network_utils import get_active_network_info

class App(tk.Tk):
    """
    Clase principal de la aplicación que representa la ventana raíz.

    Hereda de `tkinter.Tk` y orquesta toda la interfaz gráfica. Contiene el
    panel de navegación y el frame de contenido donde se muestran las
    diferentes vistas.
    """
    def __init__(self, icon_path=None, menu_icon_path=None):
        """
        Inicializa la ventana principal de la aplicación.

        Configura el título, las dimensiones y las propiedades del menú.
        Detecta la interfaz de red activa una sola vez al inicio para que
        las demás vistas puedan utilizarla. Llama a los métodos para construir
        el layout y crear los frames de cada sección.

        Args:
            icon_path (str, optional): Ruta al archivo .ico para el icono de la ventana.
                                       Defaults to None.
        """
        super().__init__()
        self.title("Capacitación en Ciberseguridad - PYMEs")
        if icon_path:
            try:
                self.iconbitmap(icon_path)
            except tk.TclError:
                # Previene un error si el icono no se encuentra o es inválido.
                print(f"Advertencia: No se pudo cargar el icono desde {icon_path}")

        self.menu_icon_path = menu_icon_path
        self.state('zoomed')  # Abrir siempre maximizado en Windows

        # --- Propiedades para el menú de navegación colapsable ---
        self.EXPANDED_WIDTH = 200
        self.COLLAPSED_WIDTH = 50
        self.menu_expanded = True
        self.current_frame_name = None
        self.nav_widgets_to_hide = []

        # --- Colores para botones de navegación ---
        self.ACTIVE_BTN_COLOR = "#2980b9"  # Un azul más brillante para el botón activo
        self.INACTIVE_BTN_COLOR = "#34495e" # El color original para los inactivos

        # --- Estado de la Aplicación ---
        # Detectar la red UNA SOLA VEZ al inicio para evitar llamadas repetidas.
        # Se carga en segundo plano para no bloquear la GUI.
        self.active_interface = None
        self.local_ip = None
        self._cargar_info_red_async()

        # Diccionario para almacenar las instancias de cada frame (vista).
        self.frames = {} # Almacenará las instancias de los frames ya creados
        self.nav_buttons = {}

        # Construir la interfaz gráfica.
        self._crear_layout()
        self._crear_frames()
        self.mostrar_frame("Dashboard")

    def _cargar_info_red_async(self):
        """
        Carga la información de la red activa en un hilo separado para no
        bloquear la GUI al inicio.
        """
        def worker():
            """Función que se ejecuta en el hilo."""
            try:
                active_interface, local_ip = get_active_network_info()
                self.active_interface = active_interface
                self.local_ip = local_ip
            except Exception as e:
                print(f"Error al obtener información de la red: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _crear_layout(self):
        """Crea la estructura base de la GUI: panel de navegación y área de contenido."""
        # Frame de navegación lateral
        self.nav_frame = tk.Frame(self, bg="#2c3e50", width=self.EXPANDED_WIDTH)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False) # Evita que el frame cambie de tamaño

        # Frame de contenido principal
        self.content_frame = tk.Frame(self, bg="#a7dbd8")
        self.content_frame.pack(side="right", fill="both", expand=True)


        # Botón para ocultar/mostrar el menú (hamburguesa)
        self.toggle_btn = tk.Button(self.nav_frame, text="☰", command=self.toggle_menu,
                                    relief="ridge", bd=1, font=("Arial", 12), bg="#2c3e50", fg="white")
        self.toggle_btn.pack(side="top", anchor="ne", pady=5, padx=5)

        # Icono encima del título

        try:
            if self.menu_icon_path:
                icon_img = Image.open(self.menu_icon_path)
                icon_img = icon_img.resize((88, 88), Image.LANCZOS)
                self.menu_icon = ImageTk.PhotoImage(icon_img)
                icon_label = tk.Label(self.nav_frame, image=self.menu_icon, bg="#2c3e50")
                icon_label.pack(pady=(16, 0))
                self.nav_widgets_to_hide.append(icon_label)
        except Exception as e:
            print(f"No se pudo cargar el icono del menú: {e}")

        # Título en el panel de navegación (centrado)
        title_label = tk.Label(self.nav_frame, text="CyberTrainer",
                               font=("Arial", 20, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=8, fill="x")
        self.nav_widgets_to_hide.append(title_label)

        # Espacio extra entre el título y los botones
        spacer = tk.Frame(self.nav_frame, height=30, bg="#2c3e50")
        spacer.pack()
        self.nav_widgets_to_hide.append(spacer)

        # Crear los botones de navegación para cada sección de la aplicación.
        secciones = {
            "Dashboard": "Dashboard",
            "Capacitación": "Docs",
            "Manual de Usuario": "Manual",
            "Monitor de Red": "Monitor",
            "Simulador de Ataques": "Simulador",
            "Información Adicional": "Info"
        }
        for texto, nombre_frame in secciones.items():
            btn = tk.Button(self.nav_frame, text=texto,
                            command=lambda nf=nombre_frame: self.mostrar_frame(nf),
                            bg=self.INACTIVE_BTN_COLOR, fg="white", font=("Arial", 12), relief="ridge",
                            bd=1, anchor="w")
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_widgets_to_hide.append(btn)
            self.nav_buttons[nombre_frame] = btn

        # --- Botón de Salir ---
        # Este botón se empaqueta al final, en la parte inferior del panel.
        # Se maneja por separado de 'nav_widgets_to_hide' para que pueda tener
        # un comportamiento de empaquetado y de toggle diferente.
        self.btn_salir = tk.Button(self.nav_frame, text="Salir",
                                   command=self._confirmar_salida,
                                   bg="#c0392b", fg="white", font=("Arial", 12, "bold"), relief="ridge",
                                   bd=1, padx=10) # padx para el espaciado interno
        self.btn_salir.pack(side="bottom", pady=(5, 20)) # Centrado por defecto

    def toggle_menu(self):
        """
        Alterna el estado del menú de navegación entre expandido y colapsado.

        Modifica el ancho del `nav_frame` y oculta o muestra los textos de los botones.
        """
        if self.menu_expanded:
            # Colapsar menú
            for widget in self.nav_widgets_to_hide:
                widget.pack_forget()
            self.nav_frame.config(width=self.COLLAPSED_WIDTH)
            self.btn_salir.config(text="\u274C", padx=10) # Icono de X, mantenemos padding
            self.menu_expanded = False
        else:
            # Expandir menú
            self.nav_frame.config(width=self.EXPANDED_WIDTH)
            # Volver a mostrar los widgets en el orden y con la configuración original.
            # La lista contiene: [icon_label, title_label, spacer, btn1, btn2, ...]
            self.nav_widgets_to_hide[0].pack(pady=(10, 0))      # icon_label
            self.nav_widgets_to_hide[1].pack(pady=5, fill="x")  # title_label
            self.nav_widgets_to_hide[2].pack()                  # spacer
            # El resto de los widgets son los botones de navegación.
            for i in range(3, len(self.nav_widgets_to_hide)):
                self.nav_widgets_to_hide[i].pack(fill="x", padx=10, pady=5)
            self.btn_salir.config(text="Salir", padx=10)
            self.menu_expanded = True

    def _confirmar_salida(self):
        """Muestra un diálogo de confirmación antes de cerrar la aplicación."""
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir de CyberTrainer?"):
            self.destroy()

    def _crear_frames(self):
        """
        Instancia cada una de las vistas (frames) de la aplicación.

        Almacena las instancias en el diccionario `self.frames` y las apila
        en el mismo lugar dentro del `content_frame`. Solo una será visible
        a la vez.
        """
        # Un contenedor dentro del content_frame para gestionar los frames apilados.
        self.container = tk.Frame(self.content_frame, bg=self.content_frame.cget("bg"))
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # En lugar de crear los frames, almacenamos sus clases para crearlos "perezosamente".
        self.frame_classes = {
            "Dashboard": DashboardViewFrame,
            "Docs": EducacionViewFrame,
            "Manual": ManualUsuarioViewFrame,
            "Monitor": MonitorViewFrame,
            "Simulador": SimuladorViewFrame,
            "Info": InfoAdicionalViewFrame
        }

        # Limpiamos el diccionario de instancias. Se llenará bajo demanda.
        self.frames = {}


    def mostrar_frame(self, nombre):
        """
        Muestra el frame solicitado, oculta el anterior y actualiza el estado
        visual de los botones de navegación.

        Args:
            nombre (str): El nombre del frame a mostrar (debe ser una clave
                          en `self.frames`).
        """
        # Lógica de limpieza: si estamos saliendo de la pestaña del simulador,
        # nos aseguramos de que cualquier captura en vivo que estuviera activa se detenga.
        if self.current_frame_name: # Evitar en el primer arranque
            if self.current_frame_name == "Simulador":
                sim_frame = self.frames.get("Simulador")
                if sim_frame and sim_frame.captor:
                    sim_frame.detener_captura_real()

        # Actualizar el estado de los botones de navegación
        for frame_name, button in self.nav_buttons.items():
            if frame_name == nombre:
                button.config(bg=self.ACTIVE_BTN_COLOR)
            else:
                button.config(bg=self.INACTIVE_BTN_COLOR)

        # --- Lógica de Carga Perezosa (Lazy Loading) ---
        # Busca si el frame ya fue creado.
        frame = self.frames.get(nombre)

        if frame is None:
            # Si no existe, lo crea por primera vez.
            FrameClass = self.frame_classes[nombre]
            frame = FrameClass(self.container, self)
            self.frames[nombre] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame.tkraise()
        self.current_frame_name = nombre

if __name__ == "__main__":
    app = App()
    app.mainloop()
