import ctypes
import sys
import os
import tkinter as tk
from tkinter import messagebox
from gui.main import App

def npcap_instalado():
    try:
        ctypes.windll.LoadLibrary("wpcap.dll")
        return True
    except Exception:
        return False

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller. """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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

    # Pasamos la ruta del icono de ventana y del icono de menú a la clase principal de la aplicación.
    icon_ventana = resource_path("assets/images/app_icon.ico")
    icon_menu = resource_path("assets/images/app_icon.png")
    app = App(icon_path=icon_ventana, menu_icon_path=icon_menu)
    app.mainloop()

if __name__ == "__main__":
    main()