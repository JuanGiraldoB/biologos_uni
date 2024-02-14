from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from ecosonos.utils.helper_functions import (
    get_advance_percentage
)

from .utils.helper_functions import (
    load_folder,
    prepare_destination_folder,
    process_folders,
    move_files,
    show_plot,
    stop_process
)


async def lluvia(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await load_folder(request)

        if 'destino' in request.POST:
            return await prepare_destination_folder(request)

        if 'procesar_carpetas' in request.POST:
            return await process_folders(request)

        if 'parar_proceso' in request.POST:
            return await stop_process(request)

        if 'mover_archivos' in request.POST:
            return await move_files(request)

        if 'mostrar_grafica' in request.POST:
            return await show_plot(request)

    else:
        return render(request, 'procesamiento/preproceso_ajax.html')


@csrf_exempt
def progress_bar(request):
    return get_advance_percentage()
