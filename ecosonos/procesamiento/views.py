from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from tkinter.filedialog import askdirectory
import asyncio
from asgiref.sync import sync_to_async

from .utils.lluvia_edison import run_algoritmo_lluvia_edison
from .models import Progreso


from ecosonos.utils.archivos_utils import (
    mover_archivos_lluvia
)

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_raiz_carpeta_session,
    obtener_carpeta_raiz
)


async def lluvia(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')

            if not carpeta_raiz:
                messages.error(request, 'Debe seleccionar la carpeta raiz')
                return render(request, 'procesamiento/preproceso.html')

            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz)
            carpetas = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            carpetas.insert(0, carpeta_raiz)
            data['carpetas'] = carpetas

            await sync_to_async(Progreso.objects.all().delete)()

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')

            progreso = await sync_to_async(Progreso.objects.create)()
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

            data = {}
            data['carpetas'] = carpetas_seleccionadas
            data['procesando'] = 'true'

            asyncio.create_task(run_algoritmo_lluvia_edison(
                carpetas_seleccionadas, carpeta_raiz, progreso))

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'mover_archivos' in request.POST:
            try:
                carpeta_destino = askdirectory(
                    title='Carpeta de destino de audios con lluvia')

                if not carpeta_destino:
                    messages.error(request, 'Cancelo la selección de carpeta')
                    return render(request, 'procesamiento/preproceso.html')

                carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

                mover_archivos_lluvia(carpeta_raiz, carpeta_destino)
                return render(request, 'procesamiento/preproceso.html')
            except:
                messages.error(
                    request, 'Debe primero haber procesado los audios')
                return render(request, 'procesamiento/preproceso.html')
    else:
        return render(request, 'procesamiento/preproceso.html')


@csrf_exempt
def barra_progreso(request):
    progreso = Progreso.objects.first()
    data = {}

    if not progreso:
        data['progreso'] = "terminado"
        data['max'] = "terminado"
        return JsonResponse(data)

    archivos_completados = progreso.archivos_completados
    cantidad_archivos = progreso.cantidad_archivos
    data['progreso'] = archivos_completados
    data['max'] = cantidad_archivos

    # print("cat", archivos_completados, cantidad_archivos)
    if archivos_completados == cantidad_archivos:
        Progreso.objects.all().delete()

    return JsonResponse(data)
