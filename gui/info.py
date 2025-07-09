"""
Módulo de la vista de Información Adicional.

Este archivo define el frame `InfoAdicionalViewFrame`, que presenta
información sobre la aplicación, tecnologías, desarrolladores y otros
recursos de una manera estructurada y visualmente atractiva.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser

class InfoAdicionalViewFrame(tk.Frame):
    """
    Frame que contiene información general, créditos y enlaces útiles.
    """
    def __init__(self, parent, controller=None):
        """
        Inicializa el frame de Información Adicional.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal.
        """
        super().__init__(parent, bg="#e8f4f8")

        # --- Contenedor principal para centrar el contenido ---
        main_frame = tk.Frame(self, bg=self.cget("bg"))
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # --- Encabezado ---
        tk.Label(main_frame, text="Información Adicional", font=("Arial", 28, "bold"), bg=self.cget("bg"), fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(
            main_frame,
            text="Créditos, tecnología y recursos del proyecto.",
            font=("Arial", 14), bg=self.cget("bg"), fg="#34495e"
        ).pack(pady=(0, 20))

        # --- Contenedor para el contenido scrollable ---
        canvas_container = tk.Frame(main_frame, bg=self.cget("bg"))
        canvas_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_container, bg=self.cget("bg"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg=self.cget("bg"))

        scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")

        # --- Bindeo de la rueda del ratón ---
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # --- Contenido Estructurado ---
        self._crear_card(scrollable_frame, "Acerca de la Aplicación", [
            "CyberTrainer es una herramienta educativa diseñada para enseñar los fundamentos de monitoreo de red y detección de anomalías cibernéticas mediante una experiencia interactiva."
        ])

        self._crear_card(scrollable_frame, "Tecnologías Utilizadas", [
            "🐍 Python 3",
            "🎨 Tkinter para la interfaz gráfica",
            "📦 Scapy para la manipulación de paquetes",
            "⚙️ psutil para la detección de interfaces de red"
        ])

        self._crear_card(scrollable_frame, "Equipo de Desarrollo", [
            "Carlos Lorenzo - Estudiante de Ingeniería en Sistemas con enfoque en Ciberseguridad. Apasionado por la formación técnica aplicada.",
            "Sebastian Rodriguez - Estudiante de Ingeniería en Sistemas (NO HIZO NADA).",
            "Fernando Piñango - Estudiante de Ingeniería en Sistemas.",
            "Sebastian Vera - Estudiante de Ingeniería en Sistemas."
        ], is_link=True, link_text="Ver perfil de Carlos Lorenzo en GitHub", link_url="https://github.com/Cedelp")

        self._crear_card(scrollable_frame, "Enlaces Útiles", [
            "🔗 Documentación de Scapy",
            "🔗 Npcap (Driver de captura para Windows)",
            "🔗 Wireshark (Herramienta profesional de análisis)"
        ], links=["https://scapy.readthedocs.io/", "https://nmap.org/npcap/", "https://www.wireshark.org/"])

        self._crear_card(scrollable_frame, "Contacto y Contribuciones", [
            "¿Comentarios o sugerencias? El proyecto es de código abierto. ¡Tus aportes son bienvenidos en el repositorio de GitHub!"
        ])

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _crear_card(self, parent, titulo, items, is_link=False, link_text="", link_url="", links=None):
        card_frame = tk.Frame(parent, bg="#ffffff", relief="raised", bd=1)
        card_frame.pack(fill="x", expand=True, padx=15, pady=10)

        tk.Label(card_frame, text=titulo, font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10), padx=25, anchor="w")
        ttk.Separator(card_frame, orient="horizontal").pack(fill="x", padx=25, pady=(0, 10))

        items_frame = tk.Frame(card_frame, bg="white")
        items_frame.pack(pady=10, padx=25, fill="both", expand=True)

        all_widgets = [card_frame, items_frame]
        for i, item in enumerate(items):
            if links and i < len(links):
                link = tk.Label(items_frame, text=item, font=("Arial", 11, "underline"), fg="blue", cursor="hand2", bg="white", anchor="w")
                link.pack(pady=4, fill="x")
                link.bind("<Button-1>", lambda e, url=links[i]: webbrowser.open_new(url))
                all_widgets.append(link)
            else:
                label = tk.Label(items_frame, text=item, font=("Arial", 11), justify="left", anchor="w", wraplength=700, bg="white", fg="#34495e")
                label.pack(pady=4, fill="x")
                all_widgets.append(label)

        if is_link and link_text and link_url:
            link_label = tk.Label(items_frame, text=link_text, font=("Arial", 11, "underline"), fg="blue", cursor="hand2", bg="white", anchor="w")
            link_label.pack(pady=(10, 4), fill="x")
            link_label.bind("<Button-1>", lambda e, url=link_url: webbrowser.open_new(url))
            all_widgets.append(link_label)

        for widget in all_widgets:
            widget.bind("<MouseWheel>", self._on_mousewheel)
