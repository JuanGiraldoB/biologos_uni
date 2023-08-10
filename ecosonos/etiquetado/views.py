from django.shortcuts import render
import os


from .utils.spectograma import (
    reproducir_segmento,
)

from .utils.helper_functions import (
    cargar_carpeta,
    mostrar_pagina_etiquetado,
    etiquetar,
    obtener_data_segmento
)


def etiquetado(request):
    if request.method == 'POST':
        return cargar_carpeta(request)

    return render(request, 'etiquetado/etiquetado.html')


def espectrograma(request, ruta):
    return mostrar_pagina_etiquetado(request, ruta)


def reproducir_sonido_archivo(request, ruta):
    ruta = ruta.replace('-', os.sep)

    data_segemento = obtener_data_segmento(request)
    etiquetar(request, ruta, data_segemento)
    reproducir_segmento(ruta, data_segemento['x0'], data_segemento['x1'])

    return render(request, 'etiquetado/etiquetado.html')
