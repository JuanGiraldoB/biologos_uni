from django.shortcuts import render
from ecosonos.utils.tkinter_utils import get_file
from ..plot_helper.plot import get_conectivity_map_url
from procesamiento.models import Progreso
from etiquetado_auto.models import GuardadoClusterResult, MetodologiaResult


def conectivity_map_view(request):
    Progreso.objects.all().delete()
    GuardadoClusterResult.objects.all().delete()
    MetodologiaResult.objects.all().delete()
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    try:
        # Get the CSV file path
        xlsx_path = get_file()
    except Exception as e:
        print(e)
        return render(request, 'conectividad/conectividad.html', data)

    # Check if there was a selected file and contains a ".csv" extension
    if not xlsx_path or ".xlsx" not in xlsx_path:
        return render(request, 'conectividad/conectividad.html', data)

    sheet_name = request.POST.get("hoja_excel")
    latitud_field_name = request.POST.get("latitud")
    longitud_field_name = request.POST.get("longitud")

    data['fig_url'] = get_conectivity_map_url(xlsx_path, sheet_name,
                                              latitud_field_name, longitud_field_name)

    # Return the prepared data with the template for rendering
    return render(request, 'conectividad/conectividad.html', data)
