from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TableData
import numpy as np
from .utils.Bioacustica_Completo import (
    Metodologia,
    ZscoreMV,
    lamda_unsup,
    segmentacion,
    seleccion_features,
    time_and_date,
    run_metodologia
)
import ast

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombres_base,
    guardar_ruta_csv_session,
    obtener_ruta_csv_session
)

from ecosonos.utils.archivos_utils import obtener_detalle_archivos_wav
from procesamiento.models import Progreso
import pandas as pd
from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import mostrar_ventana_encima
import asyncio
from asgiref.sync import sync_to_async


async def etiquetado_auto(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            await sync_to_async(TableData.objects.all().delete)()

            if selecciono_carpeta(carpeta_raiz):
                return render(request, "etiquetado_auto/etiquetado-auto.html")

            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz, app='etiquetado-auto')

            await sync_to_async(Progreso.objects.all().delete)()

            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)

            data['carpetas_nombre_completo'] = carpetas_nombre_completo
            data['carpetas_nombre_base'] = carpetas_nombre_base
            data['completo_base_zip'] = zip(
                carpetas_nombre_completo, carpetas_nombre_base)

            return render(request, "etiquetado_auto/etiquetado-auto.html", data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')

            if subcarpetas_seleccionadas(carpetas_seleccionadas):
                return render(request, "etiquetado_auto/etiquetado-auto.html", data)

            await sync_to_async(guardar_carpetas_seleccionadas)(request, carpetas_seleccionadas,  app='etiquetado-auto')
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='etiquetado-auto')

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
            await sync_to_async(guardar_ruta_csv_session)(
                request, nombre_xlsx, app='etiquetado-auto')

            asyncio.create_task(run_metodologia(
                archivos_full_dir, archivos_nombre_base, banda, canal, autosel, visualize, progreso, nombre_xlsx))

            return render(request, "etiquetado_auto/etiquetado-auto.html", data)

        elif 'mostrar-tabla' in request.POST:
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='etiquetado-auto')
            ruta_xlsx = await sync_to_async(obtener_ruta_csv_session)(
                request, app='etiquetado-auto')

            df = pd.read_excel(ruta_xlsx)
            data['df'] = df

            return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    return render(request, "etiquetado_auto/etiquetado-auto.html")


@csrf_exempt
def barra_progreso(request):
    progreso = Progreso.objects.first()
    data = {}

    if not progreso:
        data['procentaje_completado'] = 0
        return JsonResponse(data)

    archivos_completados = progreso.archivos_completados
    cantidad_archivos = progreso.cantidad_archivos

    try:
        porcentaje_completado = int(
            (archivos_completados / cantidad_archivos) * 100)
    except:
        porcentaje_completado = 0

    data['procentaje_completado'] = porcentaje_completado

    if archivos_completados == cantidad_archivos:
        Progreso.objects.all().delete()

    return JsonResponse(data)
