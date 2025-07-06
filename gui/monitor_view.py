import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from core.monitor import capturar_paquetes
import psutil
from scapy.utils import wrpcap, rdpcap
from core.simulador import simular_ataque


class MonitorViewFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=parent.cget("bg"))

        tk.Label(self, text="Monitor de Red", font=("Arial", 18), bg=self.cget("bg")).pack(pady=10)

        # Entrada de interfaz (Combobox)
        entry_frame = tk.Frame(self, bg=self.cget("bg"))
        entry_frame.pack(pady=5)
        tk.Label(entry_frame, text="Interfaz de red:", bg=self.cget("bg")).pack(side="left")

        interfaces = list(psutil.net_if_addrs().keys())
        self.interface_var = tk.StringVar()
        self.interface_combo = ttk.Combobox(entry_frame, textvariable=self.interface_var, values=interfaces, state="readonly")
        if interfaces:
            self.interface_combo.current(0)
        self.interface_combo.pack(side="left", padx=5)

        # Frame principal para botones
        buttons_main_frame = tk.Frame(self, bg=self.cget("bg"))
        buttons_main_frame.pack(pady=5)

        # Todos los botones en la misma fila
        self.btn_frame = tk.Frame(buttons_main_frame, bg=self.cget("bg"))
        self.btn_frame.pack(pady=5)

        self.boton_capturar = tk.Button(self.btn_frame, text="Capturar paquetes", command=self.iniciar_captura)
        self.boton_capturar.pack(side="left", padx=5)

        self.boton_guardar = tk.Button(self.btn_frame, text="Guardar a .pcap", command=self.guardar_paquetes, state="disabled")
        self.boton_guardar.pack(side="left", padx=5)

        self.boton_cargar = tk.Button(self.btn_frame, text="Cargar .pcap", command=self.cargar_pcap)
        self.boton_cargar.pack(side="left", padx=5)

        self.boton_limpiar = tk.Button(self.btn_frame, text="Limpiar", command=self.limpiar_paquetes)
        self.boton_limpiar.pack(side="left", padx=5)

        # Etiqueta para los ataques
        tk.Label(self.btn_frame, text="Simular ataques:", bg=self.cget("bg")).pack(side="left", padx=10)

        self.boton_syn = tk.Button(self.btn_frame, text="Escaneo SYN", command=lambda: self.simular_ataque_gui("Escaneo SYN"))
        self.boton_syn.pack(side="left", padx=5)

        self.boton_udp = tk.Button(self.btn_frame, text="Flood UDP", command=lambda: self.simular_ataque_gui("Flood UDP"))
        self.boton_udp.pack(side="left", padx=5)

        self.boton_arp = tk.Button(self.btn_frame, text="Spoofing ARP", command=lambda: self.simular_ataque_gui("Spoofing ARP"))
        self.boton_arp.pack(side="left", padx=5)

        # Lista de paquetes
        self.lista = tk.Listbox(self, width=100, height=20)
        self.lista.pack(pady=10)
        self.lista.bind("<<ListboxSelect>>", self.mostrar_detalles)

        self.paquetes = []  # Aquí guardamos los objetos Scapy

    def iniciar_captura(self):
        interfaz = self.interface_var.get()
        stats = psutil.net_if_stats()
        if interfaz not in stats or not stats[interfaz].isup:
            messagebox.showerror(
                "Interfaz inactiva",
                "La interfaz seleccionada está desactivada o no es compatible.\n"
                "Por favor, elige una interfaz activa."
            )
            return

        self.boton_capturar.config(state="disabled")
        self.lista.delete(0, tk.END)
        self.paquetes = []

        def capturar():
            try:
                self.paquetes = capturar_paquetes(interface=interfaz, count=15)
                for pkt in self.paquetes:
                    self.lista.insert(tk.END, pkt.summary())
                self.boton_guardar.config(state="normal" if self.paquetes else "disabled")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Error de captura",
                    f"No se pudo capturar en la interfaz seleccionada.\n\n"
                    f"Verifica que la interfaz esté activa y sea compatible.\n\n"
                    f"Detalle técnico: {e}"
                ))
            finally:
                self.after(0, lambda: self.boton_capturar.config(state="normal"))

        threading.Thread(target=capturar, daemon=True).start()

    def mostrar_detalles(self, event):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        pkt = self.paquetes[index]
        detalles = pkt.show(dump=True)

        ventana = tk.Toplevel(self)
        ventana.title("Detalles del Paquete")
        ventana.geometry("600x400")
        text_area = tk.Text(ventana, wrap="none")
        text_area.insert("1.0", detalles)
        text_area.config(state="disabled")
        text_area.pack(fill="both", expand=True)

    def guardar_paquetes(self):
        if not self.paquetes:
            messagebox.showwarning("Sin paquetes", "No hay paquetes para guardar.")
            return

        archivo = filedialog.asksaveasfilename(defaultextension=".pcap", filetypes=[("PCAP files", "*.pcap")])
        if archivo:
            wrpcap(archivo, self.paquetes)
            messagebox.showinfo("Éxito", f"Paquetes guardados en:\n{archivo}")

    def cargar_pcap(self):
        archivo = filedialog.askopenfilename(filetypes=[("PCAP files", "*.pcap")])
        if not archivo:
            return
        try:
            self.paquetes = rdpcap(archivo)
            self.lista.delete(0, tk.END)
            for pkt in self.paquetes:
                self.lista.insert(tk.END, pkt.summary())
            self.boton_guardar.config(state="normal" if self.paquetes else "disabled")
            messagebox.showinfo("Cargado", f"Se cargaron {len(self.paquetes)} paquetes desde el archivo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def limpiar_paquetes(self):
        self.paquetes = []
        self.lista.delete(0, tk.END)
        self.boton_guardar.config(state="disabled")