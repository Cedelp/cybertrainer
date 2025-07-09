"""
Módulo de monitoreo de red.

Este archivo contiene la lógica principal para la captura de paquetes de red.
Utiliza la librería Scapy para realizar el sniffing de tráfico en una interfaz
de red específica. Proporciona una clase `PacketCaptor` que encapsula la
captura en un hilo separado para no bloquear la interfaz gráfica, y funciones
auxiliares para listar las interfaces de red disponibles.
"""

from scapy.all import sniff
from scapy.arch.windows import get_windows_if_list
import threading

class PacketCaptor:
    """
    Gestiona la captura de paquetes de red en un hilo de ejecución separado.

    Esta clase permite iniciar y detener la captura de paquetes de forma asíncrona,
    lo que es esencial para no congelar la interfaz de usuario de la aplicación.
    Cada paquete capturado se pasa a una función `packet_callback` para su
    procesamiento.
    """
    def __init__(self, interface, packet_callback):
        """
        Inicializa el capturador de paquetes.

        Args:
            interface (str): El nombre de la interfaz de red en la que se capturarán
                             los paquetes (ej. 'Ethernet', 'Wi-Fi').
            packet_callback (function): La función que se llamará por cada paquete
                                        capturado. Esta función recibirá el paquete
                                        como único argumento.
        """
        self.interface = interface
        self.packet_callback = packet_callback
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        """
        Inicia la captura de paquetes en un nuevo hilo (demonio).
        
        El hilo se configura como demonio para que no impida que el programa
        principal finalice.
        """
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        """
        Método privado que se ejecuta en el hilo de captura.
        
        Llama a la función `sniff` de Scapy, que es bloqueante. El sniffing se
        detendrá cuando el `stop_event` sea activado.
        """
        sniff(iface=self.interface, prn=self.packet_callback, stop_filter=lambda p: self.stop_event.is_set())

    def stop(self):
        """Señaliza al hilo de captura para que se detenga de forma segura."""
        self.stop_event.set()

def get_network_interfaces():
    """
    Obtiene y devuelve una lista de nombres de las interfaces de red disponibles.

    Utiliza la función `get_windows_if_list` de Scapy, específica para sistemas
    Windows, para recuperar todas las interfaces de red.

    Returns:
        list[str]: Una lista de strings, donde cada string es el nombre de una
                   interfaz de red válida.
    """
    interfaces = get_windows_if_list()
    return [iface['name'] for iface in interfaces if iface.get('name')]

def get_loopback_interface():
    """
    Encuentra y devuelve el nombre de la interfaz de loopback de Npcap.

    Esta interfaz es especial y es necesaria para capturar tráfico que se genera
    y se consume en la misma máquina, un caso de uso clave para el simulador
    de ataques.

    Returns:
        str or None: El nombre de la interfaz de loopback de Npcap si se encuentra,
                     de lo contrario, devuelve None.
    """
    for iface in get_windows_if_list():
        if iface.get('description', '').lower().startswith('npcap loopback adapter'):
            return iface.get('name')
    return None