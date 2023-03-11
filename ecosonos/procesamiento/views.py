from django.shortcuts import render, redirect
# from .utils.procesos_lluvia import getRutasArchivos, csvReturn, removeRainFiles
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .utils.procesos_lluvia_progress import tipos_grabaciones, procesar_audio, csvReturn, removeRainFiles, getRutasArchivos
from .utils.session_utils import inicializar_variables_session, guardar_grabaciones_session, guardar_raiz_carpeta_session
from .utils.lluvia_edison import algoritmo_lluvia_edison
import numpy as np
from django.contrib import messages
from tkinter.filedialog import askdirectory
import os
from django.http import HttpResponse


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
#                 # plot_polar_indices()
#                 removeRainFiles(
#                     request.session['ruta'], request.session['ruta_csv'])

#             except:
#                 # TODO: agregar flash message
#                 print('debe haber procesado archivos .wav previamente')

#     return render(request, 'procesamiento/preproceso.html')


@csrf_exempt
def lluvia(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            grabaciones, ruta = getRutasArchivos()
            print(grabaciones, ruta)
            n_grabaciones = len(grabaciones)
            PSD_medio = np.zeros((n_grabaciones,))
            PSD_medio = PSD_medio.tolist()

            inicializar_variables_session(
                request, ruta, grabaciones, n_grabaciones, PSD_medio)

    return render(request, 'procesamiento/preproceso.html')


def escoger_carpeta(request):
    if request.method == 'POST':

        if 'cargar' in request.POST:
            carpeta = askdirectory(title='Seleccionar carpeta con audios')
            guardar_raiz_carpeta_session(request, carpeta)

            carpetas = []
            carpetas.append(carpeta)

            for ruta, carpetas_subdir, _ in os.walk(carpeta):
                # Add all directories to the carpetas list
                for carpeta_subdir in carpetas_subdir:
                    carpetas.append(os.path.join(
                        ruta, carpeta_subdir).replace('\\', '/'))

            return render(request, 'procesamiento/lista_carpeta.html', {'carpetas': carpetas})

    return render(request, 'procesamiento/escoger_carpeta.html')


def lista_carpetas(request):
    if request.method == 'POST':
        carpetas = request.POST.getlist('carpetas')

        algoritmo_lluvia_edison(carpetas, request.session['raiz_preproceso'])
        return HttpResponse('Archivos procesados: {}'.format(carpetas))
    else:
        # Return a form to select the files
        return render(request, 'procesamiento/escoger_carpeta.html')
