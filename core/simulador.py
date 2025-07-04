
# simulator.py
# Simulación de ataques - DDoS, ARP spoofing, etc. (en modo educativo)

import time
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import ARP
from scapy.sendrecv import send
from scapy.packet import Raw

def simular_ataque(tipo):
    if tipo == "Escaneo SYN":
        for puerto in range (80, 85):
            pkt = IP(dst="127.0.0.1")/TCP(dport=puerto, flags="S")
            send(pkt, verbose=False)

    elif tipo == "Flood UDP":
        for _ in range(50):
            pkt = IP(dst="127.0.0.1")/UDP(dport=123)/Raw(load="FLOOD")
            send(pkt, verbose=False)

    elif tipo == "Spoofing ARP":
        pkt = ARP(op=2, pdst="127.0.0.1", hwdst="ff:ff:ff:ff:ff:ff", psrc="192.168.1.1")
        send(pkt, verbose=False)

    else:
        raise ValueError("Ataque no soportado.")

def simular_ddos():
    print("[*] Simulando ataque DDoS...")
    for i in range(5):
        print(f"[!] Ataque simulado #{i+1} - Múltiples peticiones enviadas")
        time.sleep(1)
    print("[*] Fin de simulación DDoS.")

def simular_arp_spoofing():
    print("[*] Simulando ataque ARP Spoofing...")
    print("[!] Paquetes ARP falsos enviados a la red")
    print("[*] Fin de simulación ARP Spoofing.")