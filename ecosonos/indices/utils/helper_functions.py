from django.shortcuts import render
import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilename
from asgiref.sync import sync_to_async
import asyncio
import pathlib

from .session_utils import save_indices_session, get_indices_session

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    get_root_folder_session,
    save_destination_folder_session,
    get_destination_folder_session
)

from ecosonos.utils.tkinter_utils import show_tkinter_windown_top
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
        root = show_tkinter_windown_top()
        root_folder = askdirectory(title='Seleccionar carpeta raiz')
        root_folder = str(pathlib.Path(root_folder))
        root.destroy()
    except Exception as e:
        print("Error en cargar carpeta en indices", e)
        return render(request, 'indices/indices.html')

    if not root_folder:
        return render(request, 'indices/indices.html')

    selected_indices = request.POST.getlist('options')

    if not selected_indices:
        return render(request, 'indices/indices.html')

    await sync_to_async(save_root_folder_session)(request, root_folder, app='indices')
    await sync_to_async(save_indices_session)(request, selected_indices)
    await sync_to_async(Progreso.objects.all().delete)()

    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    data['folders'] = zip(folders_wav_path, folders_wav_basename)
    data['indices'] = selected_indices

    return render(request, 'indices/indices.html', data)


async def prepare_destination_folder(request):
    try:
        root = show_tkinter_windown_top()
        destination_folder = askdirectory(title='Seleccionar carpeta destino')
        destination_folder = str(pathlib.Path(destination_folder))
        root.destroy()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, 'indices/indices.html')

    if not destination_folder:
        return render(request, 'indices/indices.html')

    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="indices")

    return render(request, 'indices/indices.html')


async def process_folders(request):
    data = {}
    selected_folders = request.POST.getlist('carpetas')

    if not selected_folders:
        return render(request, 'indices/indices.html', data)

    await sync_to_async(save_selected_subfolders_session)(request, selected_folders,  app='indices')
    root_folder = await sync_to_async(get_root_folder_session)(request, app='indices')
    selected_indices = await sync_to_async(get_indices_session)(request)
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='indices')

    all_files, _ = get_all_files_in_all_folders(selected_folders)

    progress = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(all_files))

    asyncio.create_task(run_calcular_indice(
        selected_indices, root_folder, all_files, destination_folder, progress))

    selected_folders_basenames = get_subfolders_basename(
        selected_folders)

    data['carpetas_procesando'] = selected_folders_basenames
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
        root = show_tkinter_windown_top()
        file = askopenfilename(
            title='Seleccionar archivo csv')
        root.destroy()
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
