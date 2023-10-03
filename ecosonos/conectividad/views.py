from django.shortcuts import render
from .utils.helper_functions import conectivity_map_view


def conectividad(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return conectivity_map_view(request)

    return render(request, 'conectividad/conectividad.html')
