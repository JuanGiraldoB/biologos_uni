from django.shortcuts import render
from .utils.spectograma import run_spectogram
from easygui import diropenbox
from easygui import fileopenbox
import os

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz,
    cambiar_diagonales_carpeta
)

# Create your views here.


def etiquetado(request):
    if request.method == 'POST':
        if 'resultados' in request.POST:
            carpeta_raiz = diropenbox(
                title='Seleccionar carpeta')
            carpeta_raiz = cambiar_diagonales_carpeta(carpeta_raiz)

            guardar_raiz_carpeta_session(
                request, carpeta_raiz, app='etiquetado')

        if 'cargar' in request.POST:
            ruta_audio = fileopenbox(
                title='Seleccionar archivo', msg='.wav', filetypes=['*.wav'])
            carpeta_raiz = obtener_carpeta_raiz(request, app='etiquetado')

            run_spectogram(ruta_audio, carpeta_raiz)
    return render(request, 'etiquetado/etiquetado.html')
