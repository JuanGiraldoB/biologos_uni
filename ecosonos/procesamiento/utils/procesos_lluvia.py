# from tkinter import *
# from tkinter import filedialog
from tkinter.filedialog import askdirectory
import os


def getRutasArchivos():
    """Obtiene las rutas de los archivos de audio con extension .WAV
    de la carpeta indicada por el usuario

    :return: Lista con las rutas de los archivos de audio con
    extension .WAV
    :rtype: list
    """

    rutas = []
    carpeta = askdirectory(title='Seleccionar carpeta con audios')
    archivos = os.listdir(carpeta)
    for archivo in archivos:
        # archivo = archivo.lower()
        # incluir los tipos de archivo de audio que soporta sf
        if archivo[-4:] == ".wav" or archivo[-4:] == ".WAV":
            rutas.append(carpeta + "/" + archivo)

    return rutas, carpeta
