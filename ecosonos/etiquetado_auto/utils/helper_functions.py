from django.shortcuts import render
from ..models import TableData
import pathlib

from .Bioacustica_Completo import (
    run_metodologia
)

from .utils import prepare_xlsx_table_name

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    get_root_folder_session,
    save_csv_path_session,
    get_csv_path_session,
    save_destination_folder_session,
    get_destination_folder_session,
    save_subfolders_details_session,
    get_subfolders_details_session
)

from ecosonos.utils.carpeta_utils import (
    get_subfolders_basename,
    get_folders_with_wav,
    get_all_files_in_all_folders
)

from procesamiento.models import Progreso
import pandas as pd
from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import get_root_folder
import asyncio
from asgiref.sync import sync_to_async


async def load_folder(request):
    try:
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(TableData.objects.all().delete)()

    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado_auto')

    await sync_to_async(Progreso.objects.all().delete)()

    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folders_path': path,
            'folders_basename': basename,
        }
        folders_details.append(folder_detail)

    import pprint
    pprint.pprint(folders_details)

    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='etiquetado_auto')

    return render(request, "etiquetado_auto/etiquetado-auto.html")


async def prepare_destination_folder(request):
    data = {}

    try:
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado_auto")
    folders_details = await sync_to_async(get_subfolders_details_session)(request, app='etiquetado_auto')

    import pprint
    pprint.pprint(folders_details)

    data['folders_details'] = folders_details

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def process_folders(request):
    data = {}
    selected_folders = request.POST.getlist('carpetas')
    minimum_frequency = request.POST.get('frecuenciaminima')
    maximum_frequency = request.POST.get('frecuenciamaxima')

    if minimum_frequency:
        minimum_frequency = int(minimum_frequency)
    else:
        minimum_frequency = 'min'

    if maximum_frequency:
        maximum_frequency = int(maximum_frequency)
    else:
        maximum_frequency = 'max'

    if not selected_folders:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    await sync_to_async(save_selected_subfolders_session)(request, selected_folders,  app='etiquetado_auto')
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='etiquetado_auto')

    all_files, all_files_basename = get_all_files_in_all_folders(
        selected_folders)

    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(all_files))
    selected_folders_basenames = get_subfolders_basename(
        selected_folders)

    canal = 1
    autosel = 0
    visualize = 0
    banda = [minimum_frequency, maximum_frequency]

    xlsx_name = prepare_xlsx_table_name(
        selected_folders_basenames, destination_folder)
    await sync_to_async(save_csv_path_session)(
        request, xlsx_name)

    asyncio.create_task(run_metodologia(
        all_files, all_files_basename, banda, canal, autosel, visualize, progreso, xlsx_name))

    data['carpetas_procesando'] = selected_folders_basenames
    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def show_table(request):
    data = {}
    csv_xlsx = await sync_to_async(get_csv_path_session)(
        request)

    df = pd.read_excel(csv_xlsx)
    data['df'] = df

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)
