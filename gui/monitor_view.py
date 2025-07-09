import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from core.monitor import PacketCaptor, get_network_interfaces
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import ARP

class MonitorViewFrame(tk.Frame):
    """
    Frame que implementa la vista del "Monitor de Red".

    Esta clase es responsable de mostrar una interfaz para capturar y analizar
    el tráfico de red en tiempo real. Permite al usuario seleccionar una interfaz,
    iniciar/detener la captura y ver los paquetes en una lista, con detalles
    para cada paquete seleccionado.
    """
    def __init__(self, parent, controller):
        """
        Inicializa el frame del Monitor de Red.

        Args:
            parent (tk.Widget): El widget padre (el contenedor de frames).
            controller (App): La instancia de la aplicación principal, usada para
                              acceder a estado global como la interfaz activa.
        """
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")

        # --- Diccionario de información educativa ---
        self.info_educativa = {
            "Cómo leer la lista de paquetes": (
                "- Source/Destination: IP de origen y destino.\n"
                "- Protocol: TCP, UDP, ARP, etc.\n"
                "- Info: Resumen del contenido del paquete.\n"
                "\nEjemplo: Un paquete TCP con destino a puerto 80 suele ser tráfico web.\n"
                "Haz clic en un paquete para ver todos sus detalles abajo."
            ),
            "Cómo entender los detalles de un paquete": (
                "Cada campo en los detalles representa información específica del protocolo.\n\n"
                "Por ejemplo, en IP:\n"
                "- version: Versión del protocolo IP (normalmente 4).\n"
                "- ihl: Longitud del encabezado IP.\n"
                "- tos: Tipo de servicio.\n"
                "- len: Longitud total del paquete IP.\n"
                "- id: Identificador del paquete.\n"
                "- flags: Indicadores de fragmentación.\n"
                "- frag: Fragment offset.\n"
                "- ttl: Tiempo de vida del paquete.\n"
                "- proto: Protocolo encapsulado (TCP, UDP, ICMP, etc).\n"
                "- chksum: Suma de verificación del encabezado IP.\n"
                "- src: Dirección IP de origen.\n"
                "- dst: Dirección IP de destino.\n"
                "\nEn TCP:\n"
                "- sport: Puerto de origen.\n"
                "- dport: Puerto de destino.\n"
                "- seq: Número de secuencia.\n"
                "- ack: Número de acuse de recibo.\n"
                "- dataofs: Tamaño del encabezado TCP.\n"
                "- reserved: Reservado.\n"
                "- flags: Indicadores (SYN, ACK, FIN, etc).\n"
                "- window: Tamaño de ventana.\n"
                "- chksum: Suma de verificación TCP.\n"
                "- urgptr: Puntero urgente.\n"
                "\nEn UDP:\n"
                "- sport: Puerto de origen.\n"
                "- dport: Puerto de destino.\n"
                "- len: Longitud del segmento UDP.\n"
                "- chksum: Suma de verificación UDP.\n"
                "\nEn ARP:\n"
                "- hwtype: Tipo de hardware.\n"
                "- ptype: Tipo de protocolo.\n"
                "- hwlen: Longitud de dirección hardware.\n"
                "- plen: Longitud de dirección de protocolo.\n"
                "- op: Operación (request/reply).\n"
                "- hwsrc: Dirección MAC de origen.\n"
                "- psrc: Dirección IP de origen.\n"
                "- hwdst: Dirección MAC de destino.\n"
                "- pdst: Dirección IP de destino.\n"
                "\nConsulta el glosario para ver todos los campos posibles."
            ),
            "Glosario de términos": (
                "Campos comunes al inspeccionar un paquete:\n\n"
                "IP: version, ihl, tos, len, id, flags, frag, ttl, proto, chksum, src, dst\n"
                "TCP: sport, dport, seq, ack, dataofs, reserved, flags, window, chksum, urgptr\n"
                "UDP: sport, dport, len, chksum\n"
                "ICMP: type, code, chksum, id, seq\n"
                "ARP: hwtype, ptype, hwlen, plen, op, hwsrc, psrc, hwdst, pdst\n"
                "Ethernet: dst, src, type\n\n"
                "Otros términos:\n"
                "- Paquete: Unidad de datos transmitida por la red.\n"
                "- Protocolo: Conjunto de reglas para la comunicación (ej: TCP, UDP, ARP).\n"
                "- Puerto: Punto lógico de conexión en un dispositivo.\n"
                "- Flag SYN: Indica el inicio de una conexión TCP.\n"
                "- MAC: Dirección física única de una tarjeta de red.\n"
                "- ICMP: Protocolo usado para mensajes de control y diagnóstico (ej: ping).\n"
                "- TTL: Tiempo de vida de un paquete IP.\n"
                "- Fragmentación: División de paquetes grandes en fragmentos más pequeños.\n"
                "- Window: Control de flujo TCP.\n"
                "- Checksum: Suma de verificación para detectar errores.\n"
                "- Dataofs: Tamaño del encabezado TCP.\n"
                "- Urgptr: Puntero urgente TCP.\n"
                "- Seq/Ack: Números de secuencia y acuse de recibo TCP.\n"
                "- Type/Code: Tipo y código de mensaje ICMP.\n"
                "- HWsrc/HWdst: MAC origen/destino en ARP.\n"
                "- Psrc/Pdst: IP origen/destino en ARP.\n"
            ),
            "Tráfico normal vs sospechoso": (
                "Tráfico normal: Navegación web, DNS, correo, actualizaciones.\n"
                "Tráfico sospechoso: Muchos paquetes a puertos no estándar, ráfagas de paquetes similares, tráfico a direcciones desconocidas, mucho ICMP, etc.\n"
                "\nEjemplo: Un solo equipo enviando cientos de paquetes por segundo a diferentes destinos puede indicar un malware o escaneo."
            ),
            "Buenas prácticas de monitoreo": (
                "- Analiza patrones, no solo paquetes individuales.\n"
                "- Guarda capturas relevantes para análisis posterior.\n"
                "- Mantén tu software de monitoreo actualizado.\n"
                "- Si detectas algo sospechoso, consulta con un experto en ciberseguridad."
            )
        }

        # --- Variables de estado ---
        self.captor = None  # Instancia de PacketCaptor para el hilo de captura.
        self.captured_packets = []  # Lista para almacenar los objetos de paquete completos.
        self.packet_queue = queue.Queue()  # Cola para comunicar paquetes entre hilos.
        self.update_job = None  # ID del trabajo 'after' para poder cancelarlo.

        # --- Layout Principal con Paneles Redimensionables ---
        self._crear_layout_redimensionable()

    def _crear_layout_redimensionable(self):
        """
        Crea el layout principal de la vista usando PanedWindow.

        Esto permite que el usuario redimensione las áreas de la interfaz:
        - Un panel horizontal divide los controles (izquierda) del contenido (derecha).
        - Un panel vertical divide el contenido en la lista de paquetes (arriba) y
          los detalles del paquete (abajo).
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

        # 2. Panel de Lista de Paquetes (arriba)
        list_panel_frame = self._crear_panel_lista_paquetes()
        v_pane.add(list_panel_frame, weight=5)

        # 3. Panel de Detalles (abajo)
        details_panel_frame = self._crear_panel_detalles()
        v_pane.add(details_panel_frame, weight=1)
    def _crear_panel_controles(self):
        """
        Crea el panel de la izquierda con los controles de captura.

        Este panel contiene el selector de interfaz y los botones para iniciar
        y detener la captura. Se implementa dentro de un Canvas con una Scrollbar
        para asegurar que todos los controles sean visibles incluso si la ventana
        es muy pequeña.
        """
        # Contenedor principal para el canvas y la scrollbar
        container = tk.Frame(self, bg="#e0e0e0")
        # --- Título y selección de interfaz ---
        tk.Label(container, text="Monitor de Red", font=("Arial", 16, "bold"), bg=container.cget("bg"), anchor="center", justify="center").pack(pady=10, fill="x")
        if_frame = tk.Frame(container, bg=container.cget("bg"))
        if_frame.pack(fill="x", pady=5)
        tk.Label(if_frame, text="Interfaz:", bg=container.cget("bg")).pack(side="left")
        self.iface_var = tk.StringVar()
        self.iface_combo = ttk.Combobox(if_frame, textvariable=self.iface_var, state="readonly", width=25)
        self.iface_combo.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # --- Botones de captura debajo de la selección de interfaz ---
        self.btn_start = tk.Button(container, text="Iniciar Captura", command=self.iniciar_captura)
        self.btn_start.pack(fill="x", padx=5, pady=(8,2))
        self.btn_stop = tk.Button(container, text="Detener Captura", command=self.detener_captura, state="disabled")
        self.btn_stop.pack(fill="x", padx=5, pady=(0,8))

        # --- Botones de exportar/importar uno debajo del otro, mismo estilo, justo después de detener captura ---
        btn_export = tk.Button(
            container, text="Exportar paquetes", command=self._exportar_paquetes
        )
        btn_export.pack(fill="x", padx=5, pady=(0, 4))
        btn_import = tk.Button(
            container, text="Importar paquetes", command=self._importar_paquetes
        )
        btn_import.pack(fill="x", padx=5, pady=(0, 10))

        # --- Separador y sección de guías rápidas ---
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(2, 6))

        # Guías rápidas (estilo sección de ataques)
        tk.Label(container, text="Guías rápidas", font=("Arial", 11, "bold"), bg="#e0e0e0", fg="black", anchor="center", justify="center").pack(padx=8, pady=(2, 2), fill="x")
        for titulo in self.info_educativa.keys():
            frame_info = tk.Frame(container, bg=container.cget("bg"))
            frame_info.pack(fill="x", pady=2, padx=8)
            btn_details = tk.Button(frame_info, text="Ver Guía",
                                    command=lambda t=titulo: self._mostrar_info_educativa_en_pestana(t),
                                    font=("Arial", 10, "bold"))
            btn_details.pack(side="right", padx=4)
            tk.Label(frame_info, text=f"{titulo}", font=("Arial", 9, "bold"), bg=container.cget("bg"), anchor="w").pack(side="left", anchor="w")
        # Cargar interfaces al iniciar
        self._cargar_interfaces()
        return container

    def _exportar_paquetes(self):
        """Exporta los paquetes capturados a un archivo .pcap."""
        from tkinter import filedialog
        import scapy.utils
        if not self.captured_packets:
            messagebox.showinfo("Exportar paquetes", "No hay paquetes capturados para exportar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pcap", filetypes=[("PCAP files", "*.pcap"), ("Todos", "*.*")])
        if file_path:
            try:
                scapy.utils.wrpcap(file_path, self.captured_packets)
                messagebox.showinfo("Exportar paquetes", f"Paquetes exportados correctamente a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error al exportar", f"No se pudo exportar:\n{e}")

    def _importar_paquetes(self):
        """Importa paquetes desde un archivo .pcap y los muestra en la lista."""
        from tkinter import filedialog
        import scapy.utils
        file_path = filedialog.askopenfilename(filetypes=[("PCAP files", "*.pcap"), ("Todos", "*.*")])
        if file_path:
            try:
                pkts = list(scapy.utils.rdpcap(file_path))
                if not pkts:
                    messagebox.showinfo("Importar paquetes", "El archivo no contiene paquetes.")
                    return
                self.packet_list.delete(*self.packet_list.get_children())
                self.captured_packets = pkts
                for i, packet in enumerate(pkts, 1):
                    proto, src, dst, info = "N/A", "N/A", "N/A", packet.summary()
                    from scapy.layers.inet import IP, TCP, UDP
                    from scapy.layers.l2 import ARP
                    if packet.haslayer(IP):
                        src = packet[IP].src
                        dst = packet[IP].dst
                        if packet.haslayer(TCP):
                            proto = "TCP"
                        elif packet.haslayer(UDP):
                            proto = "UDP"
                        else:
                            proto = "IP"
                    elif packet.haslayer(ARP):
                        proto = "ARP"
                        src = packet[ARP].psrc
                        dst = packet[ARP].pdst
                    pkt_time = "--:--:--"
                    values = (i, pkt_time, src, dst, proto, len(packet), info)
                    self.packet_list.insert('', 'end', values=values, iid=str(i))
                self.details_text.config(state="normal")
                self.details_text.delete("1.0", tk.END)
                self.details_text.config(state="disabled")
                messagebox.showinfo("Importar paquetes", f"Se importaron {len(pkts)} paquetes.")
            except Exception as e:
                messagebox.showerror("Error al importar", f"No se pudo importar:\n{e}")
    def _mostrar_info_educativa_en_pestana(self, titulo):
        """Muestra la guía rápida como una pestaña en el notebook inferior derecho, con botón de cerrar y scroll si es necesario."""
        if not hasattr(self, 'notebook'):
            return
        # Buscar si ya existe la pestaña
        for idx in range(len(self.notebook.tabs())):
            tab_id = self.notebook.tabs()[idx]
            if self.notebook.tab(tab_id, 'text') == titulo:
                self.notebook.select(tab_id)
                return
        # Si no existe, crearla
        texto = self.info_educativa.get(titulo, "Sin información disponible.")
        guia_frame = tk.Frame(self.notebook, bg="#f9fbe7")
        # Botón de cerrar
        close_btn = tk.Button(guia_frame, text="❌ Cerrar", font=("Arial", 9), bg="#f9fbe7", fg="#a33", bd=0, cursor="hand2",
                             command=lambda: self._cerrar_pestana_guia(guia_frame), anchor="e")
        close_btn.pack(anchor="ne", padx=8, pady=(8, 0))
        from tkinter import scrolledtext
        st = scrolledtext.ScrolledText(guia_frame, bg="#f9fbe7", fg="#1a3c4a", font=("Arial", 11), wrap="word", relief="flat", borderwidth=0)
        st.insert("1.0", texto)
        st.config(state="disabled")
        st.pack(fill="both", expand=True, padx=20, pady=10)
        self.notebook.add(guia_frame, text=titulo)
        self.notebook.select(guia_frame)

    def _cerrar_pestana_guia(self, frame):
        """Cierra la pestaña de guía rápida asociada al frame dado."""
        if hasattr(self, 'notebook'):
            self.notebook.forget(frame)


    # El método _mostrar_info_educativa ya no es necesario porque las guías estarán en pestañas

    def _crear_panel_lista_paquetes(self):
        """
        Crea el panel superior derecho que contiene la lista de paquetes (Treeview).

        Returns:
            tk.Frame: El frame que contiene el Treeview y sus scrollbars.
        """
        list_panel = tk.Frame(self, bg="#f0f0f0")
        list_panel.grid_rowconfigure(1, weight=1)
        list_panel.grid_columnconfigure(0, weight=1)


        # --- Lista de Paquetes (Treeview) ---
        cols = ('#', 'Time', 'Source', 'Destination', 'Protocol', 'Length', 'Info')
        self.packet_list = ttk.Treeview(list_panel, columns=cols, show='headings')
        for col in cols:
            self.packet_list.heading(col, text=col)
        # Configuración de columnas
        self.packet_list.column("#", width=50, anchor="center")
        self.packet_list.column("Time", width=80, anchor="center")
        self.packet_list.column("Source", width=120)
        self.packet_list.column("Destination", width=120)
        self.packet_list.column("Protocol", width=70, anchor="center")
        self.packet_list.column("Length", width=60, anchor="center")
        self.packet_list.column("Info", width=300)

        # Scrollbars para la lista
        vsb = ttk.Scrollbar(list_panel, orient="vertical", command=self.packet_list.yview)
        hsb = ttk.Scrollbar(list_panel, orient="horizontal", command=self.packet_list.xview)
        self.packet_list.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Vincular el evento de selección a la función para mostrar detalles
        self.packet_list.bind("<<TreeviewSelect>>", self._mostrar_detalles_paquete)

        self.packet_list.grid(row=1, column=0, sticky='nswe')
        vsb.grid(row=1, column=1, sticky='ns')
        hsb.grid(row=2, column=0, sticky='ew')
        # Expandir correctamente
        list_panel.grid_rowconfigure(1, weight=1)
        list_panel.grid_columnconfigure(0, weight=1)
        return list_panel

    def _crear_panel_detalles(self):
        """
        Crea el panel inferior derecho que muestra un Notebook con pestañas:
        - Detalles del Paquete
        - Guías rápidas (una pestaña por cada guía)
        """
        notebook_panel = tk.Frame(self, bg="#f0f0f0")
        notebook_panel.rowconfigure(0, weight=1)
        notebook_panel.columnconfigure(0, weight=1)
        self.notebook = ttk.Notebook(notebook_panel)
        self.notebook.grid(row=0, column=0, sticky='nswe', padx=0, pady=(5,0))

        # Pestaña de Detalles del Paquete
        details_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        details_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)
        self.details_text = scrolledtext.ScrolledText(details_frame, state="disabled", bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10))
        self.details_text.grid(row=0, column=0, sticky='nswe')
        self.notebook.add(details_frame, text='Detalles del Paquete')

        return notebook_panel

    def _cargar_interfaces(self):
        """
        Carga las interfaces de red disponibles de forma asíncrona.

        Para evitar que la GUI se congele mientras Scapy busca las interfaces,
        esta operación se realiza en un hilo separado. Una vez obtenidas,
        la actualización del ComboBox se programa para ejecutarse en el hilo
        principal de la GUI usando `self.after`.
        """
        self.iface_combo['values'] = ["Cargando..."]
        self.iface_var.set("Cargando...")
        def fetch():
            try:
                interfaces = get_network_interfaces()
                if interfaces:
                    def update_gui():
                        placeholder = "Seleccione una interfaz de red"
                        full_list = [placeholder] + interfaces
                        self.iface_combo.configure(values=full_list)
                        self.iface_var.set(placeholder)
                    self.after(0, update_gui)
                else:
                    self.after(0, lambda: self.iface_combo.configure(values=["No hay interfaces"]))
            except Exception as e:
                self.after(0, lambda: self.iface_combo.configure(values=["Error al cargar"]))
                messagebox.showerror("Error de Interfaz", f"No se pudieron cargar las interfaces de red:\n{e}")
        threading.Thread(target=fetch, daemon=True).start()

    def iniciar_captura(self):
        """
        Inicia el proceso de captura de paquetes.

        Valida la interfaz seleccionada, limpia la vista de capturas anteriores,
        inicia un nuevo `PacketCaptor` en su propio hilo, actualiza el estado
        de los botones y comienza el bucle de procesamiento de la cola de paquetes
        para actualizar la GUI.
        """
        placeholder = "Seleccione una interfaz de red"
        iface = self.iface_var.get()
        if not iface or iface == placeholder or "Cargando" in iface or "Error" in iface:
            messagebox.showerror("Error", "Por favor, selecciona una interfaz de red válida.")
            return

        # Limpiar vista anterior
        self.packet_list.delete(*self.packet_list.get_children())
        self.captured_packets.clear()
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state="disabled")

        # Limpiar la cola de cualquier paquete residual
        while not self.packet_queue.empty():
            try:
                self.packet_queue.get_nowait()
            except queue.Empty:
                continue

        self.captor = PacketCaptor(interface=iface, packet_callback=self._agregar_paquete)
        self.captor.start()

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.iface_combo.config(state="disabled")
        
        # Iniciar el bucle de procesamiento de la cola
        self._process_packet_queue()

    def detener_captura(self):
        """
        Detiene la captura de paquetes.

        Señaliza al hilo de `PacketCaptor` para que se detenga, cancela el
        trabajo de actualización de la GUI (`update_job`) y restaura el estado
        de los botones.
        """
        if self.captor:
            self.captor.stop()
            self.captor = None
        
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None

        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.iface_combo.config(state="readonly")

    def _agregar_paquete(self, packet):
        """
        Callback ejecutado por el hilo de captura para cada paquete.

        Este método se ejecuta en el hilo de `PacketCaptor`, NO en el hilo de la GUI.
        Su única responsabilidad es poner el paquete capturado en una `queue.Queue`
        thread-safe, para que el hilo de la GUI pueda procesarlo más tarde.

        Args:
            packet (scapy.packet.Packet): El paquete capturado.
        """
        self.packet_queue.put(packet)

    def _process_packet_queue(self):
        """
        Procesa la cola de paquetes y actualiza la GUI a un ritmo controlado.

        Este método se ejecuta en el hilo principal de la GUI. Extrae paquetes de la
        cola y los inserta en la lista. Al procesar solo un paquete y luego
        reprogramarse a sí mismo con `self.after`, se asegura que la GUI permanezca
        fluida y receptiva, y que los paquetes aparezcan uno por uno.
        """
        try:
            # Procesa solo UN paquete por ciclo para que aparezcan de uno en uno.
            # Esto hace que la captura sea fácil de seguir para el aprendizaje.
            for _ in range(1): 
                packet = self.packet_queue.get_nowait()
                self._insertar_paquete_en_gui(packet)
        except queue.Empty:
            pass  # La cola está vacía, no hay nada que hacer
        finally:
            # Vuelve a llamar a esta función después de una pausa más larga (en ms).
            # Un valor como 300-500ms permite que el usuario note cada paquete.
            self.update_job = self.after(400, self._process_packet_queue)

    def _insertar_paquete_en_gui(self, packet):
        """
        Inserta un único paquete en el Treeview de la GUI.

        Este método se ejecuta en el hilo principal. Extrae la información resumida
        del paquete y la añade como una nueva fila en el widget `packet_list`.

        Args:
            packet (scapy.packet.Packet): El paquete a mostrar.
        """
        self.captured_packets.append(packet)
        pkt_id = len(self.captured_packets)

        proto, src, dst, info = "N/A", "N/A", "N/A", packet.summary()
        if packet.haslayer(IP):
            src = packet[IP].src
            dst = packet[IP].dst
            if packet.haslayer(TCP):
                proto = "TCP"
            elif packet.haslayer(UDP):
                proto = "UDP"
            else:
                proto = "IP"
        elif packet.haslayer(ARP):
            proto = "ARP"
            src = packet[ARP].psrc
            dst = packet[ARP].pdst

        pkt_time = time.strftime('%H:%M:%S', time.localtime(packet.time))
        values = (pkt_id, pkt_time, src, dst, proto, len(packet), info)

        self.packet_list.insert('', 'end', values=values, iid=str(pkt_id))
        self.packet_list.yview_moveto(1) # Auto-scroll

    def _mostrar_detalles_paquete(self, event):
        """
        Muestra los detalles del paquete seleccionado en el panel de detalles.

        Este es el manejador de eventos para la selección de un item en el Treeview.
        Recupera el objeto de paquete completo de la lista `captured_packets` y
        utiliza `packet.show(dump=True)` para obtener una representación detallada
        en formato de texto, que luego se muestra en el panel inferior.
        """
        try:
            # Asegurarse de que hay una selección
            if not self.packet_list.selection():
                return
            selected_item = self.packet_list.selection()[0]
            packet_id = int(selected_item)
            # El ID del Treeview es 1-based, el índice de la lista es 0-based
            packet = self.captured_packets[packet_id - 1]

            # Usar el método show de Scapy con dump=True para obtener los detalles como string
            details = packet.show(dump=True)

            self.details_text.config(state="normal")
            self.details_text.delete("1.0", tk.END)
            self.details_text.insert(tk.END, details)
            self.details_text.config(state="disabled")
        except (IndexError, ValueError):
            # Ocurre si la selección es inválida (p. ej. al limpiar la lista). Se ignora.
            pass
