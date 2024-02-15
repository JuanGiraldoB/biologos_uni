from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from ecosonos.utils.helper_functions import (
    get_advance_percentage,
    check_csv_state
)

from .utils.helper_functions import (
    spectrogram_plot,
    get_spectrogram_data,
    representative_element_plot,
    get_hourly_sonotype_plots_urls
)

from .utils.helper_functions_sonotipo import (
    load_main_folder_sonotipo,
    prepare_destination_folder_sonotipo,
    process_folders_sonotipo,
    stop_process_sonotipo
)

from .utils.helper_functions_reconocer import (
    load_main_folder_reconocer,
    prepare_destination_folder_reconocer,
    process_folders_reconocer,
    load_csv_reconocer,
    stop_process_reconocer
)

from .utils.helper_functions_temporal import (
    process_hourly_sonotype,
    stop_process_temporal
)


def etiquetado_auto_view(request):
    return render(request, "etiquetado_auto/etiquetado_auto.html")


async def sonotipo_view(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await load_main_folder_sonotipo(request)

        if 'destino' in request.POST:
            return await prepare_destination_folder_sonotipo(request)

        if 'procesar_carpetas' in request.POST:
            return await process_folders_sonotipo(request)

        if 'parar_proceso' in request.POST:
            return await stop_process_sonotipo(request)

    return render(request, "etiquetado_auto/etiquetado_auto_sonotipo_ajax.html")


async def reconocer_view(request):
    if request.method == 'POST':
        if 'cargar_csv' in request.POST:
            return await load_csv_reconocer(request)

        if 'cargar' in request.POST:
            return await load_main_folder_reconocer(request)

        if 'destino' in request.POST:
            return await prepare_destination_folder_reconocer(request)

        if 'procesar_carpetas' in request.POST:
            return await process_folders_reconocer(request)

        if 'parar_proceso' in request.POST:
            return await stop_process_reconocer(request)

    return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html")


async def temporal_view(request):
    if request.method == 'POST':
        if 'cargar_csv' in request.POST:
            return await process_hourly_sonotype(request)

        if 'parar_proceso' in request.POST:
            return await stop_process_temporal(request)

    return render(request, "etiquetado_auto/etiquetado_auto_temporal_ajax.html")


@csrf_exempt
def plots_view(request):
    if request.method == 'POST':
        if 'informacion' in request.POST:
            return get_spectrogram_data(request)
        if 'path' in request.POST:
            return spectrogram_plot(request)
        if 'representativo' in request.POST:
            print(request.POST)
            return representative_element_plot(request)
        if 'graficas' in request.POST:
            return get_hourly_sonotype_plots_urls()

    return redirect('etiquetado-auto')


@csrf_exempt
def barra_progreso(request):
    return get_advance_percentage()


@csrf_exempt
def csv_cargado(request):
    return check_csv_state()
