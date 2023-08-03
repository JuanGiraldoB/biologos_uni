from django.shortcuts import render
from asgiref.sync import sync_to_async
import pathlib
from tkinter.filedialog import askdirectory
import asyncio
import os

from ..models import Progreso

from .lluvia_edison import run_algoritmo_lluvia_edison
from .plot import obtener_plot

from ecosonos.utils.tkinter_utils import (
    mostrar_ventana_encima
)

from ecosonos.utils.carpeta_utils import (
    selecciono_carpeta,
    guardar_raiz_carpeta_session,
    obtener_subcarpetas,
    subcarpetas_seleccionadas,
    obtener_carpeta_raiz,
    obtener_nombres_base,
    obtener_cantidad_archivos_por_subdir
)

from ecosonos.utils.archivos_utils import (
    mover_archivos_segun_tipo
)


async def cargar_carpeta(request):
    data = {}

    try:
        root = mostrar_ventana_encima()
        carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
        carpeta_raiz = str(pathlib.Path(carpeta_raiz))
        root.destroy()
    except Exception as e:
        print("Error en cargar carpeta")
        return render(request, 'procesamiento/preproceso.html')

    if selecciono_carpeta(carpeta_raiz):
        return render(request, 'procesamiento/preproceso.html')

    await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz)
    carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
    cantidad_archivos_subdir = obtener_cantidad_archivos_por_subdir(
        carpetas_nombre_completo)
    data['carpetas_nombre_completo'] = carpetas_nombre_completo
    data['carpetas_nombre_base'] = carpetas_nombre_base
    data['completo_base_zip'] = zip(
        carpetas_nombre_completo, carpetas_nombre_base, cantidad_archivos_subdir)

    await sync_to_async(Progreso.objects.all().delete)()

    return render(request, 'procesamiento/preproceso.html', data)


async def procesar_carpetas(request):
    data = {}

    carpetas_seleccionadas = request.POST.getlist('carpetas')

    if subcarpetas_seleccionadas(carpetas_seleccionadas):
        return render(request, 'procesamiento/preproceso.html')

    progreso = await sync_to_async(Progreso.objects.create)()
    carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

    asyncio.create_task(run_algoritmo_lluvia_edison(
        carpetas_seleccionadas, carpeta_raiz, progreso))

    carpetas_seleccionadas = obtener_nombres_base(
        carpetas_seleccionadas)
    data['carpetas_procesando'] = carpetas_seleccionadas

    return render(request, 'procesamiento/preproceso.html', data)


async def mover_archivos(request):
    try:
        root = mostrar_ventana_encima()
        carpeta_destino = askdirectory(
            title='Carpeta de destino de audios con lluvia')
        carpeta_destino = str(pathlib.Path(carpeta_destino))
        root.destroy()

    except Exception as e:
        return render(request, 'procesamiento/preproceso.html')

    if selecciono_carpeta(carpeta_destino):
        return render(request, 'procesamiento/preproceso.html')

    tipo_boton = request.POST['mover_archivos']
    tipo_archivos_a_mover = "YES" if "Lluvia" in tipo_boton else "ALTO PSD"

    try:
        carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

        mover_archivos_segun_tipo(
            carpeta_raiz, carpeta_destino, tipo_archivos_a_mover)
    except Exception as e:
        return render(request, 'procesamiento/preproceso.html')

    return render(request, 'procesamiento/preproceso.html')


async def mostrar_grafica(request):
    data = {}
    try:
        carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)
    except Exception as e:
        print(e)
        return render(request, 'procesamiento/preproceso.html')

    if not os.path.exists(carpeta_raiz):
        return render(request, 'procesamiento/preproceso.html')

    grafica = obtener_plot(carpeta_raiz)
    data['grafica'] = grafica

    return render(request, 'procesamiento/preproceso.html', data)
