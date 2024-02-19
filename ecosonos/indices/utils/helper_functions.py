from django.shortcuts import render
import pandas as pd
from asgiref.sync import sync_to_async
import asyncio
import os
from django.http import JsonResponse

from ecosonos.utils.helper_functions import get_current_datetime_with_minutes

from .utils import (
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
    get_selected_subfolders_session,
    save_csv_path_session,
    get_csv_path_session
)

from procesamiento.models import Progreso
from indices.models import Indices
from ecosonos.utils.tkinter_utils import get_root_folder, get_file
from .funciones_indices_progress import generate_polar_plot
from .funciones_indices import run_calcular_indice, stop_process_indices

from ecosonos.utils.carpeta_utils import (
    get_folders_with_wav,
    get_subfolders_basename,
    get_all_files_in_all_folders
)

global background_task


async def load_folder(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Delete all records in the Progreso model
    await sync_to_async(Progreso.objects.all().delete)()
    await sync_to_async(Indices.objects.all().delete)()

    try:
        # Get the root folder where the wav files are located
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en cargar carpeta en indices", e)
        return render(request, 'indices/indices.html')

    # If no root folder is selected, render an error page or return an error response
    if not root_folder:
        return render(request, 'indices/indices.html')

    # Get the selected indices from the POST request
    selected_indices = request.POST.getlist('options')
    print(selected_indices)

    # If no indices are selected, render an error page or return an error response
    if not selected_indices:
        return render(request, 'indices/indices.html')

    # Get the paths and basenames of folders containing WAV files
    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folder_path': path,
            'folder_name': basename,
        }
        folders_details.append(folder_detail)

    # Save the root folder, subfolder details, and selected indices in session
    await sync_to_async(save_root_folder_session)(request, root_folder, app='indices')
    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='indices')
    await sync_to_async(save_indices_session)(request, selected_indices)

    data['folders_details'] = folders_details
    data['indices'] = selected_indices
    data['button_display_csv'] = 'none'

    return JsonResponse(data)
    # Return the prepared data with the template for rendering
    # return render(request, 'indices/indices.html', data)


async def prepare_destination_folder(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get the list of selected subfolders from the POST request
    selected_subdfolders = request.POST.getlist('carpetas')

    # Get the base names of selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    # If no subfolders are selected, render an error page or return an error response
    if not selected_subdfolders:
        return render(request, 'indices/indices.html')

    try:
        # Get the destination folder where the processed output csv file will be saved
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, 'indices/indices.html')

    # If no destination folder is selected, render an error page or return an error response
    if not destination_folder:
        return render(request, 'indices/indices.html')

    # Save the destination folder and selected subfolders in session
    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="indices")
    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders, app="indices")

    # Get subfolder details and selected indices from session
    indices = await sync_to_async(get_indices_session)(request)

    data['folders'] = selected_subdfolders_base_name
    data['indices'] = indices
    data['destination_folder'] = destination_folder.split('/')[-1]

    return JsonResponse(data)
    # return render(request, 'indices/indices.html', data)


