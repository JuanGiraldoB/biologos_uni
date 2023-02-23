from django.shortcuts import render, redirect
from .utils.procesos_lluvia import getRutasArchivos, algoritmo_lluvia, csvReturn, removeRainFiles
# Create your views here.


def lluvia(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            g_buenas, g_malas, cond_malas = [], [], []
            grabaciones, ruta = getRutasArchivos()
            request.session['ruta'] = ruta
            grab_buenas, grab_malas, cond_malas = algoritmo_lluvia(grabaciones)
            csvReturn(ruta, grabaciones, cond_malas, request)

        else:
            removeRainFiles(
                request.session['ruta'], request.session['ruta_csv'])

    return render(request, 'procesamiento/preprocesos.html')
