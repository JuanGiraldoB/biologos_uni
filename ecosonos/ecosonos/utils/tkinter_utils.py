import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename


def show_tkinter_windown_top():
    '''
    Forzar el popup de seleccionar carpeta a aparecer 'encima' de las otras ventanas
    '''
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()

    return root


def get_root_folder():
    root = show_tkinter_windown_top()
    root_folder = askdirectory(title='Seleccionar carpeta raiz')
    root.destroy()
    return root_folder


def get_file():
    root = show_tkinter_windown_top()
    file = askopenfilename(title='Seleccionar archivo csv')
    root.destroy()
    return file
