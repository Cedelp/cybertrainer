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
        self.geometry("900x600")
        self.frames = {}
        self._crear_menu()
        self._crear_frames()
        self.mostrar_frame("Dashboard")

    def _crear_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        secciones = tk.Menu(menu, tearoff=0)
        secciones.add_command(label="Dashboard", command=lambda: self.mostrar_frame("Dashboard"))
        secciones.add_command(label="Documentación", command=lambda: self.mostrar_frame("Docs"))
        secciones.add_command(label="Monitor de Red", command=lambda: self.mostrar_frame("Monitor"))
        secciones.add_command(label="Simulador de Ataques", command=lambda: self.mostrar_frame("Simulador"))
        secciones.add_command(label="Información Adicional", command=lambda: self.mostrar_frame("Info"))
        menu.add_cascade(label="Secciones", menu=secciones)

    def _crear_frames(self):
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames["Dashboard"] = DashboardFrame(container, self)
        self.frames["Docs"] = DocsViewerFrame(container, self)
        self.frames["Monitor"] = MonitorViewFrame(container, self)
        self.frames["Simulador"] = SimuladorViewFrame(container, self)
        self.frames["Info"] = InfoFrame(container, self)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, nombre):
        frame = self.frames[nombre]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
