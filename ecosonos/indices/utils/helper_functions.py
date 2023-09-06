from django.shortcuts import render
import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilename
from asgiref.sync import sync_to_async
import asyncio

from .session_utils import (
    save_indices_session,
    get_indices_session,
)

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    get_root_folder_session,
    save_destination_folder_session,
    get_destination_folder_session,
    save_subfolders_details_session,
    get_subfolders_details_session,
    get_selected_subfolders_session,
)

from ecosonos.utils.tkinter_utils import get_root_folder, get_file
from procesamiento.models import Progreso
from .funciones_indices_progress import polar_plot
from .funciones_indices import run_calcular_indice

from ecosonos.utils.carpeta_utils import (
    get_folders_with_wav,
    get_subfolders_basename,
    get_all_files_in_all_folders
)


async def load_folder(request):
    data = {}

    try:
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en cargar carpeta en indices", e)
        return render(request, 'indices/indices.html')

    if not root_folder:
        return render(request, 'indices/indices.html')

    selected_indices = request.POST.getlist('options')

    if not selected_indices:
        return render(request, 'indices/indices.html')

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

    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='indices')
    await sync_to_async(save_root_folder_session)(request, root_folder, app='indices')
    await sync_to_async(save_indices_session)(request, selected_indices)

    data['folders_details'] = folders_details
    data['indices'] = selected_indices

    return render(request, 'indices/indices.html', data)


async def prepare_destination_folder(request):
    data = {}

    selected_subdfolders = request.POST.getlist('carpetas')

    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)
    data['carpetas_procesando'] = selected_subdfolders_base_name

    if not selected_subdfolders:
        return render(request, 'indices/indices.html')

    try:
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, 'indices/indices.html')

    if not destination_folder:
        return render(request, 'indices/indices.html')

    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="indices")
    # folder_details = await sync_to_async(get_subfolders_details_session)(request, app='indices')
    indices = await sync_to_async(get_indices_session)(request)

    folder_details = await sync_to_async(get_subfolders_details_session)(request, 'indices')

    data['folders_details'] = folder_details
    data['indices'] = indices
    data['seleccionadas'] = 'seleccionadas'
    return render(request, 'indices/indices.html', data)


async def process_folders(request):
    data = {}

    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request)

    # if not selected_subdfolders:
    #     return render(request, 'indices/indices.html', data)

    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders,  app='indices')
    root_folder = await sync_to_async(get_root_folder_session)(request, app='indices')
    selected_indices = await sync_to_async(get_indices_session)(request)
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='indices')

    all_files, _ = get_all_files_in_all_folders(selected_subdfolders)

    progress = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(all_files))

    asyncio.create_task(run_calcular_indice(
        selected_indices, root_folder, all_files, destination_folder, progress))

    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    data['carpetas_procesando'] = selected_subdfolders_base_name
    data['indices'] = selected_indices

    return render(request, 'indices/indices.html', data)


async def show_plot(request):
    try:
        destination_folder = await sync_to_async(get_destination_folder_session)(request, app='indices')
        selected_indices = await sync_to_async(get_indices_session)(request)

    except Exception as e:
        print(e, "sss")
        return render(request, 'indices/indices.html')

    try:
        graficas = []
        for indice in selected_indices:

            if "ADIm" == indice:
                continue

            graficas.append(await sync_to_async(polar_plot)(destination_folder, indice))

        if "ADIm" in selected_indices:
            adim = []

            for i in range(30):
                adim_i = f'ADIm_{i}'
                adim.append(adim_i)
                graficas.append(await sync_to_async(polar_plot)(destination_folder, indice, adim_i))

    # Exception occurs when there are less ADIm_{i} than in the for range
    except Exception as e:
        selected_indices.remove("ADIm")
        selected_indices.extend(adim)
        print(e)

    zipped = zip(graficas, selected_indices)
    context = {'graficas': graficas,
               'indices': selected_indices, 'zipped': zipped}

    return render(request, 'indices/indices.html', context)


async def load_csv(request):
    try:
        file = await sync_to_async(get_file)()
    except Exception as e:
        print("Error cargar csv", e)
        return render(request, 'indices/indices.html')

    if not file:
        return render(request, 'indices/indices.html')

    df = pd.read_csv(file)
    indices = df.columns[1:-1].to_list()

    graficas = []
    for indice in indices:
        graficas.append(await sync_to_async(polar_plot)(file, indice))

    zipped = zip(graficas, indices)
    context = {'graficas': graficas,
               'indices': indices, 'zipped': zipped}

    return render(request, 'indices/indices.html', context)
