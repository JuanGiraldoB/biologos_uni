from django.shortcuts import render, redirect
from .utils.funciones_indices_progress import getRutasArchivos, calcularIndice, csvIndices, graficaErrorBar
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


@csrf_exempt
def indices(request):
    chart = ''
    context = {'chart': chart}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            indices_seleccionados = request.POST.getlist('options')

            if len(indices_seleccionados) == 0:
                # TODO: add flash message
                print("debe seleccionar al menos un indice")
                return redirect(reverse('indices'))

            try:
                print("cargando archivos")
                grabaciones, ruta = getRutasArchivos()
                n_grabs = len(grabaciones)
                request.session['indices_seleccionados'] = indices_seleccionados
                request.session['n_grab_indices'] = n_grabs
                request.session['index_indices'] = 0
                request.session['ruta_indices'] = ruta
                # Audios seleccionados
                request.session['grabaciones_indices'] = grabaciones
                # Indices calculados por grabacion
                request.session['grab_ind_calculados'] = []
                Valores = list()
                for i in range(len(indices_seleccionados) + 1):
                    Valores.append(list())

                request.session['valores'] = Valores

            except:
                # TODO: add flash message
                print("Debe seleccionar una carpeta o existen audios corruptos")

            finally:
                return redirect(reverse('indices'))

        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # elif 'procesar' in request.POST:

            print("Procesando...")

            Valores = request.session['valores']
            grabaciones = request.session['grabaciones_indices']
            indices_seleccionados = request.session['indices_seleccionados']
            ruta = request.session['ruta_indices']
            index = request.session['index_indices']
            n_grab = request.session['n_grab_indices']

            data = {'progress': index, 'max': n_grab}

            if index == n_grab:
                print("terminado")
                csvIndices(Valores, ruta, indices_seleccionados)
                return JsonResponse(data)

            grabacion = grabaciones[index]
            calcularIndice(indices_seleccionados,
                           ruta, grabacion, Valores)

            print(Valores)
            request.session['index_indices'] = index + 1
            request.session['valores'] = Valores
            return JsonResponse(data)

        if 'mostrar-grafica' in request.POST:
            try:
                print(request.session['ruta_indices'])
                df_means = graficaErrorBar(
                    request.session['ruta_indices'], request.session['grabaciones_indices'])
                fig = px.bar(df_means, x='Indices',
                             y='mean_DF', error_y='std_DF')
                # df = pd.read_csv(
                #     request.session['carpeta'] + "/Indices_acusticos_G21A.csv")
                # fig = px.bar_polar(df, r='hora', theta='fecha', color='ACIft', hover_data=['hora'],
                #                    template='plotly_dark', title='ACIft vs. fecha')

                chart = fig.to_html()
                context = {'chart': chart}
                return render(request, 'indices/indices.html', context)

            except Exception as e:
                # TODO: add flash message
                print(e)
                print('debe primero cargar datos')
                return redirect(reverse('indices'))

    return render(request, 'indices/indices.html', context)


async def lluvia_carpeta(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz, indices=True)

            carpetas = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            carpetas.insert(0, carpeta_raiz)

            indices_seleccionados = request.POST.getlist('options')
            await sync_to_async(guardar_indices_session)(request, indices_seleccionados)

            data['carpetas'] = carpetas
            await sync_to_async(Progreso.objects.all().delete)()
            return render(request, 'indices/indices.html', data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)
            indices_seleccionados = await sync_to_async(obtener_indices_session)(request)

            archivos = await sync_to_async(obtener_archivos_wav)(carpetas_seleccionadas)

            progreso = await sync_to_async(Progreso.objects.create)()
            progreso.cantidad_archivos = len(archivos)

            asyncio.create_task(run_calcular_indice(
                indices_seleccionados, carpeta_raiz, archivos))

            data = {}
            data['carpetas'] = carpetas_seleccionadas

            # asyncio.create_task(run_algoritmo_lluvia_edison(
            #     carpetas_seleccionadas, carpeta_raiz, progreso))

            return render(request, 'indices/indices.html', data)

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
    data['progreso'] = archivos_completados
    data['max'] = cantidad_archivos

    # print("cat", archivos_completados, cantidad_archivos)
    if archivos_completados == cantidad_archivos:
        Progreso.objects.all().delete()

    return JsonResponse(data)
