from django.shortcuts import render, redirect
# from .utils.funciones_indices import graficaErrorBar
from .utils.funciones_indices_progress import getRutasArchivos, calcularIndice, csvIndices, graficaErrorBar
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from tkinter.filedialog import askdirectory
import os
import plotly.express as px
from django.urls import reverse

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
                df_means = graficaErrorBar(
                    request.session['carpeta'], request.session['grabaciones'])
                fig = px.bar(df_means, x='Indices',
                             y='mean_DF', error_y='std_DF')
                chart = fig.to_html()
                context = {'chart': chart}
                return render(request, 'indices/indices.html', context)

            except:
                # TODO: add flash message
                print('debe primero cargar datos')
                return redirect(reverse('indices'))

    return render(request, 'indices/indices.html', context)
