from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .utils.helper_functions import (
    load_folder,
    prepare_destination_folder,
    process_folders,
    show_plot,
    load_csv,
    stop_process
)

from ecosonos.utils.helper_functions import (
    get_advance_percentage,
    check_csv_state
)


async def indices_vista(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await load_folder(request)

        if 'destino' in request.POST:
            return await prepare_destination_folder(request)

        if 'procesar_carpetas' in request.POST:
            return await process_folders(request)

        if 'parar_proceso' in request.POST:
            return await stop_process(request)

        if 'mostrar-grafica' in request.POST:
            return await show_plot(request)

        if 'cargar-csv' in request.POST:
            return await load_csv(request)

    else:
        return render(request, 'indices/indices_ajax.html')


@csrf_exempt
def barra_progreso_vista(request):
    return get_advance_percentage()


@csrf_exempt
def csv_cargado(request):
    return check_csv_state()
