from django.shortcuts import render, redirect
from .utils.funciones_indices_progress import getRutasArchivos, calcularIndice, csvIndices, graficaErrorBar, grafica_polar
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from tkinter.filedialog import askdirectory
import os
import plotly.express as px
from django.urls import reverse
import plotly.express as px
import pandas as pd
from django.contrib import messages
from django.http import HttpResponse
from asgiref.sync import sync_to_async
import asyncio
from .utils.funciones_indices import calcular_indice, run_calcular_indice
from .utils.session_utils import guardar_indices_session, obtener_indices_session
from ecosonos.utils.archivos_utils import obtener_archivos_wav
from procesamiento.models import Progreso

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz
)

# Create your views here.


async def indices(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz, indices=True)

            carpetas = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            carpetas.insert(0, carpeta_raiz)

            indices_seleccionados = request.POST.getlist('options')
            await sync_to_async(guardar_indices_session)(request, indices_seleccionados)

            await sync_to_async(Progreso.objects.all().delete)()

            data['carpetas'] = carpetas
            return render(request, 'indices/indices.html', data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')
            await sync_to_async(guardar_carpetas_seleccionadas)(request, carpetas_seleccionadas,  indices=True)
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, indices=True)
            indices_seleccionados = await sync_to_async(obtener_indices_session)(request)

            archivos = await sync_to_async(obtener_archivos_wav)(carpetas_seleccionadas)

            progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(archivos))

            asyncio.create_task(run_calcular_indice(
                indices_seleccionados, carpeta_raiz, archivos, progreso))

            data['carpetas'] = carpetas_seleccionadas

            return render(request, 'indices/indices.html', data)

        if 'mostrar-grafica' in request.POST:
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, indices=True)
            carpetas_seleccionadas = await sync_to_async(obtener_carpetas_seleccionadas)(request, indices=True)
            archivos = await sync_to_async(obtener_archivos_wav)(carpetas_seleccionadas)

            grafica = await sync_to_async(grafica_polar)(carpeta_raiz, archivos)

            context = {'grafica': grafica}
            return render(request, 'indices/indices.html', context)

    return render(request, 'indices/indices.html')


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

    print(
        f'completados: {archivos_completados}/terminados: {cantidad_archivos}')

    data['progreso'] = archivos_completados
    data['max'] = cantidad_archivos

    if archivos_completados == cantidad_archivos:
        print(f'completado')
        Progreso.objects.all().delete()

    return JsonResponse(data)
