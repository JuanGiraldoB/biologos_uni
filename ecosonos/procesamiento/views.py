from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from ecosonos.utils.helper_functions import (
    get_percentage_advance
)

from .utils.helper_functions import (
    load_folder,
    prepare_destination_folder,
    process_folders,
    move_files,
    show_plot
)


async def lluvia(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await load_folder(request)

        elif 'destino' in request.POST:
            return await prepare_destination_folder(request)

        elif 'procesar_carpetas' in request.POST:
            return await process_folders(request)

        elif 'mover_archivos' in request.POST:
            return await move_files(request)

        elif 'mostrar_grafica' in request.POST:
            print(request.POST)
            return await show_plot(request)

    else:
        return render(request, 'procesamiento/preproceso.html')


@csrf_exempt
def progress_bar(request):
    return get_percentage_advance()
