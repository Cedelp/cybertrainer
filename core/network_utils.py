"""
Módulo de utilidades de red.

Este archivo proporciona funciones para detectar y seleccionar la interfaz de red
más adecuada para la captura de paquetes. La lógica está diseñada para ser robusta
y priorizar las interfaces físicas locales (como Wi-Fi o Ethernet) sobre
interfaces virtuales (como VPNs o adaptadores de software) que podrían no
reflejar el tráfico de red real del usuario.
"""
import sys
from scapy.config import conf
from scapy.arch import get_if_addr
from scapy.arch.windows import get_windows_if_list

def _get_default_route_info():
    """
    Obtiene la interfaz y la IP a través de la ruta por defecto del sistema.

    Este método sirve como un mecanismo de respaldo. Intenta consultar la tabla de
    enrutamiento de Scapy para encontrar la interfaz utilizada para el tráfico
    general de Internet (ruta 0.0.0.0/0). Puede ser menos fiable si hay
    múltiples rutas o configuraciones de red complejas.

    Returns:
        tuple[str | None, str | None]: Una tupla conteniendo el nombre de la interfaz
                                       y su dirección IP, o (None, None) si falla.
    """
    try:
        # Consulta la tabla de enrutamiento para la ruta por defecto.
        default_route_info = conf.route.route("0.0.0.0/0")
        iface_name = default_route_info[0]
        # Una vez que tenemos el nombre, obtenemos su dirección IP.
        ip_address = get_if_addr(iface_name)
        if not ip_address:
            # Es posible que una interfaz no tenga una IP v4 asignada.
            print(f"Advertencia: La interfaz de ruta por defecto '{iface_name}' no tiene una dirección IPv4 asignada.", file=sys.stderr)
        return iface_name, ip_address
    except Exception as e:
        # Esto puede fallar si Scapy no puede determinar la ruta.
        print(f"Error al determinar la ruta por defecto: {e}", file=sys.stderr)
        return None, None

def get_active_network_info():
    """
    Determina la interfaz de red activa y su dirección IPv4.

    Esta función implementa una estrategia de varias etapas para encontrar la mejor
    interfaz para monitorear:
    1.  Primero, busca interfaces que parezcan ser físicas (no VPN, no loopback)
        y que tengan una dirección IP privada (ej. 192.168.x.x). Esto suele
        corresponder a la conexión Wi-Fi o Ethernet principal.
    2.  Si no encuentra una candidata clara, recurre a la función
        `_get_default_route_info` como plan B.

    Returns:
        tuple[str | None, str | None]: Una tupla de (nombre_interfaz, direccion_ip)
                                       o (None, None) si no se encuentra ninguna
                                       interfaz adecuada.
    """
    # Palabras clave para identificar y excluir interfaces virtuales o no deseadas.
    # Esto ayuda a ignorar adaptadores de VPN, VirtualBox, etc.
    EXCLUSION_KEYWORDS = ['loopback', 'vpn', 'tap', 'virtual', 'teredo', 'isatap']
    
    candidate_interfaces = []
    all_interfaces = get_windows_if_list()

    # 1. Filtrar para encontrar interfaces físicas con IPs locales
    for iface in all_interfaces:
        description = iface.get('description', '').lower()
        ip_address = iface.get('ip')
        iface_name = iface.get('name')

        # Omitir si la interfaz no tiene IP, nombre, o si su descripción
        # contiene una de las palabras clave de exclusión.
        if not ip_address or not iface_name:
            continue
        if any(keyword in description for keyword in EXCLUSION_KEYWORDS):
            continue

        # Comprobar si la IP pertenece a los rangos de red privada más comunes.
        # Esto aumenta la probabilidad de que sea una red LAN.
        if ip_address.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.2', '172.30.', '172.31.')):
            candidate_interfaces.append((iface_name, ip_address))

    # Si la estrategia 1 tuvo éxito, devolvemos el primer candidato encontrado.
    if candidate_interfaces:
        iface_name, ip_address = candidate_interfaces[0]
        print(f"Interfaz física local encontrada: {iface_name} ({ip_address})")
        return iface_name, ip_address

    # --- Estrategia 2: Fallback a la ruta por defecto ---
    # Si no se encontró una interfaz local clara, se notifica al usuario y se
    # intenta el método de respaldo.
    print(
        "Advertencia: No se encontró una interfaz de red local estándar (ej. Wi-Fi con IP 192.168.x.x).\n"
        "Esto puede ocurrir si usas una VPN o una red no estándar. Intentando con la ruta por defecto...",
        file=sys.stderr)
    return _get_default_route_info()
