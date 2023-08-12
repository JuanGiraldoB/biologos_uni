from django.shortcuts import render
from asgiref.sync import sync_to_async
import pathlib
from tkinter.filedialog import askdirectory
import asyncio

from procesamiento.models import Progreso

from .lluvia_edison import run_algoritmo_lluvia_edison
from .plot import get_plot

from ecosonos.utils.tkinter_utils import (
    show_tkinter_windown_top
)

from ecosonos.utils.session_utils import (
    save_root_folder_session,
    get_root_folder_session,
    save_subfolders_details_session,
    save_statistics_state_session,
    save_destination_folder_session,
    get_destination_folder_session
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
        root = show_tkinter_windown_top()
        root_folder = askdirectory(title='Seleccionar carpeta raiz')
        root_folder = str(pathlib.Path(root_folder))
        root.destroy()
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
        folder_details = get_folders_details(folders_wav_path)
        await sync_to_async(save_subfolders_details_session)(request, folder_details)
        data['statistics'] = True
        data['folders_details'] = folder_details
    else:
        data['statistics'] = False
        data['folders'] = zip(folders_wav_path, folders_wav_basename)

    return render(request, 'procesamiento/preproceso.html', data)


async def prepare_destination_folder(request):
    try:
        root = show_tkinter_windown_top()
        destination_folder = askdirectory(title='Seleccionar carpeta destino')
        destination_folder = str(pathlib.Path(destination_folder))
        root.destroy()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, 'procesamiento/preproceso.html')

    if not destination_folder:
        return render(request, 'procesamiento/preproceso.html')

    await sync_to_async(save_destination_folder_session)(request, destination_folder)

    return render(request, 'procesamiento/preproceso.html')


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

    data['carpetas_procesando'] = selected_subdfolders_base_name

    return render(request, 'procesamiento/preproceso.html', data)


async def move_files(request):
    try:
        root = show_tkinter_windown_top()
        destination_folder = askdirectory(
            title='Carpeta de destino de audios con lluvia')
        destination_folder = str(pathlib.Path(destination_folder))
        root.destroy()

    except Exception as e:
        print(e)
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
