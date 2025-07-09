import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
from gui.main import App

def npcap_instalado():
    try:
        ctypes.windll.LoadLibrary("wpcap.dll")
        return True
    except Exception:
        return False

def main():
    """Función principal para verificar dependencias y lanzar la aplicación."""
    if not npcap_instalado():
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal de tkinter
        messagebox.showerror(
            "Npcap no encontrado",
            "Para capturar paquetes necesitas instalar Npcap.\n\n"
            "Descárgalo gratis desde:\nhttps://nmap.org/npcap/\n\n"
            "Durante la instalación, marca la opción de compatibilidad con WinPcap."
        )
        sys.exit(1)

    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()