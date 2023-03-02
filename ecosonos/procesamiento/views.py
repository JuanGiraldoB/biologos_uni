from django.shortcuts import render, redirect
from .utils.procesos_lluvia import getRutasArchivos, csvReturn, removeRainFiles
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .utils.procesos_lluvia_progress import tipos_grabaciones, procesar_audio
import numpy as np
# Create your views here.


@csrf_exempt
def lluvia(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            try:
                print("cargando archivos")
                grabaciones, ruta = getRutasArchivos()
                n_grabs = len(grabaciones)
                request.session['ruta'] = ruta
                request.session['grabaciones'] = grabaciones
                request.session['n_grab'] = n_grabs
                request.session['index'] = 0
                PSD_medio = np.zeros((n_grabs,))
                PSD_medio = PSD_medio.tolist()
                request.session['PSD_medio'] = PSD_medio
                print('archivos cargados')

            except:
                # TODO: agregar flash message
                print('debe seleccionar una carpeta')

            finally:
                return redirect(reverse('preproceso'))

        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                index = request.session['index']
                n_grab = request.session['n_grab']
                grabaciones = request.session['grabaciones']
                PSD_medio = request.session['PSD_medio']

                data = {'progress': index, 'max': n_grab}

                if index == n_grab:
                    g_buenas, g_malas, cond_malas = [], [], []
                    g_buenas, g_malas, cond_malas = tipos_grabaciones(
                        grabaciones, PSD_medio)
                    csv_ruta = csvReturn(request.session['ruta'],
                                         request.session['grabaciones'], cond_malas, request)

                    request.session['ruta_csv'] = csv_ruta

                    return JsonResponse(data)

                grabacion = grabaciones[index]
                PSD_medio[index] = procesar_audio(grabacion)

                request.session['index'] = index + 1
                print(f'Procesada {grabacion}[{index}]')

                return JsonResponse(data)

            except:
                # TODO: agregar flash message
                print(
                    'debe seleccionar una carpeta previamente o existen archivos corruptos')

        else:
            try:
                removeRainFiles(
                    request.session['ruta'], request.session['ruta_csv'])

            except:
                # TODO: agregar flash message
                print('debe haber procesado archivos .wav previamente')

            finally:
                return redirect(reverse('preproceso'))

    return render(request, 'procesamiento/preproceso.html')
