from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils.procesos_lluvia import getRutasArchivos
# Create your views here.


def lluvia(request):
    if request.method == 'POST':
        rutas, carpeta = getRutasArchivos()
        print(rutas, carpeta)

    return render(request, 'procesamiento/index.html')
