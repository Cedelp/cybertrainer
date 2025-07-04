import ctypes
import tkinter as tk
from tkinter import messagebox
from gui.main import App

def npcap_instalado():
    try:
        ctypes.windll.LoadLibrary("wpcap.dll")
        return True
    except Exception:
        return False

if not npcap_instalado():
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Npcap no encontrado",
        "Para capturar paquetes necesitas instalar Npcap.\n\n"
        "Descárgalo gratis desde:\nhttps://nmap.org/npcap/\n\n"
        "Durante la instalación, marca la opción de compatibilidad con WinPcap."
    )
    exit(1)

if __name__ == "__main__":
    app = App()
    app.mainloop()