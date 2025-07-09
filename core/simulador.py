"""
Módulo del simulador de ataques de red.

Este archivo contiene la lógica para generar paquetes que simulan diversos
tipos de ataques de red (Escaneo SYN, Flood UDP, etc.). Está diseñado para
ser un entorno seguro y educativo.

Punto clave de diseño: Los paquetes generados aquí NO se envían a la red real
utilizando funciones como `sendp` de Scapy. En su lugar, se pasan a una
función `packet_callback` que los "inyecta" directamente en la interfaz gráfica
para su visualización y análisis, garantizando que la simulación no tenga
impacto en la red del usuario.
"""

import time
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether
from scapy.packet import Raw

# --- Constantes de Simulación ---
# Estas direcciones IP y MAC son ficticias y se utilizan para que los paquetes
# simulados sean fácilmente identificables en la captura.
FAKE_ATTACKER_IP = "192.168.200.100"
FAKE_ATTACKER_MAC = "00:11:22:33:44:55"
FAKE_TARGET_MAC = "AA:BB:CC:DD:EE:FF"

def simular_ataque(tipo, target_ip, packet_callback, stop_event, log_callback=None):
    """
    Genera y procesa paquetes para simular un ataque de red específico.

    Args:
        tipo (str): El nombre del ataque a simular (ej. "Escaneo SYN").
        target_ip (str): La dirección IP del objetivo simulado.
        packet_callback (function): Función a la que se le pasará cada paquete
                                    generado para ser mostrado en la GUI.
        stop_event (threading.Event): Evento que, al ser activado, detendrá la
                                      generación de paquetes de forma prematura.
        log_callback (function, optional): Función para enviar mensajes de log
                                           a la GUI. Si es None, imprime en consola.
    """
    def log(mensaje):
        """Función auxiliar para registrar logs en la GUI o en la consola."""
        if log_callback:
            log_callback(mensaje + "\n")
        else:
            print(mensaje)

    def enviar_paquete(pkt):
        """
        "Envía" un paquete a la GUI a través del callback.

        Esta función no transmite el paquete a la red. Simplemente lo pasa
        a la función de callback proporcionada. Incluye una pequeña pausa
        para que la simulación sea visualmente más lenta y fácil de seguir.

        Args:
            pkt (scapy.packet.Packet): El paquete a "enviar".
        """
        if packet_callback:
            packet_callback(pkt)
        time.sleep(0.2)  # Pausa para que los paquetes se muestren de forma gradual

    # --- Lógica de Simulación por Tipo de Ataque ---

    if tipo == "Escaneo SYN":
        log("[*] Lanzando escaneo SYN...")
        for puerto in range(80, 85):
            if stop_event.is_set():
                log("[!] Ataque detenido por el usuario.")
                break
            pkt = Ether(src=FAKE_ATTACKER_MAC, dst=FAKE_TARGET_MAC)/IP(src=FAKE_ATTACKER_IP, dst=target_ip)/TCP(dport=puerto, flags="S")
            enviar_paquete(pkt)
            log(f"  > Paquete SYN generado para el puerto {puerto}")
        else: # Se ejecuta solo si el bucle no fue interrumpido por 'break'
            log("[*] Escaneo SYN completado.")

    elif tipo == "Flood UDP":
        log("[*] Iniciando Flood UDP...")
        for i in range(50):
            if stop_event.is_set():
                log("[!] Ataque detenido por el usuario.")
                break
            pkt = Ether(src=FAKE_ATTACKER_MAC, dst=FAKE_TARGET_MAC)/IP(src=FAKE_ATTACKER_IP, dst=target_ip)/UDP(dport=123)/Raw(load="FLOOD")
            enviar_paquete(pkt)
            if i % 10 == 0:
                log(f"  > {i} paquetes UDP generados...")
        else:
            log("[*] Flood UDP finalizado.")

    elif tipo == "Spoofing ARP":
        log(f"[*] Enviando paquetes ARP falsos hacia {target_ip}...")
        for i in range(5):
            if stop_event.is_set():
                log("[!] Ataque detenido por el usuario.")
                break
            # Se simula una respuesta ARP (op=2) donde el atacante (FAKE_ATTACKER_MAC)
            # afirma tener la IP de un gateway común (192.168.1.1).
            pkt = Ether(src=FAKE_ATTACKER_MAC, dst="ff:ff:ff:ff:ff:ff")/ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc="192.168.1.1")
            enviar_paquete(pkt)
            log(f"  > Paquete ARP Spoof generado ({i+1}/5)")
        else:
            log("[*] Spoofing ARP finalizado.")

    elif tipo == "DDoS Simulado":
        log("[*] Simulando ataque DDoS UDP...")
        for i in range(100):
            if stop_event.is_set():
                log("[!] Ataque detenido por el usuario.")
                break
            pkt = Ether(src=FAKE_ATTACKER_MAC, dst=FAKE_TARGET_MAC)/IP(src=FAKE_ATTACKER_IP, dst=target_ip)/UDP(dport=80)/Raw(load="DDoS" * 10)
            enviar_paquete(pkt)
            if i % 20 == 0:
                log(f"  > {i} paquetes DDoS generados")
        else:
            log("[*] DDoS finalizado.")

    else:
        raise ValueError("Ataque no soportado.")
