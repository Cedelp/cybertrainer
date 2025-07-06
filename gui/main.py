# main.py

import tkinter as tk
from gui.dashboard import DashboardFrame
from gui.docs_viewer import DocsViewerFrame
from gui.monitor_view import MonitorViewFrame
from gui.simulador_view import SimuladorViewFrame
from gui.info import InfoFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Capacitación en Ciberseguridad - PYMEs")
        self.geometry("1000x600")

        # Propiedades del menú
        self.EXPANDED_WIDTH = 200
        self.COLLAPSED_WIDTH = 50
        self.menu_expanded = True
        self.nav_widgets_to_hide = []

        self.frames = {}

        self._crear_layout()
        self._crear_frames()
        self.mostrar_frame("Dashboard")

    def _crear_layout(self):
        # Frame de navegación lateral
        self.nav_frame = tk.Frame(self, bg="#2c3e50", width=self.EXPANDED_WIDTH)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False) # Evita que el frame cambie de tamaño

        # Frame de contenido principal
        self.content_frame = tk.Frame(self, bg="#a7dbd8")
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Botón para ocultar/mostrar el menú (hamburguesa)
        self.toggle_btn = tk.Button(self.nav_frame, text="☰", command=self.toggle_menu, relief="flat", font=("Arial", 12), bg="#2c3e50", fg="white")
        self.toggle_btn.pack(side="top", anchor="ne", pady=5, padx=5)

        # Título en el panel de navegación
        title_label = tk.Label(self.nav_frame, text="CyberTrainer", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=10)
        self.nav_widgets_to_hide.append(title_label)

        # Botones de navegación
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
        if self.menu_expanded:
            # Colapsar menú
            for widget in self.nav_widgets_to_hide:
                widget.pack_forget()
            self.nav_frame.config(width=self.COLLAPSED_WIDTH)
            self.menu_expanded = False
        else:
            # Expandir menú
            self.nav_frame.config(width=self.EXPANDED_WIDTH)
            # Volver a mostrar los widgets en orden
            self.nav_widgets_to_hide[0].pack(pady=10) # El título
            for widget in self.nav_widgets_to_hide[1:]: # Los botones
                widget.pack(fill="x", padx=10, pady=5)
            self.menu_expanded = True

    def _crear_frames(self):
        # El contenedor ahora está dentro del content_frame
        container = tk.Frame(self.content_frame, bg=self.content_frame.cget("bg"))
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Crear las vistas (frames) dentro del contenedor
        for F, name in ((DashboardFrame, "Dashboard"), (DocsViewerFrame, "Docs"),
                        (MonitorViewFrame, "Monitor"), (SimuladorViewFrame, "Simulador"),
                        (InfoFrame, "Info")):
            frame = F(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, nombre):
        frame = self.frames[nombre]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
