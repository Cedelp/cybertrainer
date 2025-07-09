"""
Punto de entrada principal de la aplicación CyberTrainer.

Este script es el responsable de iniciar la aplicación. Realiza las siguientes tareas:
1.  Verifica si Npcap, una dependencia crítica para la captura de paquetes en
    Windows, está instalado. Si no lo está, muestra un mensaje de error y sale.
2.  Define una función para manejar correctamente las rutas a los recursos
    (como los iconos), asegurando que funcione tanto en un entorno de desarrollo
    como en el ejecutable final creado por PyInstaller.
3.  Instancia y lanza la ventana principal de la aplicación (`gui.main.App`).
"""
import ctypes
import sys
import os
import tkinter as tk
from tkinter import messagebox
from gui.main import App

def npcap_instalado():
    """
    Verifica si la librería de Npcap (wpcap.dll) está accesible en el sistema.

    Intenta cargar la DLL `wpcap.dll`. Si tiene éxito, significa que Npcap
    (o su predecesor WinPcap) está instalado y es accesible.

    Returns:
        bool: True si la DLL se puede cargar, False en caso contrario.
    """
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