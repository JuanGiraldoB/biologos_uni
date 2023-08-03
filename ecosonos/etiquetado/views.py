from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import os

# Async stuffs
from asgiref.sync import sync_to_async
import asyncio

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz,
    cambiar_diagonales_carpeta,
    selecciono_carpeta,
    guardar_ruta_csv_session,
    obtener_ruta_csv_session,
    guardar_ruta_csv_session,
    obtener_ruta_csv_session
)

from .utils.spectograma import (
    run_calcular_spectrogram,
    spectrogram,
    calcular_espectrograma,
    play_sound
)

from ecosonos.utils.archivos_utils import (
    obtener_detalle_archivos_wav,
    reemplazar_caracter,
    agregar_fila_csv,
    crear_csv,
    agregar_fila_csv
)

from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import mostrar_ventana_encima


@csrf_exempt
def etiquetado(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            if selecciono_carpeta(carpeta_raiz):
                return render(request, 'etiquetado/etiquetado.html')

            guardar_raiz_carpeta_session(
                request, carpeta_raiz, app="etiquetado")

            nombre_carpeta = os.path.basename(carpeta_raiz).split(".")[0]

            csv_ruta = crear_csv(carpeta_raiz, nombre_carpeta)
            guardar_ruta_csv_session(request, csv_ruta)

            # xlsx_ruta = crear_xlsx(carpeta_raiz)
            # guardar_ruta_csv_session(request, xlsx_ruta, app='etiquetado')

            archivos, nombres_base = obtener_detalle_archivos_wav([
                                                                  carpeta_raiz])

            # Reemplazar los '/' por '-' para poder ser usados en la peticion get
            reemplazar_caracter(archivos, caracter='/', reemplazo='-')

            data['archivos'] = zip(archivos, nombres_base)

            return render(request, 'etiquetado/etiquetado.html', data)

    return render(request, 'etiquetado/etiquetado.html')


def espectrograma(request, ruta):
    data = {}
    carpeta_raiz = obtener_carpeta_raiz(request, app='etiquetado')
    archivos, nombres_base = obtener_detalle_archivos_wav([carpeta_raiz])
    reemplazar_caracter(archivos, caracter='/', reemplazo='-')

    data['ruta'] = ruta
    ruta = ruta.replace('-', '/')

    f, t, s = calcular_espectrograma(ruta)

    data['frequencies'] = f.tolist()
    data['times'] = t.tolist()
    data['spectrogram'] = s.tolist()
    data['nombre'] = os.path.basename(ruta)
    data['archivos'] = zip(archivos, nombres_base)

    return render(request, 'etiquetado/etiquetado.html', data)


# @csrf_exempt
def reproducir_sonido_archivo(request, ruta):
    ruta = ruta.replace('-', '/')

    data = json.loads(request.body)
    etiqueta = data.get('etiqueta')

    # Tiempos
    x0 = data.get('x0')
    x1 = data.get('x1')

    # Frecuencias
    y0 = data.get('y0')
    y1 = data.get('y1')

    nombre_grabacion = os.path.basename(ruta)
    csv_ruta = obtener_ruta_csv_session(request)
    agregar_fila_csv(csv_ruta, nombre_grabacion, etiqueta, x0, x1, y0, y1)
    play_sound(ruta, x0, x1)

    return render(request, 'etiquetado/etiquetado.html')
