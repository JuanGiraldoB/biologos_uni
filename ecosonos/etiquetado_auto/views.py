from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ecosonos.utils.helper_functions import (
    get_percentage_advance
)

from .utils.helper_functions import (
    load_folder,
    process_folders,
    show_table,
    prepare_destination_folder
)

from ecosonos.utils.session_utils import (
    get_files_session
)


async def etiquetado_auto(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await load_folder(request)

        elif 'destino' in request.POST:
            return await prepare_destination_folder(request)

        elif 'procesar_carpetas' in request.POST:
            return await process_folders(request)

        elif 'mostrar-tabla' in request.POST:
            return await show_table(request)

    return render(request, "etiquetado_auto/etiquetado-auto.html")


@csrf_exempt
def files_list_view(request):
    if request.method == 'POST':
        data = {}
        files_details = get_files_session(request, app='etiquetado_auto')
        data['files_details'] = files_details

        return JsonResponse(data)
    return render(request, "etiquetado_auto/etiquetado-auto.html")


@csrf_exempt
def barra_progreso(request):
    return get_percentage_advance()
