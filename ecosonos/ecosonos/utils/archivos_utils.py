import pandas as pd
import shutil
import os
import pathlib
from datetime import datetime
import csv
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor


# def save_files_detail_session(request, detalle_archivos, app='preproceso'):
#     if app == 'indices':
#         request.session['detalle_archivos_indices'] = detalle_archivos
#     else:
#         request.session['detalle_archivos_preproceso'] = detalle_archivos


# def get_files_detail_session(request, app='preproceso'):
#     if app == 'indices':
#         return request.session['detalle_archivos_indices']
#     else:
#         return request.session['detalle_archivos_preproceso']


def move_files_depending_type(root_folder, destination_folder, type):
    csv_path = os.path.join(root_folder, 'resultado_preproceso.csv')
    csv_file = pd.read_csv(csv_path)

    for _, row in csv_file.iterrows():
        file_path = row['path_FI']
        lluvia = row['rain_FI']

        if lluvia == type:
            shutil.move(file_path, destination_folder)


def get_file_length(file):
    file = AudioSegment.from_file(file)
    return int(len(file) / 1000)


def get_files_range_length(files):
    files_length = []

    for file in files:
        file = AudioSegment.from_file(file)
        length = int(len(file) / 1000)
        files_length.append(length)

    return (min(files_length), max(files_length))


def obtener_rango_duracion_archivos(duracion_archivos):
    return (min(duracion_archivos), max(duracion_archivos))


def get_date_range_files(fecha_archivos):
    # min_date = min(fecha_archivos)
    # max_date = max(fecha_archivos)

    # min_date = min_date.strftime("%d-%m-%Y")
    # max_date = max_date.strftime("%d-%m-%Y")
    # return (min_date, max_date)
    return (min(fecha_archivos), max(fecha_archivos))


def obtener_archivos_carpetas(carpetas):
    archivos_wav = []
    nombres_base = []

    for carpeta in carpetas:
        for root, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.lower().endswith('.wav'):
                    archivo_path = os.path.join(root, archivo)
                    archivos_wav.append(archivo_path)

                    nombres_base.append(os.path.basename(archivo))

    return archivos_wav, nombres_base


def procesar_carpeta(carpeta):
    archivos = []
    nombres_base = []
    cantidad_archivos_carpeta = []
    duracion_archivos_carpeta = []
    fecha_archivos_carpeta = []

    contador_archivos_carpeta = 0

    for archivo in os.listdir(carpeta):
        dir_archivo = pathlib.Path(os.path.join(carpeta, archivo))

        if os.path.isfile(dir_archivo) and dir_archivo.suffix.lower() == ".wav":
            # Obtener y guardar nombre base
            nombre_base = os.path.basename(dir_archivo)
            nombres_base.append(nombre_base)

            # Guardar direccion completa archivo
            archivos.append(str(dir_archivo))

            # Obtener y guardar duracion del archivo por carpeta
            duracion_archivos_carpeta.append(
                get_file_length(dir_archivo))

            # Obtener y guardar fecha del archivo por carpeta
            fecha_archivo = get_date_from_filename(nombre_base)
            # fecha_formato = fecha_archivo.strftime("%d-%m-%Y")
            fecha_archivos_carpeta.append(fecha_archivo)

            contador_archivos_carpeta += 1

    if duracion_archivos_carpeta:
        rango_duracion = obtener_rango_duracion_archivos(
            duracion_archivos_carpeta)
    else:
        rango_duracion = "Sin duracion"

    if fecha_archivos_carpeta:
        fecha_min, fecha_max = get_date_range_files(
            fecha_archivos_carpeta)
        fecha_min_formato = fecha_min.strftime("%d-%m-%Y")
        fecha_max_formato = fecha_max.strftime("%d-%m-%Y")

        rango_fecha = (fecha_min_formato, fecha_max_formato)
    else:
        rango_fecha = "Sin fechas"

    cantidad_archivos_carpeta.append(contador_archivos_carpeta)

    return archivos, nombres_base, cantidad_archivos_carpeta, rango_duracion, rango_fecha


