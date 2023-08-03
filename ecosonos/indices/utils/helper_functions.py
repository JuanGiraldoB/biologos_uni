from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilename
from asgiref.sync import sync_to_async
import asyncio
import pathlib

from .session_utils import guardar_indices_session, obtener_indices_session
from ecosonos.utils.archivos_utils import (
    obtener_detalle_archivos_wav,
    selecciono_archivo,
    reemplazar_caracter,
    guardar_session_detalle_archivos,
    obtener_session_detalle_archivos,
    obtener_archivos_carpetas
)
from ecosonos.utils.tkinter_utils import mostrar_ventana_encima
from procesamiento.models import Progreso
from .funciones_indices_progress import grafica_polar
from .funciones_indices import run_calcular_indice
from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombres_base
)


async def cargar_carpeta(request):
    data = {}

    try:
        root = mostrar_ventana_encima()
        carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
        carpeta_raiz = str(pathlib.Path(carpeta_raiz))
        root.destroy()
    except Exception as e:
        print("Error en cargar carpeta en indices")
        return render(request, 'indices/indices.html')

    if selecciono_carpeta(carpeta_raiz):
        return render(request, 'indices/indices.html')

    await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz, app='indices')

    indices_seleccionados = request.POST.getlist('options')

    if not indices_seleccionados:
        return render(request, 'indices/indices.html')

    await sync_to_async(guardar_indices_session)(request, indices_seleccionados)

    await sync_to_async(Progreso.objects.all().delete)()

    carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)

    archivos, nombres_base, cantidad_archivos_subdir, duracion_archivos_subdir, fecha_archivos_subdir = obtener_detalle_archivos_wav(
        carpetas_nombre_completo)

    detalle_archivos = [archivos, nombres_base, cantidad_archivos_subdir,
                        duracion_archivos_subdir, fecha_archivos_subdir]

    await sync_to_async(guardar_session_detalle_archivos)(request, detalle_archivos, app='indices')

    data['carpetas_nombre_completo'] = carpetas_nombre_completo
    data['carpetas_nombre_base'] = carpetas_nombre_base
    data['completo_base_zip'] = zip(
        carpetas_nombre_completo, carpetas_nombre_base, cantidad_archivos_subdir, duracion_archivos_subdir, fecha_archivos_subdir)

    return render(request, 'indices/indices.html', data)


async def procesar_carpetas(request):
    data = {}
    carpetas_seleccionadas = request.POST.getlist('carpetas')

    if subcarpetas_seleccionadas(carpetas_seleccionadas):
        return render(request, 'indices/indices.html', data)

    await sync_to_async(guardar_carpetas_seleccionadas)(request, carpetas_seleccionadas,  app='indices')
    carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='indices')
    indices_seleccionados = await sync_to_async(obtener_indices_session)(request)

    archivos = obtener_archivos_carpetas(carpetas_seleccionadas)

    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(archivos))

    asyncio.create_task(run_calcular_indice(
        indices_seleccionados, carpeta_raiz, archivos, progreso))

    carpetas_seleccionadas = obtener_nombres_base(
        carpetas_seleccionadas)
    data['carpetas_procesando'] = carpetas_seleccionadas

    return render(request, 'indices/indices.html', data)


async def mostrar_grafica(request):
    try:
        carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='indices')
        # carpetas_seleccionadas = await sync_to_async(obtener_carpetas_seleccionadas)(request, app='indices')
        indices_seleccionados = await sync_to_async(obtener_indices_session)(request)
        detalle_archivos = await sync_to_async(obtener_session_detalle_archivos)(request, app='indices')
        archivos = detalle_archivos[0]

    except Exception as e:
        print(e, "sss")
        return render(request, 'indices/indices.html')

    try:
        graficas = []
        for indice in indices_seleccionados:

            if "ADIm" == indice:
                continue

            graficas.append(await sync_to_async(grafica_polar)(carpeta_raiz, archivos, indice))

        if "ADIm" in indices_seleccionados:
            adim = []
            for i in range(30):
                adim_i = f'ADIm_{i}'
                adim.append(adim_i)
                graficas.append(await sync_to_async(grafica_polar)(carpeta_raiz, archivos, indice, adim_i))

    # Exception occurs when there are less ADIm_{i} than in the for range
    except Exception as e:
        indices_seleccionados.remove("ADIm")
        indices_seleccionados.extend(adim)
        print(e)

    zipped = zip(graficas, indices_seleccionados)
    context = {'graficas': graficas,
               'indices': indices_seleccionados, 'zipped': zipped}

    return render(request, 'indices/indices.html', context)


async def cargar_csv(request):
    try:
        root = mostrar_ventana_encima()
        archivo = askopenfilename(
            title='Seleccionar archivo csv')
        root.destroy()
    except Exception as e:
        print("Error cargar csv")
        return render(request, 'indices/indices.html')

    if selecciono_archivo(archivo):
        return render(request, 'indices/indices.html')

    df = pd.read_csv(archivo)
    indices = df.columns[1:-1].to_list()

    graficas = []
    for indice in indices:

        if "ADIm" == indice:
            continue

        graficas.append(await sync_to_async(grafica_polar)(archivo, "archivos", indice))

    zipped = zip(graficas, indices)
    context = {'graficas': graficas,
               'indices': indices, 'zipped': zipped}

    return render(request, 'indices/indices.html', context)
