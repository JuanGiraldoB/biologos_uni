import pandas as pd
import shutil
import os


def mover_archivos_lluvia(carpeta_raiz, carpeta_destino):
    ruta_xlsx = f'{carpeta_raiz}/resultado.xlsx'
    xlsx_file = pd.read_excel(ruta_xlsx)

    for _, row in xlsx_file.iterrows():
        ruta_archivo = row['path_FI']
        lluvia = row['rain_FI']

        if lluvia == 'YES':
            shutil.move(ruta_archivo, carpeta_destino)


def obtener_archivos_wav(carpetas):
    archivos = []
    formatos = ['wav', 'WAV']

    for carpeta in carpetas:
        for archivo in os.listdir(carpeta):
            file_name = os.path.join(
                carpeta, archivo).replace('\\', '/')

            # Verifica que sea un archivo y que la extension corresponda con las de la variable formatos
            if os.path.isfile(file_name):
                file_extension = file_name.split(".")[1]

                if file_extension in formatos:
                    archivos.append(file_name)

    return archivos
