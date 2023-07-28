from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import asyncio
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
    obtener_subcarpetas,
    guardar_raiz_carpeta_session,
    obtener_carpeta_raiz,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombre_base
)

from ecosonos.utils.tkinter_utils import mostrar_ventana_encima


async def lluvia(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            if selecciono_carpeta(carpeta_raiz):
                return render(request, 'procesamiento/preproceso.html')

            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz)
            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            data['carpetas_nombre_completo'] = carpetas_nombre_completo
            data['carpetas_nombre_base'] = carpetas_nombre_base
            data['completo_base_zip'] = zip(
                carpetas_nombre_completo, carpetas_nombre_base)

            await sync_to_async(Progreso.objects.all().delete)()

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')

            if subcarpetas_seleccionadas(carpetas_seleccionadas):
                return render(request, 'procesamiento/preproceso.html')

            progreso = await sync_to_async(Progreso.objects.create)()
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)

            asyncio.create_task(run_algoritmo_lluvia_edison(
                carpetas_seleccionadas, carpeta_raiz, progreso))

            carpetas_seleccionadas = obtener_nombre_base(
                carpetas_seleccionadas)
            data['carpetas_procesando'] = carpetas_seleccionadas

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'mover_archivos' in request.POST:

            try:
                root = mostrar_ventana_encima()
                carpeta_destino = askdirectory(
                    title='Carpeta de destino de audios con lluvia')
                root.destroy()

            except Exception as e:
                return render(request, 'procesamiento/preproceso.html')

            if selecciono_carpeta(carpeta_destino):
                return render(request, 'procesamiento/preproceso.html')

            tipo_boton = request.POST['mover_archivos']
            tipo_archivos_a_mover = "YES" if "Lluvia" in tipo_boton else "ALTO PSD"

            try:
                carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

                mover_archivos_segun_tipo(
                    carpeta_raiz, carpeta_destino, tipo_archivos_a_mover)
            except Exception as e:
                return render(request, 'procesamiento/preproceso.html')

            return render(request, 'procesamiento/preproceso.html')

        elif 'mostrar-grafica' in request.POST:
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)
            grafica = obtener_plot(carpeta_raiz)
            data['grafica'] = grafica

            return render(request, 'procesamiento/preproceso.html', data)

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
