from datetime import datetime
from django.http import JsonResponse
from procesamiento.models import Progreso


def get_advance_percentage():
    data = {}
    progreso = Progreso.objects.first()

    if not progreso:
        return JsonResponse(data)

    archivos_completados = progreso.archivos_completados
    cantidad_archivos = progreso.cantidad_archivos

    try:
        porcentaje_completado = round(
            (archivos_completados / cantidad_archivos) * 100, 2)
    except:
        porcentaje_completado = 0

    data['procentaje_completado'] = porcentaje_completado

    if archivos_completados == cantidad_archivos:
        Progreso.objects.all().delete()

    return JsonResponse(data)


def get_current_datetime_with_minutes():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%y-%H-%M")

    return formatted_datetime
