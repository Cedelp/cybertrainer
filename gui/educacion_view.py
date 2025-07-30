"""
Módulo de la vista Educativa.

Este archivo define el frame `EducacionViewFrame`, que presenta los
conceptos fundamentales de ciberseguridad y redes de una manera
estructurada y visualmente atractiva, utilizando un sistema de tarjetas
similar al del dashboard.
"""


import tkinter as tk
from tkinter import ttk, messagebox

class EducacionViewFrame(tk.Frame):
    """
    Frame que presenta contenido educativo sobre ciberseguridad y redes.
    """
    def __init__(self, parent, controller=None):
        """
        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App, optional): La instancia de la aplicación principal. Defaults to None.
        """
        super().__init__(parent, bg="#e8f4f8")
        self.current_canvas = None # Para mantener una referencia al canvas activo
        self.labels_to_wrap_educacion = [] # Lista para las etiquetas que necesitan ajuste de línea

        # --- Contenedor principal para centrar el contenido ---
        main_frame = tk.Frame(self, bg=self.cget("bg"))
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # --- Encabezado ---
        tk.Label(main_frame, text="Contenido Educativo", font=("Arial", 28, "bold"), bg=self.cget("bg"), fg="#2c3e50").pack(pady=(10, 5))
        tk.Label(
            main_frame,
            text="Explora los conceptos clave de ciberseguridad y redes, nivel por nivel.",
            font=("Arial", 14), bg=self.cget("bg"), fg="#34495e"
        ).pack(pady=(0, 20))

        # --- Contenido de la vista ---
        self.niveles = {
            "Nivel 1: Fundamentos de Redes": self.nivel_1,
            "Nivel 2: Anomalías de Red": self.nivel_2,
            "Nivel 3: Tipos de Ataques": self.nivel_3,
            "Nivel 4: Interpretación de Tráfico": self.nivel_4,
            "Nivel 5: Buenas Prácticas": self.nivel_5
        }

        self.estado_completado = {nivel: False for nivel in self.niveles}

        # Frame para los botones de selección de nivel
        self.botones_niveles = tk.Frame(main_frame, bg=self.cget("bg"))
        self.botones_niveles.pack(pady=10)

        # Diccionario para todos los botones de navegación de esta vista
        self.boton_widgets = {}

        # Botón de Inicio
        inicio_btn = tk.Button(self.botones_niveles, text="🏠 Inicio", command=self.mostrar_inicio,
                               bg='#ffffff', fg="#34495e", font=("Arial", 10), relief='ridge', bd=1, padx=10, pady=5)
        inicio_btn.pack(side=tk.LEFT, padx=4)
        self.boton_widgets["Inicio"] = inicio_btn

        # Botones de Niveles
        for nivel in self.niveles:
            # Usamos el texto corto para el botón (ej. "Nivel 1")
            texto_corto = nivel.split(":")[0]
            btn = tk.Button(self.botones_niveles, text=f"🟥 {texto_corto}", command=lambda n=nivel: self.mostrar_nivel(n),
                            bg='#ffffff', fg="#34495e", font=("Arial", 10), relief='ridge', bd=1, padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=4)
            self.boton_widgets[nivel] = btn

        # Contenedor para el contenido del nivel (scrollable) y las acciones (fijas)
        content_container = tk.Frame(main_frame, bg=self.cget("bg"))
        content_container.pack(expand=True, fill='both')

        # El marco de contenido es la "tarjeta" blanca que albergará el canvas scrollable
        self.marco_contenido = tk.Frame(main_frame, bg="#ffffff", relief="raised", bd=1)
        self.marco_contenido.pack(in_=content_container, expand=True, fill='both', padx=15, pady=(10,0))

        # Frame para los botones de acción fijos en la parte inferior
        self.actions_frame = tk.Frame(main_frame, bg=self.cget("bg"))
        self.actions_frame.pack(in_=content_container, side='bottom', fill='x', pady=10)
        # Mostrar la vista de inicio por defecto
        self.mostrar_inicio()

    def _actualizar_botones_activos(self, nombre_activo):
        """Resalta el botón activo y desactiva los demás."""
        for nombre, boton in self.boton_widgets.items():
            if nombre == nombre_activo:
                boton.config(bg="#d4edda") # Color verde claro para activo
            else:
                # Restaurar color original, excepto para los ya completados
                if nombre in self.estado_completado and self.estado_completado[nombre]:
                    texto_corto = nombre.split(":")[0]
                    boton.config(text=f"✅ {texto_corto}", bg='#d4edda', fg="#155724")
                else:
                    boton.config(bg="#ffffff") # Color blanco para inactivo

    def _on_mousewheel(self, event):
        """Manejador de la rueda del ratón para el canvas activo."""
        if self.current_canvas:
            self.current_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def mostrar_inicio(self):
        """Muestra la tarjeta de bienvenida del módulo educativo."""
        self.nivel_actual = "Inicio"
        self._actualizar_botones_activos("Inicio")
        for widget in self.marco_contenido.winfo_children():
            widget.destroy()

        # Ocultar y limpiar el frame de acciones en la página de inicio
        self.actions_frame.pack_forget()
        for widget in self.actions_frame.winfo_children():
            widget.destroy()

        self.current_canvas = None  # No hay canvas en la página de inicio

        # Recrear la tarjeta de bienvenida con un wraplength fijo, ya que esta
        # vista no usa el canvas de scroll y, por lo tanto, no tiene ajuste dinámico.
        titulo = "Bienvenido al Módulo Educativo"
        parrafos = [
            "Esta sección está diseñada para guiarte a través de los conceptos clave de la ciberseguridad en redes, desde los fundamentos hasta las buenas prácticas.",
            "Utiliza los botones de nivel en la parte superior para navegar por el contenido. Cada nivel se enfoca en un tema específico y termina con un pequeño desafío para poner a prueba tus conocimientos.",
            "Cuando completes un nivel, puedes marcarlo como tal. ¡Tu progreso se guardará visualmente en los botones!"
        ]

        tk.Label(self.marco_contenido, text=titulo, font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10), padx=25, anchor="w")
        ttk.Separator(self.marco_contenido, orient="horizontal").pack(fill="x", padx=25, pady=(0, 10))
        items_frame = tk.Frame(self.marco_contenido, bg="white")
        items_frame.pack(pady=5, padx=25, fill="x", anchor="w")

        for p in parrafos:
            # Usar un wraplength fijo y razonable.
            tk.Label(items_frame, text=f"• {p}", font=("Arial", 11), justify="left", anchor="w", wraplength=850, bg="white", fg="#34495e").pack(pady=4, fill="x")

    def actualizar_estado(self, nivel):
        """
        Marca un nivel como completado y actualiza visualmente su botón.

        Args:
            nivel (str): El nombre completo del nivel a marcar como completado.
        """
        self.estado_completado[nivel] = True
        btn = self.boton_widgets[nivel]
        texto_corto = nivel.split(":")[0]
        btn.config(text=f"✅ {texto_corto}", bg='#d4edda', fg="#155724")

    def mostrar_nivel(self, nivel_nombre):
        """
        Limpia el contenido actual y muestra el contenido de un nivel específico.

        Crea un canvas con scrollbar para albergar el contenido del nivel,
        que es generado por la función correspondiente (ej. self.nivel_1).

        Args:
            nivel_nombre (str): El nombre del nivel a mostrar.
        """
        self.nivel_actual = nivel_nombre
        self._actualizar_botones_activos(nivel_nombre)
        for widget in self.marco_contenido.winfo_children():
            widget.destroy()

        # Limpiar y mostrar el frame de acciones
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        self.actions_frame.pack(side='bottom', fill='x', pady=10)

        self.labels_to_wrap_educacion = [] # Reiniciar la lista para el nuevo nivel

        canvas = tk.Canvas(self.marco_contenido, bg='white', highlightthickness=0)
        self.current_canvas = canvas # Guardar referencia al canvas actual
        scrollbar = ttk.Scrollbar(self.marco_contenido, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='white')
        
        # ID del frame dentro del canvas, para poder modificar su ancho.
        scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        
        # Cuando el frame interior se reconfigure (cambie de tamaño), actualizamos la región de scroll.
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def update_content_and_wraplength(event):
            """Actualiza el ancho del contenido y el ajuste de línea del texto."""
            canvas.itemconfig(scroll_window, width=event.width)
            wrap_width = event.width - (25 * 2) - 10 # Padding de 25px a cada lado
            if wrap_width < 1: wrap_width = 1
            for label in self.labels_to_wrap_educacion:
                if label.winfo_exists():
                    label.config(wraplength=wrap_width)

        canvas.bind("<Configure>", update_content_and_wraplength)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Poblar el frame con el contenido del nivel
        self.niveles[nivel_nombre](scroll_frame, self.actions_frame)

        # --- Bindeo de la rueda del ratón ---
        # Se bindea a todos los widgets dentro del área de scroll para asegurar
        # que el scroll funcione sin importar dónde esté el cursor del ratón.
        widgets_to_bind = [canvas, scroll_frame]
        def collect_children(widget):
            widgets_to_bind.extend(widget.winfo_children())
            for child in widget.winfo_children():
                collect_children(child)
        collect_children(scroll_frame)

        for widget in widgets_to_bind:
            widget.bind("<MouseWheel>", self._on_mousewheel)

    def insertar_texto(self, parent, titulo, parrafos):
        """
        Inserta un bloque de texto con título y viñetas en un frame.

        Args:
            parent (tk.Widget): El widget padre donde se insertará el texto.
            titulo (str): El título del bloque de texto.
            parrafos (list[str]): Una lista de strings, cada uno será un punto
                                  con una viñeta.
        """
        # Estilo de título de tarjeta
        tk.Label(parent, text=titulo, font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10), padx=25, anchor="w")
        # Separador como en las otras tarjetas
        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=25, pady=(0, 10))

        items_frame = tk.Frame(parent, bg="white")
        items_frame.pack(pady=5, padx=25, fill="x", anchor="w")

        for p in parrafos:
            # Estilo de item de tarjeta con viñeta
            label = tk.Label(items_frame, text=f"• {p}", font=("Arial", 11), justify="left", anchor="w", wraplength=1, bg="white", fg="#34495e")
            label.pack(pady=4, fill="x")
            self.labels_to_wrap_educacion.append(label)

    def quiz(self, parent, pregunta, opciones, correcta, completar_callback=None):
        """
        Crea un pequeño quiz de opción múltiple dentro de un frame.

        Args:
            parent (tk.Widget): El widget padre donde se insertará el quiz.
            pregunta (str): La pregunta del quiz.
            opciones (list[str]): Una lista de posibles respuestas.
            correcta (str): La respuesta correcta, que debe estar en la lista
                            de opciones.
            completar_callback (callable, optional): Función a ejecutar al marcar como completado.
        """
        quiz_frame = tk.Frame(parent, bg=parent.cget("bg"))
        quiz_frame.pack(side='left', fill='x', expand=True, padx=20)

        tk.Label(quiz_frame, text="🧠 Desafío de Conocimiento", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(anchor="w")
        label_pregunta = tk.Label(quiz_frame, text=pregunta, wraplength=1, font=("Arial", 11), bg="white", justify="left", fg="#34495e")
        label_pregunta.pack(anchor="w", pady=(5, 10))
        self.labels_to_wrap_educacion.append(label_pregunta)

        respuesta = tk.StringVar()
        for opt in opciones:
            tk.Radiobutton(quiz_frame, text=opt, variable=respuesta, value=opt, bg="white", font=("Arial", 11), fg="#34495e", anchor="w",
                           activebackground="white", activeforeground="#2c3e50", selectcolor="#e8f4f8").pack(anchor="w")

        def validar():
            if respuesta.get() == correcta:
                messagebox.showinfo("Resultado", "✅ ¡Correcto!")
            else:
                messagebox.showerror("Resultado", f"❌ Incorrecto. La respuesta correcta es: {correcta}")

        btn_frame = tk.Frame(quiz_frame, bg='white')
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Validar Respuesta", command=validar, bg='#dff0d8', relief="ridge", bd=1).pack(side='left', padx=5)

        if completar_callback:
            tk.Button(btn_frame, text="Marcar como Completado", command=completar_callback, bg='#e6f7ff', relief="ridge", bd=1).pack(side='left', padx=5)

    def completado_btn(self, parent):
        """
        Crea un botón para que el usuario marque el nivel actual como completado.

        Args:
            parent (tk.Widget): El widget padre donde se insertará el botón.
        """
        def marcar():
            self.actualizar_estado(self.nivel_actual)
            messagebox.showinfo("Nivel completado", "✔️ Este nivel ha sido marcado como completado.")
        comp_frame = tk.Frame(parent, bg=parent.cget("bg"))
        comp_frame.pack(side='right', padx=20, pady=10)
        tk.Button(comp_frame, text="Marcar como Completado", command=marcar, bg='#e6f7ff', relief="ridge", bd=1).pack(side='right')
        
    def nivel_1(self, frame, actions_frame):
        self.insertar_texto(frame, "¿Qué es una red informática?", [
            "Una red informática es un conjunto de dispositivos interconectados entre sí que pueden comunicarse para compartir datos, servicios y recursos.",
            "Puede ser de tipo LAN (local), MAN (metropolitana), WAN (amplia) o PAN (personal), según el tamaño y la ubicación.",
            "Ejemplo: una red doméstica conecta tu computadora, celular e impresora a través de un router."
        ])
        self.insertar_texto(frame, "Componentes clave de una red:", [
            "- Router: distribuye tráfico entre redes.",
            "- Switch: conecta múltiples dispositivos dentro de una red.",
            "- IP: dirección única de cada dispositivo.",
            "- Paquete: unidad mínima de datos que se transmite."
        ])
        self.insertar_texto(frame, "Protocolos comunes:", [
            "TCP: orientado a conexión, asegura que los paquetes lleguen (HTTP, FTP).",
            "UDP: sin conexión, más rápido pero no confiable (streaming, DNS).",
            "ICMP: usado para mensajes de error y diagnóstico (ping)."
        ])
        self.quiz(actions_frame, "¿Qué protocolo garantiza entrega de datos?", ["UDP", "ARP", "TCP", "ICMP"], "TCP", completar_callback=lambda: self.actualizar_estado(self.nivel_actual) or messagebox.showinfo("Nivel completado", "✔️ Este nivel ha sido marcado como completado."))

    def nivel_2(self, frame, actions_frame):
        self.insertar_texto(frame, "¿Qué es una anomalía de red?", [
            "Una anomalía de red es un comportamiento inesperado en el tráfico, que puede indicar un problema técnico, una mala configuración o un ataque.",
            "El monitoreo permite detectarlas a tiempo y actuar antes de que causen daño."
        ])
        self.insertar_texto(frame, "Ejemplos de anomalías:", [
            "- Flujo masivo de paquetes a puertos aleatorios.",
            "- Repetidas respuestas ARP no solicitadas.",
            "- Niveles de tráfico que superan la línea base habitual.",
            "- IP desconocidas generando múltiples intentos de conexión fallidos."
        ])
        self.insertar_texto(frame, "¿Cómo se detectan?", [
            "Herramientas de monitoreo analizan patrones, frecuencia, comportamiento inusual.",
            "El uso de registros históricos ayuda a reconocer desviaciones.",
            "En CyberTrainer puedes ver ejemplos reales en el módulo de monitoreo."
        ])
        self.quiz(actions_frame, "¿Cuál de los siguientes sería una posible señal de anomalía?", ["Un archivo .pdf", "Muchos paquetes ICMP en segundos", "Uso bajo del CPU", "Ping exitoso"], "Muchos paquetes ICMP en segundos", completar_callback=lambda: self.actualizar_estado(self.nivel_actual) or messagebox.showinfo("Nivel completado", "✔️ Este nivel ha sido marcado como completado."))

    def nivel_3(self, frame, actions_frame):
        self.insertar_texto(frame, "Tipos de ataques de red (simulados en CyberTrainer):", [
            "🔎 Escaneo SYN: el atacante envía múltiples solicitudes SYN a diferentes puertos para descubrir cuáles están abiertos sin completar el 'handshake' completo.",
            "💧 UDP Flood: bombardeo de paquetes UDP aleatorios para saturar puertos y consumir recursos.",
            "🎭 ARP Spoofing: el atacante finge ser otro dispositivo, interceptando tráfico o redirigiendo comunicaciones.",
            "🌪️ DDoS: ataques distribuidos desde múltiples máquinas para agotar el ancho de banda o recursos del sistema objetivo."
        ])
        self.insertar_texto(frame, "¿Cómo identificarlos?", [
            "Usa el monitoreo de tráfico para buscar:",
            "- Exceso de solicitudes SYN sin respuesta.",
            "- Respuestas ARP inusuales.",
            "- Patrones masivos de tráfico hacia un mismo puerto.",
            "- Fuentes IP múltiples con alto volumen de paquetes."
        ])
        self.quiz(actions_frame, "¿Qué ataque finge ser otro dispositivo en red?", ["DDoS", "ARP Spoofing", "SYN Scan", "Ninguno"], "ARP Spoofing", completar_callback=lambda: self.actualizar_estado(self.nivel_actual) or messagebox.showinfo("Nivel completado", "✔️ Este nivel ha sido marcado como completado."))

    def nivel_4(self, frame, actions_frame):
        self.insertar_texto(frame, "Interpretación del tráfico de red:", [
            "Cada protocolo tiene características que lo distinguen.",
            "⚙️ TCP: usa banderas SYN, ACK, FIN, RST para establecer, mantener y cerrar una conexión.",
            "🔍 Si ves muchos SYN sin ACK → escaneo o denegación.",
            "📊 Si ves muchas peticiones UDP sin respuesta → ataque tipo flood.",
            "🛡️ Las respuestas ARP sin petición suelen ser señal de spoofing."
        ])
        self.insertar_texto(frame, "¿Cómo mejorar la interpretación?", [
            "✔️ Practicar viendo paquetes reales.",
            "✔️ Usar herramientas como Wireshark o el propio CyberTrainer.",
            "✔️ Estudiar tráfico normal vs tráfico anómalo.",
            "✔️ Comparar logs de distintas sesiones."
        ])
        self.quiz(actions_frame, "¿Qué bandera TCP indica inicio de conexión?", ["ACK", "SYN", "RST", "FIN"], "SYN", completar_callback=lambda: self.actualizar_estado(self.nivel_actual) or messagebox.showinfo("Nivel completado", "✔️ Este nivel ha sido marcado como completado."))

    def nivel_5(self, frame, actions_frame):
        self.insertar_texto(frame, "Buenas Prácticas de Seguridad en Redes:", [
            "✅ Mantén tu red segmentada: separa dispositivos por niveles de acceso.",
            "✅ Desactiva servicios innecesarios en routers y servidores.",
            "✅ Cambia las contraseñas por defecto.",
            "✅ Revisa logs frecuentemente y establece alertas.",
            "✅ Cierra puertos no utilizados.",
            "✅ Asegura los endpoints con antivirus y políticas de uso.",
            "✅ Aplica políticas de mínimo privilegio en usuarios y procesos.",
            "✅ Monitorea constantemente con herramientas como CyberTrainer."
        ])
        self.quiz(actions_frame, "¿Cuál de estas prácticas mejora la visibilidad de actividad sospechosa?", ["Usar USB", "Revisar logs", "Dejar puertos abiertos", "Compartir Wi-Fi"], "Revisar logs", completar_callback=lambda: self.actualizar_estado(self.nivel_actual) or messagebox.showinfo("Nivel completado", "✔️ Este nivel ha sido marcado como completado."))