def obtener_detalle_archivos_wav(carpetas):
    archivos = []
    nombres_base = []
    cantidad_archivos_carpeta = []
    rango_duracion_archivos_carpetas = []
    rango_fechas_archivos_carpetas = []

    with ThreadPoolExecutor() as executor:
        results = executor.map(procesar_carpeta, carpetas)

        for result in results:
            archivos.extend(result[0])
            nombres_base.extend(result[1])
            cantidad_archivos_carpeta.extend(result[2])
            rango_duracion_archivos_carpetas.append(result[3])
            rango_fechas_archivos_carpetas.append(result[4])

    return archivos, nombres_base, cantidad_archivos_carpeta, rango_duracion_archivos_carpetas, rango_fechas_archivos_carpetas


def reemplazar_caracter(archivos, caracter, reemplazo):
    for i in range(len(archivos)):
        archivos[i] = archivos[i].replace(caracter, reemplazo)


def get_date_range_from_filenames(files):
    dates = []
    for file in files:
        dates.append(get_date_from_filename(file))

    min_date = min(dates)
    max_date = max(dates)

    min_date = min_date.strftime("%d-%m-%Y")
    max_date = max_date.strftime("%d-%m-%Y")
    return (min_date, max_date)


def get_date_from_filename(file):

    if "." in file:
        file = pathlib.Path(file).stem

    file_parts = file.split('_')
    fecha = file_parts[-2]
    hora = file_parts[-1]

    yy = int(fecha[0:4])
    mm = int(fecha[4:6])
    dd = int(fecha[6:8])

    hh = int(hora[0:2])
    min = int(hora[2:4])
    ss = int(hora[4:6])

    date = datetime(year=yy, month=mm, day=dd, hour=hh, minute=min, second=ss,
                    microsecond=0)

    return date


def crear_csv(carpeta_raiz, nombre_carpeta):
    nombre_csv = f'etiquetas_{nombre_carpeta}.csv'
    csv_ruta = os.path.join(carpeta_raiz, nombre_csv)

    if not os.path.exists(csv_ruta):
        with open(csv_ruta, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["grabacion", "etiqueta", "t_min",
                            "t_max", "f_min", "f_max"])

    return csv_ruta


def agregar_fila_csv(csv_ruta, nombre_grabacion, etiqueta, x0, x1, y0, y1):
    with open(csv_ruta, "a", newline='') as file:
        writer = csv.writer(file)

        fila = [nombre_grabacion, etiqueta, x0, x1, y0, y1]
        writer.writerow(fila)


# def crear_xlsx(carpeta_raiz):
#     base = os.path.basename(carpeta_raiz)
#     nombre = f'etiquetas-{base}.xlsx'
#     xlsx_ruta = os.path.join(carpeta_raiz, nombre).replace('\\', '/')

#     print(xlsx_ruta)
#     if not os.path.exists(xlsx_ruta):
#         wb = xl.Workbook()
#         wb.save(xlsx_ruta)
#         wb.close()

#     return xlsx_ruta


# def crear_hoja_xlsx(xlsx_ruta, nombre_archivo):
#     wb = xl.load_workbook(filename=xlsx_ruta)  # wb = workbook
#     nombre_hojas = wb.sheetnames

#     if nombre_archivo in nombre_hojas:
#         ws = wb[nombre_archivo]
#     else:
#         ws = wb.create_sheet(title=nombre_archivo)
#         ws.append(["etiqueta,t_min,t_max,f_min,f_max"])

#     if "Sheet" in nombre_hojas:
#         del wb["Sheet"]

#     wb.save(xlsx_ruta)
#     wb.close()


# def agregar_fila_csv(csv_ruta, nombre_archivo, etiqueta, x0, x1, y0, y1):
#     wb = xl.load_workbook(filename=csv_ruta)
#     ws = wb[nombre_archivo]

#     fila = [f"{etiqueta},{x0},{x1},{y0},{y1}"]
#     ws.append(fila)

#     wb.save(csv_ruta)
#     wb.close()


def selecciono_archivo(archivo):
    """
        Verifica si fue seleccionada un archivo
    """
    return not archivo
