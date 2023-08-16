from django.shortcuts import render
from asgiref.sync import sync_to_async
import pathlib
from tkinter.filedialog import askdirectory
import asyncio

from procesamiento.models import Progreso

from .lluvia_edison import run_algoritmo_lluvia_edison
from .plot import get_plot

from ecosonos.utils.tkinter_utils import (
    get_root_folder
)

from ecosonos.utils.session_utils import (
    save_root_folder_session,
    get_root_folder_session,
    save_subfolders_details_session,
    save_destination_folder_session,
    get_destination_folder_session,
    get_subfolders_details_session,
    save_statistics_state_session,
    get_statistics_state_session
)

from ecosonos.utils.carpeta_utils import (
    subcarpetas_seleccionadas,
    get_folders_with_wav,
    get_folders_details,
    get_subfolders_basename
)

from ecosonos.utils.archivos_utils import (
    move_files_depending_type,
)


async def load_folder(request):
    data = {}

    await sync_to_async(Progreso.objects.all().delete)()

    try:
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en cargar carpeta", e)
        return render(request, 'procesamiento/preproceso.html')

    if not root_folder:
        return render(request, 'procesamiento/preproceso.html')

    await sync_to_async(save_root_folder_session)(request, root_folder)

    statistics_checked = request.POST.get('estadisticas')
    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    if statistics_checked:
        folders_details = get_folders_details(folders_wav_path)
        data['statistics'] = True
        await sync_to_async(save_statistics_state_session)(request, True)
        await sync_to_async(save_subfolders_details_session)(request, folders_details)
        print(type(folders_details))
    else:
        data['statistics'] = False

        folders_details = []
        for path, basename in zip(folders_wav_path, folders_wav_basename):
            folder_detail = {
                'folders_path': path,
                'folders_basename': basename,
            }
            folders_details.append(folder_detail)

        await sync_to_async(save_statistics_state_session)(request, False)
        await sync_to_async(save_subfolders_details_session)(request, folders_details)

    return render(request, 'procesamiento/preproceso.html', data)


async def prepare_destination_folder(request):
    data = {}

    try:
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en cargar carpeta", e)
        return render(request, 'procesamiento/preproceso.html')

    if not destination_folder:
        return render(request, 'procesamiento/preproceso.html')

    await sync_to_async(save_destination_folder_session)(request, destination_folder)

    folder_details = await sync_to_async(get_subfolders_details_session)(request)
    statistics = await sync_to_async(get_statistics_state_session)(request)
    data['folders_details'] = folder_details
    data['statistics'] = statistics
    data['destino'] = True

    return render(request, 'procesamiento/preproceso.html', data)


async def process_folders(request):
    data = {}

    selected_subdfolders = request.POST.getlist('carpetas')

    if subcarpetas_seleccionadas(selected_subdfolders):
        return render(request, 'procesamiento/preproceso.html')

    progress = await sync_to_async(Progreso.objects.create)()
    root_folder = await sync_to_async(get_root_folder_session)(request)
    destination_folder = await sync_to_async(get_destination_folder_session)(request)

    asyncio.create_task(run_algoritmo_lluvia_edison(
        selected_subdfolders, root_folder, destination_folder, progress))

    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    statistics = await sync_to_async(get_statistics_state_session)(request)

    data['statistics'] = statistics
    data['carpetas_procesando'] = selected_subdfolders_base_name

    return render(request, 'procesamiento/preproceso.html', data)


async def move_files(request):
    try:
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en cargar carpeta", e)
        return render(request, 'procesamiento/preproceso.html')

    if not destination_folder:
        return render(request, 'procesamiento/preproceso.html')

    button_type = request.POST['mover_archivos']
    type_of_files_to_move = "YES" if "Lluvia" in button_type else "ALTO PSD"

    try:
        csv_folder = await sync_to_async(get_destination_folder_session)(request)

        move_files_depending_type(
            csv_folder, destination_folder, type_of_files_to_move)
    except Exception as e:
        print(e)
        return render(request, 'procesamiento/preproceso.html')

    return render(request, 'procesamiento/preproceso.html')


async def show_plot(request):
    data = {}
    try:
        csv_folder = await sync_to_async(get_destination_folder_session)(request)
        plot = get_plot(csv_folder)
        data['plot'] = plot
    except Exception as e:
        print(e)
        return render(request, 'procesamiento/preproceso.html')

    return render(request, 'procesamiento/preproceso.html', data)
