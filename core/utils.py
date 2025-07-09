"""
Módulo de utilidades generales.

Este archivo contiene funciones auxiliares que pueden ser utilizadas por
diferentes partes del núcleo (`core`) de la aplicación. Su objetivo es
centralizar lógica común que no pertenece a un módulo específico como
`monitor` o `simulador`.
"""

def formatear_paquete(pkt):
    """
    Genera una representación de texto simple de un paquete de Scapy.

    Args:
        pkt (scapy.packet.Packet): El paquete de Scapy a formatear.

    Returns:
        str: Un resumen del paquete si el método `summary()` está disponible,
             de lo contrario, la representación de string del paquete.
    """
    return pkt.summary() if hasattr(pkt, 'summary') else str(pkt)

def log_evento(mensaje):
    """
    Escribe un mensaje de log en un archivo de texto.

    Abre (o crea) el archivo `log_eventos.txt` y añade el mensaje proporcionado
    en una nueva línea.

    Args:
        mensaje (str): El mensaje que se escribirá en el log.
    """
    with open("log_eventos.txt", "a") as f:
        f.write(mensaje + "\n")
