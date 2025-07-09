"""
Módulo de la vista del "Simulador de Ataques".

Este archivo define el frame `SimuladorViewFrame`, que es la interfaz más
interactiva y compleja de la aplicación. Permite a los usuarios:
- Lanzar simulaciones de ataques de red (ej. Escaneo SYN, Flood UDP).
- Ver los paquetes de ataque generados en una lista, mezclados con tráfico real.
- Iniciar y detener una captura de red en vivo en una interfaz seleccionada.
- Ver los paquetes de ataque resaltados visualmente para un fácil reconocimiento.
- Consultar un panel de logs para seguir el progreso de la simulación.
- Leer guías rápidas sobre cómo identificar estos patrones en Wireshark.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import threading
import queue
import time
from core.simulador import simular_ataque, FAKE_ATTACKER_IP
from core.monitor import PacketCaptor, get_network_interfaces
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import ARP

class SimuladorViewFrame(tk.Frame):
    """
    Frame que implementa la vista del "Simulador de Ataques".

    Esta clase combina la captura de paquetes en vivo con la generación de
    paquetes de ataque simulados, mostrándolos en una única interfaz para
    fines educativos.
    """
    def __init__(self, parent, controller):
        """
        Inicializa el frame del Simulador de Ataques.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal, usada para
                              acceder a estado global como la interfaz activa.
        """
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")

        # --- Variables de estado ---
        self.captor = None  # Instancia de PacketCaptor para la captura en vivo.
        self.captured_packets = []  # Almacena todos los paquetes (reales y simulados).
        self.packet_queue = queue.Queue()  # Cola para paquetes de la captura en vivo.
        self.update_job = None  # ID del trabajo 'after' para el bucle de la GUI.
        self.attack_thread = None  # Hilo para ejecutar la simulación de ataque.
        self.stop_attack_event = threading.Event()  # Evento para detener el ataque.
        self.attack_buttons = []  # Lista para gestionar el estado de los botones de ataque.
        self.FAKE_TARGET_IP = "192.168.1.100"  # IP ficticia para el objetivo de los ataques.
        self.iface_var = tk.StringVar()  # Variable para el ComboBox de interfaces.
        self.autoscroll_var = tk.BooleanVar(value=True)  # Variable para el Checkbutton de auto-scroll.

        # --- Diccionario con la información detallada de cada ataque ---
        self.attack_info = {
            "Escaneo SYN": {
                "titulo": "Escaneo de Puertos SYN (Half-Open)",
                "descripcion": (
                    "Un escaneo SYN es una técnica de reconocimiento usada por atacantes para descubrir qué puertos están abiertos en un sistema objetivo. "
                    "El atacante envía un paquete SYN (solicitud de conexión) a varios puertos. Si recibe una respuesta SYN-ACK, el puerto está abierto. Si recibe un RST, está cerrado. "
                    "El atacante nunca completa el 'handshake' de tres vías, por lo que el escaneo es sigiloso y se le llama 'half-open' (medio abierto)."
                ),
                "identificacion": (
                    "En la simulación, verás una ráfaga de paquetes TCP con el flag SYN activado, enviados desde la IP del atacante (192.168.200.100) a diferentes puertos del objetivo. "
                    "Estos paquetes estarán resaltados en rojo. No verás el paquete final ACK que completaría la conexión."
                )
            },
            "Flood UDP": {
                "titulo": "Inundación UDP (UDP Flood)",
                "descripcion": (
                    "Es un ataque de denegación de servicio (DoS) donde el atacante envía una cantidad masiva de paquetes UDP a puertos aleatorios del sistema objetivo. "
                    "El objetivo se ve forzado a procesar cada paquete para determinar qué servicio (si alguno) está escuchando en ese puerto. Al no encontrar un servicio, responde con un paquete ICMP 'Destination Unreachable'. "
                    "El agotamiento de los recursos para procesar estos paquetes y generar respuestas puede dejar al sistema inaccesible."
                ),
                "identificacion": (
                    "Observarás un gran volumen de paquetes UDP resaltados en rojo, enviados desde el atacante al objetivo en un corto período. "
                    "A menudo, el campo 'Info' mostrará que los paquetes van a puertos de destino poco comunes o aleatorios."
                )
            },
            "Spoofing ARP": {
                "titulo": "Envenenamiento ARP (ARP Spoofing)",
                "descripcion": (
                    "Es un ataque Man-in-the-Middle (MitM) donde un atacante envía mensajes ARP falsificados en una red local. El objetivo es asociar la dirección MAC del atacante con la dirección IP de otro dispositivo (como el router o gateway). "
                    "Esto hace que el tráfico de la víctima, destinado al router, pase primero por el atacante, permitiéndole interceptar, leer o modificar los datos."
                ),
                "identificacion": (
                    "Busca paquetes ARP de tipo 'is-at' (respuesta) que no hayas solicitado. En la simulación, verás un paquete ARP resaltado en rojo que le dice a tu IP objetivo que la MAC del router ahora pertenece al atacante. "
                    "Esto se manifiesta como una respuesta ARP (opcode=2) que no fue precedida por una solicitud 'who-has' de tu parte."
                )
            },
            "DDoS Simulado": {
                "titulo": "Ataque de Denegación de Servicio Distribuido (DDoS) Simulado",
                "descripcion": (
                    "Un ataque DDoS real utiliza múltiples sistemas comprometidos (una botnet) para inundar un objetivo con tráfico, sobrecargando sus recursos y haciéndolo inaccesible. "
                    "Esta simulación emula el efecto de un ataque volumétrico simple, enviando una cantidad abrumadora de paquetes (generalmente UDP) en un período muy corto para saturar la capacidad de procesamiento del objetivo."
                ),
                "identificacion": (
                    "Es similar a un Flood UDP pero a una escala mucho mayor y más rápida. Verás una avalancha de paquetes UDP (resaltados en rojo) que aparecen casi instantáneamente en la lista, "
                    "simulando el impacto combinado de múltiples fuentes de ataque."
                )
            }
        }

        # Construir la interfaz gráfica de esta vista.
        self._crear_layout_redimensionable()

    def _crear_layout_redimensionable(self):
        """
        Crea el layout principal de la vista usando PanedWindow.

        Esto permite que el usuario redimensione las áreas de la interfaz:
        - Un panel horizontal divide los controles (izquierda) del contenido (derecha).
        - Un panel vertical divide el contenido en la lista de paquetes (arriba) y
          un Notebook con pestañas para detalles y logs (abajo).
        """
        # El panel principal divide la ventana horizontalmente.
        h_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        h_pane.pack(fill=tk.BOTH, expand=True)

        # 1. Panel de Controles (izquierda)
        control_panel_frame = self._crear_panel_controles()
        h_pane.add(control_panel_frame, weight=1)

        # 2. Panel de Contenido (derecha), que a su vez se divide verticalmente.
        v_pane = ttk.PanedWindow(h_pane, orient=tk.VERTICAL)
        h_pane.add(v_pane, weight=4)

        # 2a. Panel de Lista de Paquetes (arriba-derecha)
        list_panel_frame = self._crear_panel_lista_paquetes()
        v_pane.add(list_panel_frame, weight=5)

        # 2b. Panel de Detalles/Log con pestañas (abajo-derecha)
        notebook_panel_frame = self._crear_panel_detalles_log()
        v_pane.add(notebook_panel_frame, weight=1)

    def _crear_panel_controles(self):
        """
        Crea el panel de la izquierda con todos los controles y la información educativa.

        Este panel es complejo y contiene:
        - Controles para lanzar y detener simulaciones de ataque.
        - Controles para iniciar y detener la captura de red en vivo.
        - Una sección educativa con pistas para identificar ataques en Wireshark.
        Todo está dentro de un Canvas con Scrollbar para ser usable en pantallas pequeñas.
        """
        # Panel de controles compacto, sin scroll
        container = tk.Frame(self, bg="#e0e0e0")

        # --- Título ---
        tk.Label(container, text="Simulador de Ataques", font=("Arial", 15, "bold"), bg=container.cget("bg"), padx=8, anchor="center", justify="center").pack(pady=(10, 6), fill="x")

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(6, 8))

        # Lanzar Simulación
        tk.Label(container, text="Lanzar Simulación", font=("Arial", 11, "bold"), bg=container.cget("bg")).pack(pady=(8, 3))
        ataques = ["Escaneo SYN", "Flood UDP", "Spoofing ARP", "DDoS Simulado"]
        for ataque in ataques:
            btn = tk.Button(container, text=ataque, command=lambda a=ataque: self._iniciar_ataque_en_hilo(a))
            btn.pack(fill="x", pady=2, padx=8)
            self.attack_buttons.append(btn)

        self.btn_stop_attack = tk.Button(container, text="Detener Ataque", command=self._detener_ataque_actual, state="disabled")
        self.btn_stop_attack.pack(fill="x", pady=(7, 4), padx=8)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(10, 8))

        # Captura Real
        tk.Label(container, text="Captura en Vivo", font=("Arial", 11, "bold"), bg=container.cget("bg"), anchor="center", justify="center").pack(padx=8, fill="x")

        if_frame = tk.Frame(container, bg=container.cget("bg"))
        if_frame.pack(fill="x", pady=3, padx=8)
        tk.Label(if_frame, text="Interfaz:", bg=container.cget("bg")).pack(side="left")
        self.iface_combo = ttk.Combobox(if_frame, textvariable=self.iface_var, state="readonly", width=30)
        self.iface_combo.pack(side="left", expand=True, fill="x")

        self.btn_start_capture = tk.Button(container, text="Iniciar Captura Real", command=self.iniciar_captura_real)
        self.btn_start_capture.pack(fill="x", pady=2, padx=8)
        self.btn_stop_capture = tk.Button(container, text="Detener Captura Real", command=self.detener_captura_real, state="disabled")
        self.btn_stop_capture.pack(fill="x", pady=2, padx=8)

        autoscroll_check = tk.Checkbutton(container, text="Auto-scroll en vivo", variable=self.autoscroll_var, bg=container.cget("bg"), anchor="w")
        autoscroll_check.pack(fill="x", padx=12, pady=(2, 6))

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(10, 8))

        # Información de Ataques
        tk.Label(container, text="Información de Ataques", font=("Arial", 11, "bold"), bg=container.cget("bg"), anchor="center", justify="center").pack(padx=8, pady=(2, 2), fill="x")
        for ataque in self.attack_info.keys():
            frame_info = tk.Frame(container, bg=container.cget("bg"))
            frame_info.pack(fill="x", pady=2, padx=8)
            btn_details = tk.Button(frame_info, text="Ver Detalles",
                                    command=lambda a=ataque: self._mostrar_info_ataque(a))
            btn_details.pack(side="right", padx=4)
            tk.Label(frame_info, text=f"{ataque}", font=("Arial", 9, "bold"), bg=container.cget("bg")).pack(side="left", anchor="w")

        self._cargar_interfaces()
        return container

    def _crear_panel_lista_paquetes(self):
        """
        Crea el panel que contiene la lista de paquetes (Treeview).

        Define las columnas, configura un tag 'attack' para resaltar filas,
        y añade las scrollbars.
        """
        list_panel = tk.Frame(self, bg="#f0f0f0")
        list_panel.grid_rowconfigure(0, weight=1)
        list_panel.grid_columnconfigure(0, weight=1)

        cols = ('#', 'Time', 'Source', 'Destination', 'Protocol', 'Length', 'Info')
        self.packet_list = ttk.Treeview(list_panel, columns=cols, show='headings')
        # Configura un 'tag' especial para los paquetes de ataque. Cuando un item
        # se inserta con este tag, tendrá el fondo coloreado.
        self.packet_list.tag_configure('attack', background='#ffdddd')
        for col in cols:
            self.packet_list.heading(col, text=col)
        # ... (configuración de columnas) ...
        self.packet_list.column("#", width=50, anchor="center")
        self.packet_list.column("Time", width=80, anchor="center")
        self.packet_list.column("Source", width=120)
        self.packet_list.column("Destination", width=120)
        self.packet_list.column("Protocol", width=70, anchor="center")
        self.packet_list.column("Length", width=60, anchor="center")
        self.packet_list.column("Info", width=300)

        # Scrollbars
        vsb = ttk.Scrollbar(list_panel, orient="vertical", command=self.packet_list.yview)
        hsb = ttk.Scrollbar(list_panel, orient="horizontal", command=self.packet_list.xview)
        self.packet_list.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.packet_list.bind("<<TreeviewSelect>>", self._mostrar_detalles_paquete)
        self.packet_list.grid(row=0, column=0, sticky='nswe')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        return list_panel

    def _crear_panel_detalles_log(self):
        """
        Crea el panel inferior derecho que contiene un Notebook con pestañas.

        Este panel tiene dos pestañas:
        1. "Detalles del Paquete": Muestra el desglose completo del paquete seleccionado.
        2. "Log de Simulación": Muestra mensajes sobre el progreso de los ataques.
        """
        notebook_panel = tk.Frame(self, bg="#f0f0f0")
        self.notebook = ttk.Notebook(notebook_panel)
        self.notebook.pack(fill="both", expand=True, pady=(5,0))

        # Pestaña de Detalles del Paquete
        details_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.details_text = scrolledtext.ScrolledText(details_frame, state="disabled", bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10))
        self.details_text.pack(expand=True, fill="both")
        self.notebook.add(details_frame, text='Detalles del Paquete')

        # Pestaña de Log de Simulación
        log_frame = tk.Frame(self.notebook, bg="#1a2530")
        self.log_text = scrolledtext.ScrolledText(log_frame, state="disabled", bg="#1a2530", fg="white", font=("Consolas", 10))
        self.log_text.pack(expand=True, fill="both")
        self.notebook.add(log_frame, text='Log de Simulación')
        return notebook_panel
    
    def _mostrar_info_ataque(self, nombre_ataque):
        """
        Muestra la información del ataque en una pestaña del notebook inferior derecho, con botón de cerrar y scroll.
        """
        if nombre_ataque not in self.attack_info or not hasattr(self, 'notebook'):
            return

        # Buscar si ya existe la pestaña
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, 'text') == nombre_ataque:
                self.notebook.select(tab_id)
                return

        info = self.attack_info[nombre_ataque]
        guia_frame = tk.Frame(self.notebook, bg="#f9fbe7")
        # Botón de cerrar
        close_btn = tk.Button(guia_frame, text="❌ Cerrar", font=("Arial", 9), bg="#f9fbe7", fg="#a33", bd=0, cursor="hand2",
                             command=lambda: self._cerrar_pestana_ataque(guia_frame), anchor="e")
        close_btn.pack(anchor="ne", padx=8, pady=(8, 0))
        from tkinter import scrolledtext
        st = scrolledtext.ScrolledText(guia_frame, bg="#f9fbe7", fg="#1a3c4a", font=("Arial", 11), wrap="word", relief="flat", borderwidth=0)
        st.insert("end", info['titulo'] + "\n\n", "bold")
        st.insert("end", "Descripción:\n", "bold2")
        st.insert("end", info['descripcion'] + "\n\n")
        st.insert("end", "Cómo Identificarlo:\n", "bold2")
        st.insert("end", info['identificacion'] + "\n")
        st.tag_configure("bold", font=("Arial", 13, "bold"))
        st.tag_configure("bold2", font=("Arial", 10, "bold"))
        st.config(state="disabled")
        st.pack(fill="both", expand=True, padx=20, pady=10)
        self.notebook.add(guia_frame, text=nombre_ataque)
        self.notebook.select(guia_frame)

    def _cerrar_pestana_ataque(self, frame):
        """Cierra la pestaña de información de ataque asociada al frame dado."""
        if hasattr(self, 'notebook'):
            self.notebook.forget(frame)

    def iniciar_captura_real(self):
        """
        Inicia la captura de paquetes en vivo en la interfaz seleccionada.

        - Valida la selección de la interfaz.
        - Limpia la vista (lista de paquetes, logs, etc.).
        - Inicia un `PacketCaptor` en un hilo separado.
        - Actualiza el estado de los botones de la GUI.
        """
        iface = self.iface_var.get()
        if not iface or "Cargando" in iface or "Error" in iface:
            messagebox.showerror("Error de Interfaz", "Por favor, selecciona una interfaz de red válida para la captura.")
            return

        # Limpiar la vista de cualquier captura o simulación anterior.
        self.packet_list.delete(*self.packet_list.get_children())
        self.captured_packets.clear()
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

        # Limpiar la cola de cualquier paquete residual de una ejecución anterior.
        while not self.packet_queue.empty():
            try: self.packet_queue.get_nowait()
            except queue.Empty: continue

        self.captor = PacketCaptor(interface=iface, packet_callback=self._agregar_paquete)
        self.captor.start()
        self._log_to_gui(f"Captura real iniciada en {iface}\n")

        self.btn_start_capture.config(state="disabled")
        self.btn_stop_capture.config(state="normal")
        self.iface_combo.config(state="disabled")
        
        # Asegurarse de que el bucle de procesamiento de la cola esté corriendo.
        if not self.update_job:
            self._process_packet_queue()

    def detener_captura_real(self):
        """
        Detiene la captura de paquetes en vivo.

        - Señaliza al hilo de `PacketCaptor` para que se detenga.
        - Cancela el bucle de actualización de la GUI (`update_job`).
        - Restaura el estado de los botones.
        """
        if self.captor:
            self.captor.stop()
            self.captor = None
            self._log_to_gui("Captura real detenida.\n")

        # Detener el bucle de actualización de la GUI
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None

        self.btn_start_capture.config(state="normal")
        self.btn_stop_capture.config(state="disabled")
        self.iface_combo.config(state="readonly")

    def _cargar_interfaces(self):
        """
        Carga las interfaces de red disponibles de forma asíncrona.

        Para evitar que la GUI se congele mientras Scapy busca las interfaces,
        esta operación se realiza en un hilo separado. Una vez obtenidas,
        la actualización del ComboBox se programa para ejecutarse en el hilo
        principal de la GUI usando `self.after`.
        """
        self.iface_combo['values'] = ["Cargando..."]
        def fetch():
            try:
                interfaces = get_network_interfaces()
                active_iface = self.controller.active_interface
                if interfaces:
                    def update_gui():
                        self.iface_combo.configure(values=interfaces)
                        if active_iface and active_iface in interfaces:
                            self.iface_var.set(active_iface)
                        elif interfaces:
                            self.iface_var.set(interfaces[0])
                    self.after(0, update_gui)
                else:
                    self.after(0, lambda: self.iface_combo.configure(values=["No hay interfaces"]))
            except Exception as e:
                self.after(0, lambda: self.iface_combo.configure(values=["Error al cargar"]))
        threading.Thread(target=fetch, daemon=True).start()

    def _agregar_paquete(self, packet):
        """
        Callback para paquetes de la captura en vivo.

        Este método se ejecuta en el hilo de `PacketCaptor`, NO en el hilo de la GUI.
        Su única responsabilidad es poner el paquete capturado en la `queue.Queue`
        thread-safe para que el hilo de la GUI lo procese más tarde.
        """
        self.packet_queue.put(packet)

    def _process_packet_queue(self):
        """
        Procesa la cola de paquetes de la captura en vivo y actualiza la GUI.

        Este método se ejecuta en el hilo principal de la GUI. Extrae paquetes de la
        cola y los inserta en la lista. Al procesar solo un paquete y luego
        reprogramarse a sí mismo con `self.after`, se asegura que la GUI permanezca
        fluida y receptiva, y que los paquetes aparezcan uno por uno, facilitando
        el análisis visual.
        """
        try:
            # Para que la captura sea fácil de seguir, procesamos solo UN paquete
            # por cada ciclo de actualización.
            for _ in range(1):
                packet = self.packet_queue.get_nowait()
                self._insertar_paquete_en_gui(packet)
        except queue.Empty:
            pass
        finally:
            # Una pausa más larga (400ms) hace que cada paquete sea visible
            # antes de que aparezca el siguiente, facilitando el análisis.
            self.update_job = self.after(400, self._process_packet_queue)

    def _insertar_paquete_en_gui(self, packet):
        """
        Inserta un único paquete (real o simulado) en el Treeview de la GUI.

        Este método se ejecuta siempre en el hilo principal de la GUI.
        - Extrae la información resumida del paquete.
        - Determina si es un paquete de ataque basándose en las IPs/MACs falsas.
        - Inserta el paquete en el Treeview, aplicando el tag 'attack' si corresponde.
        - Gestiona el auto-scroll.
        """
        self.captured_packets.append(packet)
        pkt_id = len(self.captured_packets)
        tags = ()
        proto, src, dst, info = "N/A", "N/A", "N/A", packet.summary()

        # --- Lógica para identificar si el paquete es parte de una simulación ---
        # Se usan las constantes importadas de core.simulador para la comprobación.
        FAKE_ATTACKER_IP = "192.168.200.100" # Debe coincidir con el de core/simulador.py
        is_attack = False
        
        # IP-based attacks from our fake source
        if packet.haslayer(IP) and packet[IP].src == FAKE_ATTACKER_IP and packet[IP].dst == self.FAKE_TARGET_IP:
            # Escaneo SYN, Flood UDP o DDoS
            if packet.haslayer(TCP) or packet.haslayer(UDP):
                is_attack = True
        # ARP-based attack
        elif packet.haslayer(ARP) and packet[ARP].op == 2 and packet[ARP].pdst == self.FAKE_TARGET_IP:
            # El ataque ARP Spoof simula venir de una IP de gateway común
            is_attack = True

        if is_attack:
            # Si es un ataque, se le asigna el tag que le dará el fondo rojo.
            tags = ('attack',)

        # --- Parseo de información del paquete para la GUI ---
        if packet.haslayer(IP):
            src = packet[IP].src
            dst = packet[IP].dst
            if packet.haslayer(TCP): proto = "TCP"
            elif packet.haslayer(UDP): proto = "UDP"
            else: proto = "IP"
        elif packet.haslayer(ARP):
            proto = "ARP"
            src = packet[ARP].psrc
            dst = packet[ARP].pdst

        pkt_time = time.strftime('%H:%M:%S', time.localtime(packet.time))
        values = (pkt_id, pkt_time, src, dst, proto, len(packet), info)
        
        item_id = str(pkt_id)
        self.packet_list.insert('', 'end', values=values, iid=item_id, tags=tags)

        if is_attack:
            # Si es un paquete de ataque, siempre lo enfocamos para que no se pierda.
            self.packet_list.see(item_id)
        elif self.autoscroll_var.get():
            # Para el tráfico normal, solo hacemos auto-scroll si la opción está activada.
            self.packet_list.yview_moveto(1)

    def _mostrar_detalles_paquete(self, event):
        """
        Muestra los detalles del paquete seleccionado en el panel de detalles.

        Este es el manejador de eventos para la selección de un item en el Treeview.
        Recupera el objeto de paquete completo de la lista `captured_packets` y
        utiliza `packet.show(dump=True)` para obtener una representación detallada
        en formato de texto, que luego se muestra en el panel inferior.
        """
        try:
            if not self.packet_list.selection():
                return
            selected_item = self.packet_list.selection()[0]
            packet_id = int(selected_item)
            packet = self.captured_packets[packet_id - 1]

            details = packet.show(dump=True)

            self.details_text.config(state="normal")
            self.details_text.delete("1.0", tk.END)
            self.details_text.insert(tk.END, details)
            self.details_text.config(state="disabled")
            self.notebook.select(0)  # Cambiar a la pestaña de detalles
        except (IndexError, ValueError):
            pass

    def _log_to_gui(self, message):
        """
        Añade un mensaje al panel de log de la simulación de forma segura.

        Args:
            message (str): El mensaje a registrar.
        """
        self.notebook.select(1)
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message)
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def _detener_ataque_actual(self):
        """
        Señaliza al hilo de simulación de ataque para que se detenga.

        Activa el `stop_attack_event`, que es verificado periódicamente dentro
        de la función `simular_ataque`.
        """
        if self.attack_thread and self.attack_thread.is_alive():
            self._log_to_gui("--- Señal de detención enviada al ataque ---\n")
            self.stop_attack_event.set()
            self.btn_stop_attack.config(text="Deteniendo...", state="disabled")

    def _reset_attack_buttons(self):
        """
        Restaura el estado de los botones de ataque a su estado inicial.

        Se llama cuando una simulación de ataque termina (ya sea por completarse
        o por ser detenida).
        """
        for btn in self.attack_buttons:
            btn.config(state="normal")
        self.btn_stop_attack.config(text="Detener Ataque", state="disabled")

    def _iniciar_ataque_en_hilo(self, tipo_ataque):
        """
        Inicia una nueva simulación de ataque en un hilo separado.

        Args:
            tipo_ataque (str): El nombre del ataque a simular.
        """
        # Deshabilitar botones para evitar múltiples ataques simultáneos.
        for btn in self.attack_buttons:
            btn.config(state="disabled")
        self.btn_stop_attack.config(state="normal")
        self.stop_attack_event.clear()

        self._log_to_gui(f"--- Iniciando simulación: {tipo_ataque} ---\n")

        # --- Callback para paquetes simulados ---
        # A diferencia de la captura real, los paquetes simulados no usan una cola.
        # Se "inyectan" directamente en el hilo de la GUI usando `self.after(0, ...)`.
        # Esto asegura que se muestren inmediatamente y en el orden correcto,
        # sin interferir con la cola de paquetes de la captura real.
        def direct_insert_callback(packet):
            self.after(0, self._insertar_paquete_en_gui, packet)
        callback = direct_insert_callback

        # Si no hay una captura real activa, limpiamos la lista para que solo
        # se vean los paquetes del ataque. Si hay una captura activa, los
        # paquetes de ataque se mezclarán con el tráfico real.
        if not self.captor:
            self.packet_list.delete(*self.packet_list.get_children())
            self.captured_packets.clear()

        def attack_wrapper():
            """Ejecuta el ataque y luego resetea los botones de la GUI."""
            simular_ataque(tipo_ataque, self.FAKE_TARGET_IP, callback, self.stop_attack_event, self._log_to_gui)
            self.after(0, self._reset_attack_buttons)

        self.attack_thread = threading.Thread(target=attack_wrapper, daemon=True)
        self.attack_thread.start()