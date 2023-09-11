from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from ecosonos.utils.helper_functions import (
    get_advance_percentage
)

from .utils.helper_functions import (
    load_folder,
    process_folders,
    spectrogram_plot,
    prepare_destination_folder,
    get_spectrogram_data,
    representative_element_plot,
    load_csv
)


async def sonotipo_view(request):
    if request.method == 'POST':
        print(request.POST)
        if 'cargar' in request.POST:
            return await load_folder(request)

        elif 'destino' in request.POST:
            return await prepare_destination_folder(request)

        elif 'procesar_carpetas' in request.POST:
            return await process_folders(request)

    return render(request, "etiquetado_auto/etiquetado-auto.html")


async def reconocer_view(request):
    if request.method == 'POST':
        print(request.POST)
        if 'cargar_csv' in request.POST:
            return await load_csv(request)

        elif 'cargar' in request.POST:
            return await load_folder(request)

        elif 'destino' in request.POST:
            return await prepare_destination_folder(request)

        elif 'procesar_carpetas' in request.POST:
            return await process_folders(request)

    return render(request, "etiquetado_auto/etiquetado-auto.html")


@csrf_exempt
def spectrogram_view(request):
    if request.method == 'POST':
        print(request.POST)
        if 'informacion' in request.POST:
            return get_spectrogram_data(request)
        elif 'path' in request.POST:
            return spectrogram_plot(request)
        elif 'representativo' in request.POST:
            return representative_element_plot(request)

    return redirect('etiquetado-auto')


@csrf_exempt
def barra_progreso(request):
    return get_advance_percentage()
