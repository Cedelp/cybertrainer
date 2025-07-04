
# utils.py
# Funciones auxiliares para el núcleo

def formatear_paquete(pkt):
    return pkt.summary() if hasattr(pkt, 'summary') else str(pkt)

def log_evento(mensaje):
    with open("log_eventos.txt", "a") as f:
        f.write(mensaje + "\n")
