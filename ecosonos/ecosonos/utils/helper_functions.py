from django.http import JsonResponse
from procesamiento.models import Progreso


def get_advance_percentage():
    data = {}
    progreso = Progreso.objects.first()

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
