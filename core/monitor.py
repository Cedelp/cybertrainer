
# monitor.py
# Captura de paquetes - Lógica de monitoreo (usando scapy o pyshark)

from scapy.all import sniff
import scapy.all as scapy
from scapy.all import sniff, conf

def capturar_paquetes(interface, count=15):
    paquetes = sniff(iface=interface, count=count)
    return paquetes