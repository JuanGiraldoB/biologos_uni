from django.shortcuts import render
import json
import os
import pathlib

from ecosonos.utils.session_utils import (
    save_root_folder_session,
    get_root_folder_session,
    save_csv_path_session,
    get_csv_path_session,
    save_csv_path_session,
    get_csv_path_session
)

from ecosonos.utils.carpeta_utils import (
    selecciono_carpeta,
)

from .spectograma import (
    calcular_espectrograma,
)

from ecosonos.utils.archivos_utils import (
    obtener_detalle_archivos_wav,
    reemplazar_caracter,
    agregar_fila_csv,
    crear_csv,
    agregar_fila_csv,
    obtener_archivos_carpetas
)

from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import show_tkinter_windown_top


def cargar_carpeta(request):
    data = {}

    try:
        root = show_tkinter_windown_top()
        carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
        carpeta_raiz = str(pathlib.Path(carpeta_raiz))
        root.destroy()
    except Exception as e:
        print("Error en cargar carpeta")
        return render(request, 'etiquetado/etiquetado.html')

    if selecciono_carpeta(carpeta_raiz):
        return render(request, 'etiquetado/etiquetado.html')

    save_root_folder_session(
        request, carpeta_raiz, app="etiquetado")

    nombre_carpeta = os.path.basename(carpeta_raiz).split(".")[0]

    csv_ruta = crear_csv(carpeta_raiz, nombre_carpeta)
    save_csv_path_session(request, csv_ruta)

    archivos, nombres_base, = obtener_archivos_carpetas([
        carpeta_raiz])

    # Reemplazar los '/' por '-' para poder ser usados en la peticion get
    reemplazar_caracter(archivos, caracter=os.sep, reemplazo='-')

    data['archivos'] = zip(archivos, nombres_base)

    return render(request, 'etiquetado/etiquetado.html', data)


def preparar_datos_etiquetado(request, ruta):
    carpeta_raiz = get_root_folder_session(request, app='etiquetado')
    archivos, nombres_base = obtener_archivos_carpetas([carpeta_raiz])
    reemplazar_caracter(archivos, caracter=os.sep, reemplazo='-')

    data = {}
    data['ruta'] = ruta
    ruta = ruta.replace('-', os.sep)

    f, t, s = calcular_espectrograma(ruta)

    data['frequencies'] = f.tolist()
    data['times'] = t.tolist()
    data['spectrogram'] = s.tolist()
    data['nombre'] = os.path.basename(ruta)
    data['archivos'] = zip(archivos, nombres_base)

    return data


def mostrar_pagina_etiquetado(request, ruta):
    data = preparar_datos_etiquetado(request, ruta)
    return render(request, 'etiquetado/etiquetado.html', data)


def etiquetar(request, ruta, data_segmento):
    nombre_grabacion = os.path.basename(ruta)
    csv_ruta = get_csv_path_session(request)
    agregar_fila_csv(csv_ruta, nombre_grabacion,
                     data_segmento['etiqueta'],
                     data_segmento['x0'],
                     data_segmento['x1'],
                     data_segmento['y0'],
                     data_segmento['y1']
                     )


def obtener_data_segmento(request):
    data = json.loads(request.body)
    etiqueta = data.get('etiqueta')

    # Tiempos
    x0 = data.get('x0')
    x1 = data.get('x1')

    # Frecuencias
    y0 = data.get('y0')
    y1 = data.get('y1')

    data_segmento = {
        'x0': x0,
        'x1': x1,
        'y0': y0,
        'y1': y1,
        'etiqueta': etiqueta
    }

    return data_segmento
