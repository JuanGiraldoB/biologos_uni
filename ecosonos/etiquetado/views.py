from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json


# Async stuffs
from asgiref.sync import sync_to_async
import asyncio

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz,
    cambiar_diagonales_carpeta,
    selecciono_carpeta
)

from .utils.spectograma import (
    run_calcular_spectrogram,
    spectrogram,
    calcular_espectrograma,
    play_sound
)

from ecosonos.utils.archivos_utils import (
    obtener_archivos_wav,
    reemplazar_caracter
)

from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import mostrar_ventana_encima


@csrf_exempt
def etiquetado(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            if selecciono_carpeta(carpeta_raiz):
                return render(request, 'etiquetado/etiquetado.html')

            guardar_raiz_carpeta_session(
                request, carpeta_raiz, app="etiquetado")

            archivos, nombres_base = obtener_archivos_wav([carpeta_raiz])

            # Reemplazar los '/' por '_' para poder ser usados en la peticion get
            reemplazar_caracter(archivos, caracter='/', reemplazo='-')

            data['archivos'] = zip(archivos, nombres_base)

            return render(request, 'etiquetado/etiquetado.html', data)

    return render(request, 'etiquetado/etiquetado.html')

    # return render(request, 'etiquetado/upload.html')


# async def espectrograma(request, ruta):
#     data = {}

#     carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='etiquetado')
#     archivos, nombres_base = await sync_to_async(obtener_archivos_wav)([carpeta_raiz])
#     await sync_to_async(reemplazar_caracter)(archivos, caracter='/', reemplazo='-')

#     ruta = ruta.replace('-', '/')

    # asyncio.create_task(run_calcular_spectrogram(ruta, carpeta_raiz))
    # f, t, s = await sync_to_async(calcular_espectrograma)(ruta)
    # sync_to_async(play_sound)(ruta, 37, 40)
    # spectrogram(ruta, carpeta_raiz)

    # data['archivos'] = zip(archivos, nombres_base)
    # data['frequencies'] = f.tolist()
    # data['times'] = t.tolist()
    # data['spectrogram'] = s.tolist()
    # data = json.dumps(data)

    # return render(request, 'etiquetado/pruebas.html', data)


def espectrograma(request, ruta):
    data = {}
    carpeta_raiz = obtener_carpeta_raiz(request, app='etiquetado')
    archivos, nombres_base = obtener_archivos_wav([carpeta_raiz])
    reemplazar_caracter(archivos, caracter='/', reemplazo='-')

    ruta = ruta.replace('-', '/')

    f, t, s = calcular_espectrograma(ruta)

    data['frequencies'] = f.tolist()
    data['times'] = t.tolist()
    data['spectrogram'] = s.tolist()

    return render(request, 'etiquetado/etiquetado.html', data)
