from django.shortcuts import render
from django.http import JsonResponse
import os

from ecosonos.utils.helper_functions import get_current_datetime_with_minutes

from ..models import MetodologiaResult

from .Bioacustica_Completo import (
    run_metodologia,
    stop_process_metodologia
)

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    save_csv_path_session,
    save_destination_folder_session,
    get_destination_folder_session,
    save_subfolders_details_session,
    save_files_session,
    get_selected_subfolders_session,
)

from ecosonos.utils.carpeta_utils import (
    get_subfolders_basename,
    get_folders_with_wav,
    get_all_files_in_all_folders
)

from procesamiento.models import Progreso
from ecosonos.utils.tkinter_utils import get_root_folder
import asyncio
from asgiref.sync import sync_to_async


async def load_main_folder_sonotipo(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Delete all records in the Progreso model
    await sync_to_async(Progreso.objects.all().delete)()
    # Delete MetodologiaResult records
    await sync_to_async(MetodologiaResult.objects.all().delete)()

    try:
        # Get the root folder where the wav files are located
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # If no root folder is selected, render an error page or return an error response
    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Get lists of folder paths and their basenames that contain WAV files
    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folder_path': path,
            'folder_name': basename,
        }
        folders_details.append(folder_detail)

    # Save root folder path and folder details to the session
    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado_auto')
    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='etiquetado_auto')

    data['folders_details'] = folders_details
    print(data)

    # Save the statistics state and subfolder details to the session
    return JsonResponse(data)
    # return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def prepare_destination_folder_sonotipo(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get the list of selected subfolders from the POST request
    selected_subdfolders = request.POST.getlist('carpetas')

    # Get the base names of selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    try:
        # Get the destination folder where the processed output csv file will be saved
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    # If no destination folder is selected, return to the template
    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    # Save the destination folder and selected subfolders paths to the session
    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado_auto")
    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders,  app='etiquetado_auto')

    data['folders'] = selected_subdfolders_base_name
    data['destination_folder'] = destination_folder.split('/')[-1]

    # Delete only if the request was sent from sonotipo (check the div visibility)
    # if data['div_reconocer'] == 'block':
    #     selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)
    #     data['selected_cluster_names'] = selected_cluster_names

    # Return the prepared data with the template for rendering
    return JsonResponse(data)
    # return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def process_folders_sonotipo(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get selected subfolders from the session
    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request, app='etiquetado_auto')

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Get frequency range from POST request
    minimum_frequency = request.POST.get('frecuenciaminima')
    maximum_frequency = request.POST.get('frecuenciamaxima')

    # Check and set minimum and maximum frequency values
    if minimum_frequency:
        minimum_frequency = int(minimum_frequency)
    else:
        minimum_frequency = 'min'

    if maximum_frequency:
        maximum_frequency = int(maximum_frequency)
    else:
        maximum_frequency = 'max'

    # Get the destination folder from the session
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='etiquetado_auto')

    # Get all file paths and basenames from the selected subfolders
    files_paths, files_basenames = get_all_files_in_all_folders(
        selected_subdfolders)

    # Prepare file details for rendering in the template
    files_details = []
    for path, basename in zip(files_paths, files_basenames):
        file_details = {
            'path': path,
            'basename': basename
        }

        files_details.append(file_details)

    # Save file details to the session
    save_files_session(request, files_details, app='etiquetado_auto')

    # Calculate the 1% of total files
    one_percent = int(0.01 * len(files_paths))

    # Create a progress object to track the processing progress with the amount of files from the selected folders
    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(files_paths) + one_percent, uno_porciento=one_percent)

    # Get selected subfolders basenames
    selected_folders_basenames = get_subfolders_basename(
        selected_subdfolders)

    # Set parameters for processing
    canal = 1
    autosel = 0
    visualize = 0
    banda = [minimum_frequency, maximum_frequency]

    # Name of csv file where the output will be saved
    date_time = get_current_datetime_with_minutes()
    csv_name = f'tabla-nuevas-especies-{date_time}.csv'
    csv_path = os.path.join(destination_folder, csv_name)
    await sync_to_async(save_csv_path_session)(request, csv_path, app="etiquetado_auto")

    # Create a MetodologiaResult object for storing results
    metodologia_output = await sync_to_async(MetodologiaResult.objects.create)()

    data['carpetas_procesando'] = selected_folders_basenames

    try:
        asyncio.create_task(run_metodologia(
            files_paths, files_basenames, banda, canal, autosel, visualize, progreso, csv_path, metodologia_output))
    except Exception as e:
        print('error: ***********', e)

    # Return the prepared data with the template for rendering
    return JsonResponse(data)
    # return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def stop_process_sonotipo(request):
    data = {}
    stop_process_metodologia()

    return JsonResponse(data)
