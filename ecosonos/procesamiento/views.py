from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import asyncio
from asgiref.sync import sync_to_async

import tkinter as tk
from tkinter.filedialog import askdirectory

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

from ecosonos.utils.tkinter_utils import mostrar_ventana_encima


async def lluvia(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            if not carpeta_raiz:
                messages.error(request, 'Debe seleccionar la carpeta raiz')
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

            progreso = await sync_to_async(Progreso.objects.create)()
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request)

            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)
            data['carpetas_nombre_completo'] = carpetas_nombre_completo
            data['carpetas_nombre_base'] = carpetas_nombre_base
            data['completo_base_zip'] = zip(
                carpetas_nombre_completo, carpetas_nombre_base)

            asyncio.create_task(run_algoritmo_lluvia_edison(
                carpetas_seleccionadas, carpeta_raiz, progreso))

            return render(request, 'procesamiento/preproceso.html', data)

        elif 'mover_archivos' in request.POST:
            try:
                root = mostrar_ventana_encima()
                carpeta_destino = askdirectory(
                    title='Carpeta de destino de audios con lluvia')
                root.destroy()

                if not carpeta_destino:
                    messages.error(request, 'Canceló la selección de carpeta')
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
