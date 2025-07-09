"""
Módulo principal de la Interfaz Gráfica de Usuario (GUI).

Este archivo define la clase `App`, que hereda de `tk.Tk` y actúa como la
ventana principal de la aplicación. Es responsable de:
- Crear y gestionar el layout principal (panel de navegación y área de contenido).
- Implementar la funcionalidad del menú de navegación lateral colapsable.
- Instanciar y administrar las diferentes vistas (frames) de la aplicación.
- Controlar el cambio entre las distintas vistas.
"""

import tkinter as tk
from PIL import Image, ImageTk
from gui.dashboard import DashboardFrame
from gui.docs_viewer import DocsViewerFrame
from gui.monitor_view import MonitorViewFrame
from gui.simulador_view import SimuladorViewFrame
from gui.info import InfoFrame
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

        # --- Estado de la Aplicación ---
        # Detectar la red UNA SOLA VEZ al inicio para evitar llamadas repetidas.
        # Esta información se pasa a las vistas que la necesiten.
        self.active_interface, self.local_ip = get_active_network_info()

        # Diccionario para almacenar las instancias de cada frame (vista).
        self.frames = {}

        # Construir la interfaz gráfica.
        self._crear_layout()
        self._crear_frames()
        self.mostrar_frame("Dashboard")

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
                                    relief="flat", font=("Arial", 12), bg="#2c3e50", fg="white")
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
            "Documentación": "Docs",
            "Monitor de Red": "Monitor",
            "Simulador de Ataques": "Simulador",
            "Información Adicional": "Info"
        }
        for texto, nombre_frame in secciones.items():
            btn = tk.Button(self.nav_frame, text=texto,
                            command=lambda nf=nombre_frame: self.mostrar_frame(nf),
                            bg="#34495e", fg="white", font=("Arial", 12), relief="flat", anchor="w")
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_widgets_to_hide.append(btn)

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
            self.menu_expanded = True

    def _crear_frames(self):
        """
        Instancia cada una de las vistas (frames) de la aplicación.

        Almacena las instancias en el diccionario `self.frames` y las apila
        en el mismo lugar dentro del `content_frame`. Solo una será visible
        a la vez.
        """
        # Un contenedor dentro del content_frame para gestionar los frames apilados.
        container = tk.Frame(self.content_frame, bg=self.content_frame.cget("bg"))
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Iterar sobre las clases de los frames para crearlos y almacenarlos.
        for F, name in ((DashboardFrame, "Dashboard"), (DocsViewerFrame, "Docs"),
                        (MonitorViewFrame, "Monitor"), (SimuladorViewFrame, "Simulador"),
                        (InfoFrame, "Info")):
            frame = F(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, nombre):
        """
        Muestra el frame solicitado y oculta el anterior.

        Args:
            nombre (str): El nombre del frame a mostrar (debe ser una clave
                          en `self.frames`).
        """
        # Lógica de limpieza: si estamos saliendo de la pestaña del simulador,
        # nos aseguramos de que cualquier captura en vivo que estuviera activa se detenga.
        if self.current_frame_name == "Simulador":
            sim_frame = self.frames.get("Simulador")
            if sim_frame and sim_frame.captor:
                sim_frame.detener_captura_real()

        # Levanta el frame solicitado para que sea visible.
        frame = self.frames[nombre]
        frame.tkraise()
        self.current_frame_name = nombre

if __name__ == "__main__":
    app = App()
    app.mainloop()
