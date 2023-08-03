from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async

from tkinter.filedialog import askdirectory

from .utils.lluvia_edison import run_algoritmo_lluvia_edison
from .utils.procesos_lluvia_progress import grafica_polar
from .models import Progreso
from .utils.plot import obtener_plot


from ecosonos.utils.archivos_utils import (
    mover_archivos_segun_tipo
)

from ecosonos.utils.carpeta_utils import (
    guardar_raiz_carpeta_session,
    obtener_carpeta_raiz,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombres_base
)

from ecosonos.utils.tkinter_utils import mostrar_ventana_encima

from .utils.helper_functions import (
    cargar_carpeta,
    procesar_carpetas,
    mover_archivos,
    mostrar_grafica
)


async def lluvia(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await cargar_carpeta(request)

        elif 'procesar_carpetas' in request.POST:
            return await procesar_carpetas(request)

        elif 'mover_archivos' in request.POST:
            return await mover_archivos(request)

        elif 'mostrar-grafica' in request.POST:
            return await mostrar_grafica(request)

    else:
        return render(request, 'procesamiento/preproceso.html')


@csrf_exempt
def barra_progreso(request):
    progreso = Progreso.objects.first()
    data = {}

    if not progreso:
        data['procentaje_completado'] = 0
        return JsonResponse(data)

    archivos_completados = progreso.archivos_completados
    cantidad_archivos = progreso.cantidad_archivos

    try:
        porcentaje_completado = int(
            (archivos_completados / cantidad_archivos) * 100)
    except:
        porcentaje_completado = 0

    data['procentaje_completado'] = porcentaje_completado

    if archivos_completados == cantidad_archivos:
        Progreso.objects.all().delete()

    return JsonResponse(data)
