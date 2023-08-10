import tkinter as tk


def show_tkinter_windown_top():
    '''
    Forzar el popup de seleccionar carpeta a aparecer 'encima' de las otras ventanas
    '''
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()

    return root
