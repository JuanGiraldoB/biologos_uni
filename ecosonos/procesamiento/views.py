from django.shortcuts import render, redirect
# from .utils.procesos_lluvia import getRutasArchivos, csvReturn, removeRainFiles
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .utils.procesos_lluvia_progress import tipos_grabaciones, procesar_audio, csvReturn, removeRainFiles, getRutasArchivos
from .utils.lluvia_edison import algoritmo_lluvia_edison, run_algoritmo_lluvia_edison
import numpy as np
from django.contrib import messages
from tkinter.filedialog import askdirectory
import os
from django.http import HttpResponse
import asyncio
from asgiref.sync import sync_to_async

from .models import Progreso


from ecosonos.utils.archivos_utils import (
    mover_archivos_lluvia
)

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz
)


# @csrf_exempt
# def lluvia(request):
#     if request.method == 'POST':
#         if 'cargar' in request.POST:
#             try:
#                 print("cargando archivos")
#                 grabaciones, ruta = getRutasArchivos()
#                 n_grabs = len(grabaciones)
#                 request.session['ruta'] = ruta
#                 request.session['grabaciones'] = grabaciones
#                 request.session['n_grab'] = n_grabs
#                 request.session['index'] = 0
#                 PSD_medio = np.zeros((n_grabs,))
#                 PSD_medio = PSD_medio.tolist()
#                 request.session['PSD_medio'] = PSD_medio
#                 print('archivos cargados')

#             except:
#                 # TODO: agregar flash message
#                 messages.success(request, 'Your message goes here')
#                 print('debe seleccionar una carpeta')

#         elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             try:
#                 index = request.session['index']
#                 n_grab = request.session['n_grab']
#                 grabaciones = request.session['grabaciones']
#                 PSD_medio = request.session['PSD_medio']

#                 data = {'progress': index, 'max': n_grab}

#                 if index == n_grab:
#                     g_buenas, g_malas, cond_malas = [], [], []
#                     g_buenas, g_malas, cond_malas = tipos_grabaciones(
#                         grabaciones, PSD_medio)
#                     csv_ruta = csvReturn(request.session['ruta'],
#                                          request.session['grabaciones'], cond_malas, request)

#                     print("dasdas")
#                     request.session['ruta_csv'] = csv_ruta

#                     return JsonResponse(data)

#                 grabacion = grabaciones[index]
#                 PSD_medio[index] = procesar_audio(grabacion)

#                 request.session['index'] = index + 1
#                 print(f'Procesada {grabacion}[{index}]')

#                 return JsonResponse(data)

#             except:
#                 # TODO: agregar flash message
#                 print(
#                     'debe seleccionar una carpeta previamente o existen archivos corruptos')

#         else:
#             try:
#                 removeRainFiles(
#                     request.session['ruta'], request.session['ruta_csv'])

#             except:
#                 # TODO: agregar flash message
#                 print('debe haber procesado archivos .wav previamente')

#     return render(request, 'procesamiento/preproceso.html')


async def lluvia(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz)
            carpetas = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            carpetas.insert(0, carpeta_raiz)
            data['carpetas'] = carpetas

            await sync_to_async(Progreso.objects.all().delete)()

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')

            progreso = await sync_to_async(Progreso.objects.create)()
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

            data = {}
            data['carpetas'] = carpetas_seleccionadas
            data['procesando'] = 'true'

            asyncio.create_task(run_algoritmo_lluvia_edison(
                carpetas_seleccionadas, carpeta_raiz, progreso))

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'mover_archivos' in request.POST:
            carpeta_destino = askdirectory(
                title='Carpeta de destino de audios con lluvia')
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

            mover_archivos_lluvia(carpeta_raiz, carpeta_destino)
            return render(request, 'procesamiento/preproceso.html')
    else:
        return render(request, 'procesamiento/preproceso.html')


@csrf_exempt
def barra_progreso(request):
    progreso = Progreso.objects.first()
    data = {}

    if not progreso:
        data['progreso'] = "terminado"
        data['max'] = "terminado"
        return JsonResponse(data)

    archivos_completados = progreso.archivos_completados
    cantidad_archivos = progreso.cantidad_archivos
    data['progreso'] = archivos_completados
    data['max'] = cantidad_archivos

    # print("cat", archivos_completados, cantidad_archivos)
    if archivos_completados == cantidad_archivos:
        Progreso.objects.all().delete()

    return JsonResponse(data)
