import pandas as pd
import shutil
import os
from datetime import datetime
import csv
import openpyxl as xl

from .carpeta_utils import guardar_ruta_csv_session


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
    formatos = ['wav', 'WAV', 'mp3']
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


def crear_csv(carpeta_raiz):
    csv_ruta = os.path.join(carpeta_raiz, 'etiquetas.csv')
    if not os.path.exists(csv_ruta):
        with open(csv_ruta, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["etiqueta", "t_min", "t_max", "f_min", "f_max"])

    return csv_ruta


def agregar_fila_csv(csv_ruta, etiqueta, x0, x1, y0, y1):
    with open(csv_ruta, "a", newline='') as file:
        writer = csv.writer(file)

        fila = [etiqueta, x0, x1, y0, y1]
        writer.writerow(fila)


def crear_xlsx(carpeta_raiz):
    base = os.path.basename(carpeta_raiz)
    nombre = f'etiquetas-{base}.xlsx'
    xlsx_ruta = os.path.join(carpeta_raiz, nombre).replace('\\', '/')

    print(xlsx_ruta)
    if not os.path.exists(xlsx_ruta):
        wb = xl.Workbook()
        wb.save(xlsx_ruta)
        wb.close()

    return xlsx_ruta


def crear_hoja_xlsx(xlsx_ruta, nombre_archivo):
    wb = xl.load_workbook(filename=xlsx_ruta)  # wb = workbook
    nombre_hojas = wb.sheetnames

    if nombre_archivo in nombre_hojas:
        ws = wb[nombre_archivo]
    else:
        ws = wb.create_sheet(title=nombre_archivo)
        ws.append(["etiqueta,t_min,t_max,f_min,f_max"])

    if "Sheet" in nombre_hojas:
        del wb["Sheet"]

    wb.save(xlsx_ruta)
    wb.close()


def agregar_fila_xlsx(xlsx_ruta, nombre_archivo, etiqueta, x0, x1, y0, y1):
    wb = xl.load_workbook(filename=xlsx_ruta)  # wb = workbook
    ws = wb[nombre_archivo]

    fila = [f"{etiqueta},{x0},{x1},{y0},{y1}"]
    ws.append(fila)

    wb.save(xlsx_ruta)
    wb.close()


def selecciono_archivo(archivo):
    """
        Verifica si fue seleccionada una carpeta
    """
    return not archivo
