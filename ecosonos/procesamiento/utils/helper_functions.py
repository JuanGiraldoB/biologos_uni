from django.shortcuts import render
from asgiref.sync import sync_to_async
from django.http import JsonResponse
import asyncio

from procesamiento.models import Progreso

from .lluvia_edison import run_algoritmo_lluvia_edison
from .plot import generate_and_get_plot_url_from_csv

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
    get_statistics_state_session,
    save_selected_subfolders_session,
    get_selected_subfolders_session
)

from ecosonos.utils.carpeta_utils import (
    get_folders_with_wav,
    get_folders_details,
    get_subfolders_basename
)

from ecosonos.utils.archivos_utils import (
    move_files_depending_type,
)


def load_folder(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Delete all records in the Progreso model
    Progreso.objects.all().delete()

    try:
        # Get the root folder where the wav files are located
        root_folder = get_root_folder()
    except Exception as e:
        print("Error en cargar carpeta load_folder ", e)
        # return JsonResponse({'error': 'Must select a folder'}, status=500)
        return render(request, 'procesamiento/preproceso.html')

    # If no subfolders are selected, return to the template
    if not root_folder:
        # return JsonResponse({'error': 'Must select a folder'}, status=500)
        return render(request, 'procesamiento/preproceso.html')

    # Save the root folder path to the session
    save_root_folder_session(request, root_folder)

    # Check if statistics option is selected in the POST request
    statistics_checked = request.POST.get('estadisticas')
    statistics_checked = True if statistics_checked else False

    # Get lists of folder paths and their basenames
    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    if statistics_checked:
        # If statistics option is selected, get details of folders
        folders_details = get_folders_details(folders_wav_path)
        data['statistics'] = True
        data['folders_details'] = folders_details
    else:
        # If statistics option is not selected, provide basic folder details
        data['statistics'] = False
        folders_details = []
        for path, basename in zip(folders_wav_path, folders_wav_basename):
            folder_detail = {
                'folder_path': path,
                'folder_name': basename,
            }
            folders_details.append(folder_detail)

        data['folders_details'] = folders_details

    # Save the statistics state and subfolder details to the session
    save_statistics_state_session(request, statistics_checked)
    save_subfolders_details_session(request, folders_details)

    # return JsonResponse(data)
    # Return the prepared data with the template for rendering
    return render(request, 'procesamiento/preproceso.html', data)


async def prepare_destination_folder(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get the list of selected subfolders from the POST request
    selected_subdfolders = request.POST.getlist('carpetas')

    # Get the base names of the selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)
    data['carpetas_procesando'] = selected_subdfolders_base_name

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        # return JsonResponse({'error': 'Must select a folder'}, status=500)
        return render(request, 'procesamiento/preproceso.html')

    # Save the selected subfolders in the session
    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders)

    try:
        # Get the destination folder where the processed output csv file will be saved
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en cargar carpeta destination_folder", e)
        # return JsonResponse({'error': 'Must select a folder'}, status=500)
        return render(request, 'procesamiento/preproceso.html')

    # If no destination folder is selected, render an error page or return an error response
    if not destination_folder:
        # return JsonResponse({'error': 'Must select a folder'}, status=500)
        return render(request, 'procesamiento/preproceso.html')

    # Save the destination folder path in the session
    await sync_to_async(save_destination_folder_session)(request, destination_folder)

    # Get folder details, statistics state, and selected subfolders from the session
    folder_details = await sync_to_async(get_subfolders_details_session)(request)
    statistics = await sync_to_async(get_statistics_state_session)(request)
    data['folders_details'] = folder_details
    data['statistics'] = statistics
    data['seleccionadas'] = 'seleccionadas'

    # Return the prepared data with the template for rendering
    # return JsonResponse(data)
    return render(request, 'procesamiento/preproceso.html', data)


async def process_folders(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get the list of selected subfolders from the session
    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request)

    # Create a progress object to track the processing progress
    progress = await sync_to_async(Progreso.objects.create)()

    # Get the root and destination folder paths from the session
    root_folder = await sync_to_async(get_root_folder_session)(request)
    destination_folder = await sync_to_async(get_destination_folder_session)(request)

    # Start the processing task in the background
    asyncio.create_task(run_algoritmo_lluvia_edison(
        selected_subdfolders, root_folder, destination_folder, progress))

    # Get the base names of the selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    # Get the statistics state from the session
    statistics = await sync_to_async(get_statistics_state_session)(request)

    data['statistics'] = statistics
    data['carpetas_procesando'] = selected_subdfolders_base_name
    data['mostrar_barra_proceso'] = True
    data['button_disable'] = 'disabled'

    # Return the prepared data with the template for rendering
    # return JsonResponse(data)
    return render(request, 'procesamiento/preproceso.html', data)


async def move_files(request):
    try:
        # Attempt to retrieve the destination folder path from the session
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        # If there's an error, return a JSON response indicating that a folder must be selected
        print("Error en cargar carpeta load_folder ", e)
        return JsonResponse({'error': 'Must select a folder'}, status=500)
        # return render(request, 'procesamiento/preproceso.html')

    # Check if a destination folder was selected
    if not destination_folder:
        return JsonResponse({'error': 'Must select a folder'}, status=500)
        # return render(request, 'procesamiento/preproceso.html')

    # Get the button type that determines which files to move
    button_type = request.POST['mover_archivos']

    # Determine the type of files to move based on the button type
    type_of_files_to_move = "YES" if "Lluvia" in button_type else "ALTO PSD"

    try:
        # Attempt to retrieve the CSV folder path from the session
        csv_folder = await sync_to_async(get_destination_folder_session)(request)

        # Move files depending on their type
        move_files_depending_type(
            csv_folder, destination_folder, type_of_files_to_move)
    except Exception as e:
        # If there's an error, return a JSON response indicating that a folder must be selected
        print(e)
        return JsonResponse({'error': 'Must select a folder'}, status=500)
        # return render(request, 'procesamiento/preproceso.html')

    return render(request, 'procesamiento/preproceso.html')


async def show_plot(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    try:
        # Attempt to retrieve the CSV folder path from the session
        csv_folder = await sync_to_async(get_destination_folder_session)(request)

        # Generate a URL for the plot based on the CSV data
        fig_url = generate_and_get_plot_url_from_csv(csv_folder)

        # Store the generated plot URL in the data dictionary
        data['fig_url'] = fig_url
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Must select a folder'}, status=500)

    return JsonResponse(data)
