from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import TableData
import numpy as np
from .Bioacustica_Completo import (
    Metodologia,
    ZscoreMV,
    lamda_unsup,
    segmentacion,
    seleccion_features,
    time_and_date,
    run_metodologia
)
import ast

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    get_selected_subfolders_session,
    get_root_folder_session,
    save_csv_path_session,
    get_csv_path_session
)

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombres_base,
)

from ecosonos.utils.archivos_utils import obtener_detalle_archivos_wav
from procesamiento.models import Progreso
import pandas as pd
from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import show_tkinter_windown_top
import asyncio
from asgiref.sync import sync_to_async


async def cargar_carpeta(request):
    data = {}
    try:
        root = show_tkinter_windown_top()
        carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
        root.destroy()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(TableData.objects.all().delete)()

    if selecciono_carpeta(carpeta_raiz):
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_root_folder_session)(request, carpeta_raiz, app='etiquetado-auto')

    await sync_to_async(Progreso.objects.all().delete)()

    carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)

    data['carpetas_nombre_completo'] = carpetas_nombre_completo
    data['carpetas_nombre_base'] = carpetas_nombre_base
    data['completo_base_zip'] = zip(
        carpetas_nombre_completo, carpetas_nombre_base)

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def procesar_carpetas(request):
    data = {}
    carpetas_seleccionadas = request.POST.getlist('carpetas')

    if subcarpetas_seleccionadas(carpetas_seleccionadas):
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    await sync_to_async(save_selected_subfolders_session)(request, carpetas_seleccionadas,  app='etiquetado-auto')
    carpeta_raiz = await sync_to_async(get_root_folder_session)(request, app='etiquetado-auto')

    archivos_full_dir, archivos_nombre_base = await sync_to_async(obtener_detalle_archivos_wav)(carpetas_seleccionadas)

    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(archivos_full_dir))
    request.session['tabla'] = None
    carpetas_seleccionadas = obtener_nombres_base(
        carpetas_seleccionadas)
    data['carpetas_procesando'] = carpetas_seleccionadas

    canal = 1
    autosel = 0
    visualize = 0
    banda = ["min", "max"]

    nombre_xlsx = 'Tabla_Nuevas_especies'
    for nombre in carpetas_seleccionadas:
        nombre_xlsx += f'_{nombre}'

    nombre_xlsx = f'{carpeta_raiz}/{nombre_xlsx}.xlsx'
    await sync_to_async(save_csv_path_session)(
        request, nombre_xlsx, app='etiquetado-auto')

    asyncio.create_task(run_metodologia(
        archivos_full_dir, archivos_nombre_base, banda, canal, autosel, visualize, progreso, nombre_xlsx))

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def mostrar_tabla(request):
    data = {}
    carpeta_raiz = await sync_to_async(get_root_folder_session)(request, app='etiquetado-auto')
    ruta_xlsx = await sync_to_async(get_csv_path_session)(
        request, app='etiquetado-auto')

    df = pd.read_excel(ruta_xlsx)
    data['df'] = df

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)
