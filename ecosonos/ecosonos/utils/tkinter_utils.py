import tkinter as tk


def mostrar_ventana_encima():
    '''
    Forzar el popup de seleccionar carpeta a aparecer 'encima' de las otras ventanas
    '''
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()

    return root
