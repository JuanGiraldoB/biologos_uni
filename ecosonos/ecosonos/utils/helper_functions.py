from datetime import datetime
from django.http import JsonResponse
from procesamiento.models import Progreso


def get_advance_percentage():
    data = {}
    progreso = Progreso.objects.first()

    archivos_completados = progreso.archivos_completados
    cantidad_archivos = progreso.cantidad_archivos

    try:
        porcentaje_completado = round(
            (archivos_completados / cantidad_archivos) * 100, 2)
    except:
        porcentaje_completado = 0

    data['procentaje_completado'] = porcentaje_completado

    return JsonResponse(data)


def check_csv_state():
    data = {}
    progreso = Progreso.objects.first()
    data['csv_cargado'] = progreso.csv_cargado
    print(progreso.csv_cargado)
    return JsonResponse(data)


def get_current_datetime_with_minutes():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%y-%H-%M")

    return formatted_datetime
