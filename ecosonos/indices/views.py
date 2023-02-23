from django.shortcuts import render
from .utils.funciones_indices import calcularIndice, graficaErrorBar
from django.http import JsonResponse
from tkinter.filedialog import askdirectory
import os
import plotly.express as px

# Create your views here.


def indices(request):
    chart = ''
    context = {'chart': chart}

    if request.method == 'POST':
        if 'seleccionar-carpeta' in request.POST:
            selected_features = request.POST.getlist('options')

            if len(selected_features) == 0:
                # TODO: add flash message
                print("debe seleccionar al menos un indice")
                return render(request, 'indices/indices.html')
            try:
                carpeta = askdirectory(title='Seleccionar carpeta con audios')
                archivos = os.listdir(carpeta)
            except:
                # TODO: add flash message
                print("Debe seleccionar una carpeta")
                return render(request, 'indices/indices.html')

            carpeta, grabaciones = calcularIndice(
                selected_features, carpeta, archivos)

            request.session['carpeta'] = carpeta
            request.session['grabaciones'] = grabaciones
            print('dasdas', request.session['carpeta'])
            print('dasdas', request.session['grabaciones'])

        if 'mostrar-grafica' in request.POST:
            try:
                df_means = graficaErrorBar(
                    request.session['carpeta'], request.session['grabaciones'])
                fig = px.bar(df_means, x='Indices',
                             y='mean_DF', error_y='std_DF')
                # fig = px.bar(x_pos)
                chart = fig.to_html()
                context = {'chart': chart}
            except:
                # TODO: add flash message
                print('debe primero cargar datos')

    return render(request, 'indices/indices.html', context)
