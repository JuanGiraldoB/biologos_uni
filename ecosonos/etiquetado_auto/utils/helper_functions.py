from django.shortcuts import render
from ..models import TableData
import pathlib
import os

from .Bioacustica_Completo import (
    run_metodologia
)

# from .. import prepare_xlsx_table_name
from .utils import prepare_xlsx_table_name

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    get_root_folder_session,
    save_csv_path_session,
    get_csv_path_session,
    save_destination_folder_session,
    get_destination_folder_session
)

from ecosonos.utils.carpeta_utils import (
    get_subfolders_basename,
    get_folders_with_wav,
    get_all_files_in_all_folders
)

from procesamiento.models import Progreso
import pandas as pd
from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import show_tkinter_windown_top
import asyncio
from asgiref.sync import sync_to_async


async def load_folder(request):
    data = {}
    try:
        root = show_tkinter_windown_top()
        root_folder = askdirectory(title='Seleccionar carpeta raiz')
        root.destroy()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(TableData.objects.all().delete)()

    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado-auto')

    await sync_to_async(Progreso.objects.all().delete)()

    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    data['carpetas_nombre_completo'] = folders_wav_path
    data['carpetas_nombre_base'] = folders_wav_basename
    data['completo_base_zip'] = zip(
        folders_wav_path, folders_wav_basename)

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def prepare_destination_folder(request):
    try:
        root = show_tkinter_windown_top()
        destination_folder = askdirectory(title='Seleccionar carpeta destino')
        destination_folder = str(pathlib.Path(destination_folder))
        root.destroy()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado-auto")

    return render(request, "etiquetado_auto/etiquetado-auto.html")


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

    await sync_to_async(save_selected_subfolders_session)(request, selected_folders,  app='etiquetado-auto')
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='etiquetado-auto')

    # all_files = []
    # all_files_basename = []
    # for folder in selected_folders:
    #     files, files_basename = get_files_in_folder(folder)
    #     all_files.extend(files)
    #     all_files_basename.extend(files_basename)

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
        request, app='etiquetado-auto')

    df = pd.read_excel(csv_xlsx)
    data['df'] = df

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)
