from django.shortcuts import render, redirect
from .utils.funciones_indices_progress import getRutasArchivos, calcularIndice, csvIndices, graficaErrorBar, grafica_polar
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from tkinter.filedialog import askdirectory
from django.urls import reverse
from django.contrib import messages
from asgiref.sync import sync_to_async
import asyncio
from .utils.funciones_indices import calcular_indice, run_calcular_indice
from .utils.session_utils import guardar_indices_session, obtener_indices_session
from ecosonos.utils.archivos_utils import obtener_archivos_wav
from ecosonos.utils.tkinter_utils import mostrar_ventana_encima
from procesamiento.models import Progreso

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz
)

from ecosonos.utils.tkinter_utils import mostrar_ventana_encima

# Create your views here.


async def app(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz, app='indices')

            indices_seleccionados = request.POST.getlist('options')
            await sync_to_async(guardar_indices_session)(request, indices_seleccionados)

            await sync_to_async(Progreso.objects.all().delete)()

            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            data['carpetas_nombre_completo'] = carpetas_nombre_completo
            data['carpetas_nombre_base'] = carpetas_nombre_base
            data['completo_base_zip'] = zip(
                carpetas_nombre_completo, carpetas_nombre_base)

            return render(request, 'indices/indices.html', data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')
            await sync_to_async(guardar_carpetas_seleccionadas)(request, carpetas_seleccionadas,  app='indices')
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='indices')
            indices_seleccionados = await sync_to_async(obtener_indices_session)(request)

            archivos = await sync_to_async(obtener_archivos_wav)(carpetas_seleccionadas)

            progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(archivos))

            asyncio.create_task(run_calcular_indice(
                indices_seleccionados, carpeta_raiz, archivos, progreso))

            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            data['carpetas_nombre_completo'] = carpetas_nombre_completo
            data['carpetas_nombre_base'] = carpetas_nombre_base
            data['completo_base_zip'] = zip(
                carpetas_nombre_completo, carpetas_nombre_base)

            return render(request, 'indices/indices.html', data)

        if 'mostrar-grafica' in request.POST:
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='indices')
            carpetas_seleccionadas = await sync_to_async(obtener_carpetas_seleccionadas)(request, app='indices')
            archivos = await sync_to_async(obtener_archivos_wav)(carpetas_seleccionadas)

            grafica = await sync_to_async(grafica_polar)(carpeta_raiz, archivos)

            context = {'grafica': grafica}
            return render(request, 'indices/indices.html', context)
    else:
        return render(request, 'indices/indices.html')


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
