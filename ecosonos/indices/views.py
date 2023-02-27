from django.shortcuts import render, redirect
from .utils.funciones_indices import calcularIndice, graficaErrorBar
from django.http import JsonResponse
from tkinter.filedialog import askdirectory
import os
import plotly.express as px
from django.urls import reverse

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
                return redirect(reverse('indices'))

            try:
                carpeta = askdirectory(title='Seleccionar carpeta con audios')
                archivos = os.listdir(carpeta)
                carpeta, grabaciones = calcularIndice(
                    selected_features, carpeta, archivos)
                request.session['carpeta'] = carpeta
                request.session['grabaciones'] = grabaciones

            except:
                # TODO: add flash message
                print("Debe seleccionar una carpeta o existen audios corruptos")

            finally:
                return redirect(reverse('indices'))

        if 'mostrar-grafica' in request.POST:
            try:
                df_means = graficaErrorBar(
                    request.session['carpeta'], request.session['grabaciones'])
                fig = px.bar(df_means, x='Indices',
                             y='mean_DF', error_y='std_DF')
                # fig = px.bar(x_pos)
                chart = fig.to_html()
                context = {'chart': chart}
                return render(request, 'indices/indices.html', context)

            except:
                # TODO: add flash message
                print('debe primero cargar datos')
                return redirect(reverse('indices'))

    return render(request, 'indices/indices.html', context)