async def process_folders(request):
    # Create an empty dictionary to store data that will be sent to the template
    global background_task, cancel_flag
    data = {}

    # Get the list of selected subfolders from the session
    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request, app='indices')

    # await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders,  app='indices')
    root_folder = await sync_to_async(get_root_folder_session)(request, app='indices')
    selected_indices = await sync_to_async(get_indices_session)(request)
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='indices')

    # Get all files in selected subfolders
    all_files, _ = get_all_files_in_all_folders(selected_subdfolders)

    # Base name of root folder
    base_name_root_folder = os.path.basename(root_folder)

    # Name of csv file where the output will be saved
    date_time = get_current_datetime_with_minutes()
    csv_name = f'indices-acusticos-{base_name_root_folder}-{date_time}.csv'
    csv_path = os.path.join(destination_folder, csv_name)
    await sync_to_async(save_csv_path_session)(request, csv_path, app="indices")

    # Create a progress object in the database with the amount of files that are inside the folders
    progress = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(all_files))

    # Create indices object
    valores = list()
    for i in range(len(selected_indices)+1):
        valores.append(list())

    await sync_to_async(Indices.objects.create)(
        indices_seleccionados=selected_indices,
        csv_path=csv_path,
        valores=valores,
        grabaciones=all_files
    )

    # Start the processing task in the background
    # background_task = asyncio.create_task(run_calcular_indice(
    #     selected_indices, all_files, csv_path, progress))

    workers = request.POST.get("workers")
    print("workers:", workers)

    background_task = asyncio.create_task(run_calcular_indice(
        selected_indices, all_files, csv_path, workers))

    # Get base names of selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    data['carpetas_procesando'] = selected_subdfolders_base_name
    data['indices'] = selected_indices
    data['mostrar_barra_proceso'] = True
    data['button_disable'] = 'disabled'
    data['button_display_csv'] = 'none'
    data['button_disable_process'] = 'none'
    data['carpeta_principal_seleccionada'] = root_folder.split('/')[-1]
    data['carpeta_destino_seleccionada'] = destination_folder.split('/')[-1]

    # Return the prepared data with the template for rendering
    return JsonResponse(data)
    # return render(request, 'indices/indices.html', data)


async def stop_process(request):
    data = {}
    stop_process_indices()

    return JsonResponse(data)


async def show_plot(request):
    data = {}

    try:
        # Get the destination folder and selected indices from session
        # destination_folder = await sync_to_async(get_destination_folder_session)(request, app='indices')
        selected_indices = await sync_to_async(get_indices_session)(request)
        csv_path = await sync_to_async(get_csv_path_session)(request, app="indices")

    except Exception as e:
        print(e)
        return render(request, 'indices/indices.html')

    try:
        # Iterate over selected indices to generate polar plots
        graficas = []
        for indice in selected_indices:

            if "ADIm" == indice:
                continue

            graficas.append(await sync_to_async(generate_polar_plot)(csv_path, indice))

        # If ADIM in selected indices, generate polar plots for "ADIm_i" indices
        if "ADIm" in selected_indices:
            adim = []

            for i in range(1_000_000):
                adim_i = f'ADIm_{i}'
                adim.append(adim_i)
                graficas.append(await sync_to_async(generate_polar_plot)(csv_path, indice, adim_i))

    # Exception occurs when there are less ADIm_{i} than in the for range
    except Exception as e:
        selected_indices.remove("ADIm")
        selected_indices.extend(adim)
        print(e)

    # Create a zipped iterable to pair plots with their corresponding indices
    # zipped = zip(graficas, selected_indices)
    data['plots_urls'] = graficas
    data['indices'] = selected_indices
    # data['zipped'] = zipped

    # data = {'graficas': graficas,
    #         'indices': selected_indices, 'zipped': zipped}

    # Return the prepared data with the template for rendering
    return JsonResponse(data)
    # return render(request, 'indices/indices.html', data)


async def load_csv(request):
    data = {}

    try:
        # Get the uploaded CSV file
        file = await sync_to_async(get_file)()
    except Exception as e:
        print("Error cargar csv", e)
        return render(request, 'indices/indices.html')

    if not file:
        return render(request, 'indices/indices.html')

    # Read the CSV file into a DataFrame and extract indices
    df = pd.read_csv(file)
    indices = df.columns[1:-1].to_list()

    # Generate polar plots for each index in the CSV
    graficas = []
    for indice in indices:
        graficas.append(await sync_to_async(generate_polar_plot)(file, indice))

    # Create a zipped iterable to pair plots with their corresponding indices
    # zipped = zip(graficas, indices)
    # context = {'graficas': graficas,
    #            'indices': indices, 'zipped': zipped}
    data['plots_urls'] = graficas
    data['indices'] = indices

    return JsonResponse(data)
    # Return the prepared data with the template for rendering
    # return render(request, 'indices/indices.html', data)
