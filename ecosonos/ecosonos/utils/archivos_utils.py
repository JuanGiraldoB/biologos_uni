import pandas as pd
import shutil
import os
from datetime import datetime


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
    nombres_base = []

    for carpeta in carpetas:
        for archivo in os.listdir(carpeta):
            file_name = os.path.join(
                carpeta, archivo).replace('\\', '/')

            # Verifica que sea un archivo y que la extension corresponda con las de la variable formatos
            if os.path.isfile(file_name):
                file_extension = file_name.split(".")[1]
                if file_extension in formatos:
                    nombre_base = os.path.basename(file_name)
                    nombres_base.append(nombre_base)
                    archivos.append(file_name)

    return archivos, nombres_base


def reemplazar_caracter(archivos, caracter, reemplazo):
    for i in range(len(archivos)):
        archivos[i] = archivos[i].replace(caracter, reemplazo)


def obtener_fecha(archivo):
    archivo_partes = archivo.split('_')
    fecha = archivo_partes[-2]
    hora = archivo_partes[-1]

    print(f'partes archivo: {archivo_partes}', end='\n\n')

    yy = int(fecha[0:4])
    mm = int(fecha[4:6])
    dd = int(fecha[6:8])

    hh = int(hora[0:2])
    min = int(hora[2:4])
    ss = int(hora[4:6])

    date = datetime(year=yy, month=mm, day=dd, hour=hh, minute=min, second=ss,
                    microsecond=0)

    return date
